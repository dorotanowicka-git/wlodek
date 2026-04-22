"""A5: Economic Indicators — FRED API releases and financial headlines."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import requests

from .news_feeds import Signal

_HEADERS = {"User-Agent": "AdTechSegmentBot/1.0"}


def _fetch_fred(api_key: str, series_configs: list[dict]) -> list[Signal]:
    today = datetime.now(timezone.utc)
    observation_start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    signals: list[Signal] = []

    for series in series_configs:
        series_id = series.get("id", "")
        series_name = series.get("name", series_id)
        try:
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": series_id,
                "api_key": api_key,
                "file_type": "json",
                "observation_start": observation_start,
                "sort_order": "desc",
                "limit": 3,
            }
            resp = requests.get(url, params=params, headers=_HEADERS, timeout=10)
            resp.raise_for_status()
            observations = resp.json().get("observations", [])
            if observations:
                latest = observations[0]
                val = latest.get("value", "N/A")
                date = latest.get("date", "")
                signals.append(Signal(
                    title=f"Economic Indicator: {series_name}",
                    description=f"Latest {series_name} reading: {val} (as of {date}).",
                    category="economic",
                    source="FRED",
                    date=date,
                    url=f"https://fred.stlouisfed.org/series/{series_id}",
                    tags=["economic", series_id.lower()],
                ))
        except Exception as exc:
            print(f"[economic] FRED series {series_id} failed: {exc}")
    return signals


def _fetch_economic_news() -> list[Signal]:
    """Fetch economic-tagged news from RSS as a no-key fallback."""
    import feedparser
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    signals: list[Signal] = []
    feeds = [
        ("https://feeds.reuters.com/reuters/businessNews", "Reuters Business"),
        ("https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml", "NYT Economy"),
    ]
    for url, name in feeds:
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries[:5]:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()[:400]
                if title:
                    signals.append(Signal(
                        title=title,
                        description=summary,
                        category="economic",
                        source=name,
                        date=today,
                        url=entry.get("link", ""),
                        tags=["economy", "finance"],
                    ))
        except Exception:
            pass
    return signals


def fetch_economic(config: dict) -> list[Signal]:
    fred_key = os.getenv("FRED_API_KEY", "")
    if fred_key and config.get("fred_enabled", False):
        return _fetch_fred(fred_key, config.get("series", []))
    return _fetch_economic_news()
