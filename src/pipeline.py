"""Main orchestrator — ties all modules together into one daily pipeline run."""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .intelligence.analyzer import run_analysis
from .output.notifier import send_email, send_slack
from .output.reporter import git_commit, write_csv, write_json, write_markdown
from .sources.economic import fetch_economic
from .sources.events import fetch_events
from .sources.google_trends import fetch_trends
from .sources.news_feeds import Signal, fetch_news
from .sources.wikipedia import fetch_wikipedia_events
from .utils.cost_guard import CostGuard
from .utils.dedup import filter_duplicates


def _load_config(config_path: str) -> dict:
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _gather_signals(config: dict) -> list[Signal]:
    signals: list[Signal] = []

    feed_cfgs = config.get("news_feeds", [])
    if feed_cfgs:
        print(f"[pipeline] Fetching news from {len(feed_cfgs)} feeds …")
        signals += fetch_news(feed_cfgs)

    trends_cfg = config.get("google_trends", {})
    print("[pipeline] Fetching Google Trends …")
    signals += fetch_trends(
        geo=trends_cfg.get("geo", "US"),
        timeframe=trends_cfg.get("timeframe", "now 1-d"),
    )

    events_cfg = config.get("events", {})
    print("[pipeline] Fetching upcoming events …")
    signals += fetch_events(
        lookahead_days=events_cfg.get("lookahead_days", 30),
        ticketmaster_enabled=events_cfg.get("ticketmaster_enabled", False),
    )

    print("[pipeline] Fetching Wikipedia current events …")
    signals += fetch_wikipedia_events()

    econ_cfg = config.get("economic", {})
    print("[pipeline] Fetching economic indicators …")
    signals += fetch_economic(fred_enabled=econ_cfg.get("fred_enabled", False))

    print(f"[pipeline] Total signals collected: {len(signals)}")
    return signals


def run(
    config_path: str = "config.yaml",
    run_date: str | None = None,
    dry_run: bool = False,
    extra_verticals: list[str] | None = None,
    output_dir: str | None = None,
) -> int:
    """
    Execute the full pipeline. Returns the number of segments written.
    """
    start = time.monotonic()

    config = _load_config(config_path)

    if run_date is None:
        run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if output_dir:
        config.setdefault("output", {})["dir"] = output_dir

    if extra_verticals:
        config.setdefault("verticals", [])
        for v in extra_verticals:
            if v not in config["verticals"]:
                config["verticals"].append(v)

    base_dir = config.get("output", {}).get("dir", "segments")

    cost_cfg = config.get("cost", {})
    cost_guard = CostGuard(
        daily_limit=cost_cfg.get("daily_limit_usd", 5.00),
        warn_at=cost_cfg.get("warn_at_usd", 3.00),
    )

    signals = _gather_signals(config)
    if not signals:
        print("[pipeline] No signals collected — aborting.")
        return 0

    proposals = run_analysis(signals, config, cost_guard, run_date=run_date)
    if not proposals:
        print("[pipeline] Analyzer returned no proposals.")
        return 0

    dedup_cfg = config.get("dedup", {})
    proposals, suppressed = filter_duplicates(
        proposals,
        base_dir=base_dir,
        lookback_days=dedup_cfg.get("lookback_days", 30),
        threshold=dedup_cfg.get("similarity_threshold", 0.8),
    )
    if not proposals:
        print("[pipeline] All proposals were duplicates of recent segments.")
        return 0

    if dry_run:
        print(f"[pipeline] DRY RUN — {len(proposals)} segments would be written.")
        for p in proposals[:5]:
            print(f"  • {p.score:3d}  {p.name}")
        if len(proposals) > 5:
            print(f"  … and {len(proposals) - 5} more")
        elapsed = time.monotonic() - start
        print(f"[pipeline] Done (dry run) in {elapsed:.1f}s.")
        return len(proposals)

    output_cfg = config.get("output", {})
    formats = output_cfg.get("formats", ["json", "csv", "markdown"])

    if "json" in formats:
        write_json(proposals, base_dir, run_date)
    if "csv" in formats:
        write_csv(proposals, base_dir, run_date)
    if "markdown" in formats:
        top_n = config.get("notifications", {}).get("top_n", 10)
        write_markdown(proposals, base_dir, run_date, top_n=top_n)

    if output_cfg.get("git_commit", True):
        git_commit(base_dir, run_date)

    notif_cfg = config.get("notifications", {})
    top_n = notif_cfg.get("top_n", 10)

    if notif_cfg.get("slack_enabled", False) or os.getenv("SLACK_WEBHOOK_URL"):
        send_slack(proposals, run_date, top_n=top_n)

    if notif_cfg.get("email_enabled", False) or os.getenv("NOTIFICATION_EMAIL"):
        send_email(proposals, run_date, top_n=top_n)

    elapsed = time.monotonic() - start
    print(
        f"[pipeline] Complete — {len(proposals)} segments written "
        f"(+{len(suppressed)} suppressed) in {elapsed:.1f}s."
    )
    return len(proposals)
