"""C1-C2: Structured output — JSON, CSV, and Markdown digest. C3: Git auto-commit."""

from __future__ import annotations

import csv
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ..intelligence.analyzer import SegmentProposal


def _segment_dir(base_dir: str, run_date: str) -> Path:
    p = Path(base_dir) / run_date
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json(proposals: list[SegmentProposal], base_dir: str, run_date: str) -> Path:
    out_dir = _segment_dir(base_dir, run_date)
    path = out_dir / "proposals.json"
    payload = {
        "date": run_date,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(proposals),
        "segments": [p.to_dict() for p in proposals],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"[reporter] JSON  → {path}")
    return path


def write_csv(proposals: list[SegmentProposal], base_dir: str, run_date: str) -> Path:
    out_dir = _segment_dir(base_dir, run_date)
    path = out_dir / "proposals.csv"
    fields = [
        "name", "iab_tier1_id", "iab_tier1_name", "iab_tier2_id", "iab_tier2_name",
        "score", "temporal_tag", "expiry_date", "estimated_audience_size",
        "commercial_intent", "target_advertisers", "description",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for p in proposals:
            row = p.to_dict()
            row["commercial_intent"] = " | ".join(row.get("commercial_intent", []))
            row["target_advertisers"] = " | ".join(row.get("target_advertisers", []))
            writer.writerow({k: row.get(k, "") for k in fields})
    print(f"[reporter] CSV   → {path}")
    return path


def write_markdown(proposals: list[SegmentProposal], base_dir: str, run_date: str, top_n: int = 10) -> Path:
    out_dir = _segment_dir(base_dir, run_date)
    path = out_dir / "digest.md"

    def _badge(tag: str) -> str:
        colours = {
            "evergreen": "🟢",
            "seasonal": "🟡",
            "event-triggered": "🔵",
            "news-cycle": "🔴",
        }
        return colours.get(tag, "⚪")

    def _size_bar(size: str) -> str:
        bars = {"small": "▪", "medium": "▪▪", "large": "▪▪▪", "very-large": "▪▪▪▪"}
        return bars.get(size, "▪")

    lines = [
        f"# AdTech Segment Proposals — {run_date}",
        "",
        f"**{len(proposals)} segments proposed** | Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "---",
        "",
        "## Top Segments",
        "",
        "| # | Segment | IAB Category | Score | Type | Audience |",
        "|---|---------|-------------|-------|------|---------|",
    ]

    for i, p in enumerate(proposals[:top_n], 1):
        expiry = f" (exp. {p.expiry_date()})" if p.expiry_date() else ""
        lines.append(
            f"| {i} | **{p.name}** | {p.iab_tier2_id} {p.iab_tier2_name} | "
            f"{p.score}/100 | {_badge(p.temporal_tag)} {p.temporal_tag}{expiry} | "
            f"{_size_bar(p.estimated_audience_size)} {p.estimated_audience_size} |"
        )

    lines += ["", "---", "", "## Full Segment Details", ""]

    for i, p in enumerate(proposals, 1):
        lines += [
            f"### {i}. {p.name}",
            "",
            f"> {p.description}",
            "",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| **IAB Tier 1** | {p.iab_tier1_id} — {p.iab_tier1_name} |",
            f"| **IAB Tier 2** | {p.iab_tier2_id} — {p.iab_tier2_name} |",
            f"| **Score** | {p.score}/100 |",
            f"| **Type** | {_badge(p.temporal_tag)} {p.temporal_tag} |",
            f"| **Expiry** | {p.expiry_date() or 'N/A'} |",
            f"| **Audience Size** | {_size_bar(p.estimated_audience_size)} {p.estimated_audience_size} |",
            f"| **Commercial Intent** | {', '.join(p.commercial_intent)} |",
            f"| **Target Advertisers** | {', '.join(p.target_advertisers)} |",
        ]
        if p.overlap_with:
            lines.append(f"| **⚠ Overlaps with** | {p.overlap_with} |")
        lines += [
            f"| **Source Signals** | {' · '.join(p.source_signals[:3])} |",
            f"| **Reasoning** | _{p.reasoning}_ |",
            "",
        ]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[reporter] MD    → {path}")
    return path


def git_commit(base_dir: str, run_date: str) -> None:
    try:
        out_dir = str(Path(base_dir) / run_date)
        subprocess.run(["git", "add", out_dir], check=True, capture_output=True)
        msg = f"chore: add segment proposals for {run_date}"
        subprocess.run(["git", "commit", "-m", msg], check=True, capture_output=True)
        print(f"[reporter] git commit: {msg}")
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode() if exc.stderr else ""
        if "nothing to commit" in stderr:
            print("[reporter] git: nothing new to commit.")
        else:
            print(f"[reporter] git commit failed: {stderr[:200]}")
