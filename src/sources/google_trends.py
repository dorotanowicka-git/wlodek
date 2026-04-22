"""A2: Google Trends — surfaces rising search queries for the configured geo."""

from __future__ import annotations

from datetime import datetime, timezone

from .news_feeds import Signal


def fetch_trends(geo: str = "US", timeframe: str = "now 1-d") -> list[Signal]:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 30), retries=2, backoff_factor=0.5)
        df = pt.trending_searches(pn=geo.lower())
        signals: list[Signal] = []
        for term in df[0].tolist():
            term = str(term).strip()
            if term:
                signals.append(Signal(
                    title=f"Trending: {term}",
                    description=f"'{term}' is trending on Google Search in {geo}.",
                    category="trend",
                    source="Google Trends",
                    date=today,
                    url="",
                    tags=[term],
                ))
        return signals
    except Exception as exc:
        print(f"[google_trends] Skipped: {exc}")
        return []
