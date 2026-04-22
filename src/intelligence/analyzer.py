"""B1-B5: Claude-powered intelligence layer — IAB mapping, scoring, intent, temporal tagging, overlap detection."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import anthropic

from .iab_taxonomy import IAB_TAXONOMY_TEXT
from ..sources.news_feeds import Signal
from ..utils.cost_guard import CostGuard

_SYSTEM_PROMPT = f"""You are a senior AdTech data analyst for a leading Data Provider. Your job is to
analyse real-time signals (news, trends, events, economic data) and propose high-value audience
segments for Demand-Side Platform (DSP) buyers. You use the IAB Content Taxonomy 3.0 to classify
every segment precisely.

## Your Responsibilities
1. **IAB Classification (B1)** — Map each segment to the exact IAB Tier 1 and Tier 2 category.
2. **Segment Scoring (B2)** — Score 0-100 based on audience size, commercial intent density,
   advertiser demand, and novelty. 70+ = premium, 50-69 = standard, <50 = low priority.
3. **Intent Signal Inference (B3)** — Go beyond the topic. Infer downstream commercial behaviours:
   what will this audience *buy*, *search for*, or *respond to* in the next 7-30 days?
4. **Temporal Tagging (B4)** — Classify each segment as one of:
   - `evergreen` — sustained interest, no expiry
   - `seasonal` — recurs annually (holidays, sports seasons, tax season)
   - `event-triggered` — tied to a specific upcoming event; include expiry date
   - `news-cycle` — tied to breaking news; short shelf life (3-7 days)
5. **Overlap Detection (B5)** — Within your proposed set, flag if any two segments would target
   almost identical audiences (>80% overlap). Only keep the stronger one.

## Output Format
Return ONLY valid JSON — no markdown, no explanation outside the JSON block.
Return a JSON object with a single key `"segments"` containing an array of segment objects.

Each segment object MUST have exactly these fields:
{{
  "name": "<concise segment name, max 60 chars>",
  "description": "<1-2 sentence description for DSP buyers, max 200 chars>",
  "iab_tier1_id": "<e.g. IAB24>",
  "iab_tier1_name": "<e.g. Sports>",
  "iab_tier2_id": "<e.g. IAB24-37>",
  "iab_tier2_name": "<e.g. Soccer / MLS / International Football>",
  "score": <integer 0-100>,
  "commercial_intent": ["<intent label 1>", "<intent label 2>"],
  "target_advertisers": ["<advertiser vertical 1>", "<advertiser vertical 2>"],
  "temporal_tag": "<evergreen|seasonal|event-triggered|news-cycle>",
  "expiry_days": <null or integer days from today until segment expires>,
  "estimated_audience_size": "<small|medium|large|very-large>",
  "source_signals": ["<signal title 1>", "<signal title 2>"],
  "overlap_with": <null or "name of overlapping segment if >80% overlap">,
  "reasoning": "<1 sentence internal reasoning>"
}}

## IAB Content Taxonomy 3.0 Reference (use for all classifications)

