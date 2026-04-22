"""A3: Event Calendar — upcoming sports events, holidays, and public events."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import requests

from .news_feeds import Signal

_HEADERS = {"User-Agent": "AdTechSegmentBot/1.0"}


def _fetch_holidays(lookahead_days: int) -> list[Signal]:
    """Fetch public holidays from Nager.Date (free, no key required)."""
    today = datetime.now(timezone.utc)
    year = today.year
    signals: list[Signal] = []
    cutoff = today + timedelta(days=lookahead_days)

    try:
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/US"
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
        for h in resp.json():
            date_str = h.get("date", "")
            try:
                hdate = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if today <= hdate <= cutoff:
                name = h.get("name", "")
                signals.append(Signal(
                    title=f"Upcoming Holiday: {name}",
                    description=f"{name} is a US public holiday on {date_str}.",
                    category="event",
                    source="Public Holidays",
                    date=date_str,
                    url="",
                    tags=["holiday", name.lower()],
                ))
    except Exception as exc:
        print(f"[events] Holiday fetch failed: {exc}")
    return signals


def _fetch_sports_events(api_key: str, lookahead_days: int) -> list[Signal]:
    """Fetch upcoming events from Ticketmaster (optional)."""
    today = datetime.now(timezone.utc)
    start = today.strftime("%Y-%m-%dT00:00:00Z")
    end = (today + timedelta(days=lookahead_days)).strftime("%Y-%m-%dT23:59:59Z")
    signals: list[Signal] = []
    try:
        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        params = {
            "apikey": api_key,
            "classificationName": "sports",
            "startDateTime": start,
            "endDateTime": end,
            "size": 20,
            "sort": "relevance,desc",
        }
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        for event in data.get("_embedded", {}).get("events", []):
            name = event.get("name", "")
            event_date = event.get("dates", {}).get("start", {}).get("localDate", "")
            venue = event.get("_embedded", {}).get("venues", [{}])[0].get("name", "")
            url_link = event.get("url", "")
            signals.append(Signal(
                title=f"Sports Event: {name}",
                description=f"{name} at {venue} on {event_date}.",
                category="event",
                source="Ticketmaster",
                date=event_date,
                url=url_link,
                tags=["sports", "event"],
            ))
    except Exception as exc:
        print(f"[events] Ticketmaster fetch failed: {exc}")
    return signals


def _fetch_wikipedia_upcoming() -> list[Signal]:
    """Scrape Wikipedia's 'Upcoming events' section as a fallback."""
    from .wikipedia import fetch_wikipedia_events
    all_wiki = fetch_wikipedia_events()
    return [s for s in all_wiki if "upcoming" in s.title.lower() or s.category == "event"]


def fetch_events(config: dict) -> list[Signal]:
    lookahead = config.get("lookahead_days", 30)
    signals = _fetch_holidays(lookahead)

    tm_key = os.getenv("TICKETMASTER_API_KEY", "")
    if tm_key and config.get("ticketmaster_enabled", False):
        signals += _fetch_sports_events(tm_key, lookahead)

    return signals
