"""A1: RSS/News Feed Aggregator — pulls trending topics from configurable feeds."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

import feedparser
import requests


@dataclass
class Signal:
    title: str
    description: str
    category: str          # news / trend / event / economic / wikipedia
    source: str
    date: str
    url: str = ""
    tags: list[str] = field(default_factory=list)


def fetch_news(feed_configs: list[dict], max_per_feed: int = 10) -> list[Signal]:
    signals: list[Signal] = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for feed in feed_configs:
        url = feed.get("url", "")
        name = feed.get("name", url)
        try:
            parsed = feedparser.parse(url)
            entries = parsed.entries[:max_per_feed]
            for entry in entries:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                link = entry.get("link", "")
                tags = [t.get("term", "") for t in entry.get("tags", [])]

                # strip html from summary
                if "<" in summary:
                    import re
                    summary = re.sub(r"<[^>]+>", " ", summary).strip()
                summary = summary[:500]

                if title:
                    signals.append(Signal(
                        title=title,
                        description=summary,
                        category="news",
                        source=name,
                        date=today,
                        url=link,
                        tags=tags,
                    ))
        except Exception as exc:
            print(f"[news_feeds] Failed to fetch {name}: {exc}")

    return signals
