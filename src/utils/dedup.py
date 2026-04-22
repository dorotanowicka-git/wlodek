"""D3: Deduplication — compare today's proposals against a rolling history window."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..intelligence.analyzer import SegmentProposal


def _load_historical(base_dir: str, lookback_days: int) -> list[str]:
    """Return a list of all segment names from the last N days."""
    today = datetime.now(timezone.utc)
    names: list[str] = []
    for offset in range(1, lookback_days + 1):
        date_str = (today - timedelta(days=offset)).strftime("%Y-%m-%d")
        path = Path(base_dir) / date_str / "proposals.json"
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
            for seg in data.get("segments", []):
                name = seg.get("name", "").strip().lower()
                if name:
                    names.append(name)
        except Exception:
            pass
    return names


def _similar(a: str, b: str, threshold: float) -> bool:
    """Simple character n-gram similarity."""
    def ngrams(s: str, n: int = 3) -> set[str]:
        s = s.lower()
        return {s[i:i+n] for i in range(len(s) - n + 1)} if len(s) >= n else {s}

    set_a = ngrams(a)
    set_b = ngrams(b)
    if not set_a or not set_b:
        return a.lower() == b.lower()
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) >= threshold


def filter_duplicates(
    proposals: list[SegmentProposal],
    base_dir: str,
    lookback_days: int,
    threshold: float = 0.8,
) -> tuple[list[SegmentProposal], list[str]]:
    """Return (new_proposals, suppressed_names)."""
    historical = _load_historical(base_dir, lookback_days)
    new: list[SegmentProposal] = []
    suppressed: list[str] = []

    for proposal in proposals:
        name = proposal.name
        is_dup = any(_similar(name, hist, threshold) for hist in historical)
        if is_dup:
            suppressed.append(name)
        else:
            new.append(proposal)
            historical.append(name.lower())

    if suppressed:
        print(f"[dedup] Suppressed {len(suppressed)} previously-seen segments: "
              f"{', '.join(suppressed[:5])}{'…' if len(suppressed) > 5 else ''}")
    return new, suppressed
