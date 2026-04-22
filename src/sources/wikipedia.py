"""A4: Wikipedia Current Events — parses the Portal:Current_events page."""

from __future__ import annotations

import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from .news_feeds import Signal

_WIKI_URL = "https://en.wikipedia.org/wiki/Portal:Current_events"
_HEADERS = {"User-Agent": "AdTechSegmentBot/1.0 (research; non-commercial)"}


def fetch_wikipedia_events() -> list[Signal]:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        resp = requests.get(_WIKI_URL, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        signals: list[Signal] = []
        # Each day's events are inside .current-events-content divs
        for section in soup.select(".current-events-content")[:3]:
            category = ""
            for elem in section.find_all(["b", "li"]):
                text = elem.get_text(separator=" ", strip=True)
                text = re.sub(r"\s+", " ", text)
                if not text or len(text) < 20:
                    continue
                if elem.name == "b":
                    category = text
                    continue
                # clean wiki citation artifacts like [1], [2]
                text = re.sub(r"\[\d+\]", "", text).strip()
                if len(text) > 30:
                    signals.append(Signal(
                        title=text[:200],
                        description=f"[{category}] {text[:400]}" if category else text[:400],
                        category="wikipedia",
                        source="Wikipedia Current Events",
                        date=today,
                        url=_WIKI_URL,
                        tags=[category] if category else [],
                    ))
        return signals[:50]
    except Exception as exc:
        print(f"[wikipedia] Skipped: {exc}")
        return []