{IAB_TAXONOMY_TEXT}
"""


@dataclass
class SegmentProposal:
    name: str
    description: str
    iab_tier1_id: str
    iab_tier1_name: str
    iab_tier2_id: str
    iab_tier2_name: str
    score: int
    commercial_intent: list[str] = field(default_factory=list)
    target_advertisers: list[str] = field(default_factory=list)
    temporal_tag: str = "evergreen"
    expiry_days: int | None = None
    estimated_audience_size: str = "medium"
    source_signals: list[str] = field(default_factory=list)
    overlap_with: str | None = None
    reasoning: str = ""
    date_proposed: str = ""

    def expiry_date(self) -> str | None:
        if self.expiry_days is None:
            return None
        d = datetime.now(timezone.utc) + timedelta(days=self.expiry_days)
        return d.strftime("%Y-%m-%d")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "iab_tier1_id": self.iab_tier1_id,
            "iab_tier1_name": self.iab_tier1_name,
            "iab_tier2_id": self.iab_tier2_id,
            "iab_tier2_name": self.iab_tier2_name,
            "score": self.score,
            "commercial_intent": self.commercial_intent,
            "target_advertisers": self.target_advertisers,
            "temporal_tag": self.temporal_tag,
            "expiry_days": self.expiry_days,
            "expiry_date": self.expiry_date(),
            "estimated_audience_size": self.estimated_audience_size,
            "source_signals": self.source_signals,
            "overlap_with": self.overlap_with,
            "reasoning": self.reasoning,
            "date_proposed": self.date_proposed,
        }


def _build_user_prompt(
    signals: list[Signal],
    verticals: list[str],
    max_segments: int,
    run_date: str,
) -> str:
    by_category: dict[str, list[Signal]] = {}
    for s in signals:
        by_category.setdefault(s.category, []).append(s)

    lines = [f"# Daily Signal Digest — {run_date}", ""]
    if verticals:
        lines += [f"**Priority advertiser verticals:** {', '.join(verticals)}", ""]

    section_labels = {
        "news": "## Breaking News & Trending Topics",
        "trend": "## Rising Search Trends",
        "event": "## Upcoming Events (next 30 days)",
        "wikipedia": "## Wikipedia Current Events",
        "economic": "## Economic Indicators & Financial News",
    }

    for cat, label in section_labels.items():
        items = by_category.get(cat, [])
        if not items:
            continue
        lines.append(label)
        for s in items[:25]:
            line = f"- [{s.source}] {s.title}"
            if s.description and s.description != s.title:
                line += f" — {s.description[:120]}"
            lines.append(line)
        lines.append("")

    total = sum(len(v) for v in by_category.values())
    lines.append(
        f"---\nBased on the {total} signals above, propose up to {max_segments} distinct, "
        "high-value audience segments. Prioritise specificity over breadth. "
        "Remove any segment with a score below 40. Remove duplicates via overlap_with."
    )
    return "\n".join(lines)


def _parse_response(text: str) -> list[dict]:
    # strip optional markdown fences
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text.strip(), flags=re.MULTILINE)
    data = json.loads(text)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "segments" in data:
        return data["segments"]
    raise ValueError(f"Unexpected response shape: {list(data.keys())}")


def run_analysis(
    signals: list[Signal],
    config: dict,
    cost_guard: CostGuard,
    run_date: str | None = None,
) -> list[SegmentProposal]:
    if run_date is None:
        run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    verticals = config.get("verticals", [])
    max_segments = config.get("intelligence", {}).get("max_segments", 30)
    min_score = config.get("intelligence", {}).get("min_score", 40)
    model = config.get("intelligence", {}).get("model", "claude-opus-4-7")
    max_tokens = config.get("intelligence", {}).get("max_tokens", 8000)

    if not signals:
        print("[analyzer] No signals to analyse.")
        return []

    cost_guard.check()

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    user_prompt = _build_user_prompt(signals, verticals, max_segments, run_date)

    print(f"[analyzer] Calling {model} with {len(signals)} signals …")

    full_text = ""
    input_tokens = 0
    output_tokens = 0
    cache_creation_tokens = 0
    cache_read_tokens = 0

    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        thinking={"type": "adaptive"},
        system=[
            {
                "type": "text",
                "text": _SYSTEM_PROMPT,
                # Cache the large taxonomy + instructions — stable across daily runs
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for event in stream:
            if (
                event.type == "content_block_delta"
                and hasattr(event.delta, "type")
                and event.delta.type == "text_delta"
            ):
                full_text += event.delta.text

        final = stream.get_final_message()
        usage = final.usage
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens
        cache_creation_tokens = getattr(usage, "cache_creation_input_tokens", 0) or 0
        cache_read_tokens = getattr(usage, "cache_read_input_tokens", 0) or 0

    # Track cost — Opus 4.7 pricing: $5/1M input, $25/1M output, $6.25/1M cache write, $0.50/1M cache read
    input_cost = (input_tokens / 1_000_000) * 5.00
    output_cost = (output_tokens / 1_000_000) * 25.00
    cache_write_cost = (cache_creation_tokens / 1_000_000) * 6.25
    cache_read_cost = (cache_read_tokens / 1_000_000) * 0.50
    total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost
    cost_guard.record(total_cost)

    print(
        f"[analyzer] Tokens — input: {input_tokens} (cache_write: {cache_creation_tokens}, "
        f"cache_read: {cache_read_tokens}), output: {output_tokens} | "
        f"Cost: ${total_cost:.4f}"
    )

    raw_segments = _parse_response(full_text)

    proposals: list[SegmentProposal] = []
    for raw in raw_segments:
        score = int(raw.get("score", 0))
        if score < min_score:
            continue
        proposals.append(SegmentProposal(
            name=raw.get("name", "Unnamed Segment"),
            description=raw.get("description", ""),
            iab_tier1_id=raw.get("iab_tier1_id", ""),
            iab_tier1_name=raw.get("iab_tier1_name", ""),
            iab_tier2_id=raw.get("iab_tier2_id", ""),
            iab_tier2_name=raw.get("iab_tier2_name", ""),
            score=score,
            commercial_intent=raw.get("commercial_intent", []),
            target_advertisers=raw.get("target_advertisers", []),
            temporal_tag=raw.get("temporal_tag", "evergreen"),
            expiry_days=raw.get("expiry_days"),
            estimated_audience_size=raw.get("estimated_audience_size", "medium"),
            source_signals=raw.get("source_signals", []),
            overlap_with=raw.get("overlap_with"),
            reasoning=raw.get("reasoning", ""),
            date_proposed=run_date,
        ))

    proposals.sort(key=lambda p: p.score, reverse=True)
    print(f"[analyzer] {len(proposals)} segments proposed (score ≥ {min_score}).")
    return proposals
