# AdTech Daily Segment Proposal Pipeline

An AI-powered pipeline that aggregates real-time signals from multiple sources (news, trends, events, economic data) and uses Claude AI to propose high-value audience segments for programmatic advertising. Segments are classified using the IAB Content Taxonomy 3.0 and output in JSON, CSV, and Markdown formats.

The pipeline runs automatically every day at 06:00 UTC via GitHub Actions.

---

## How It Works

### Architecture Overview

```
run.py (CLI entry point)
  └─> src/pipeline.py (orchestrator)
      ├─> Signal Gathering (5 sources)
      │   ├─> src/sources/news_feeds.py    — RSS feeds (Reuters, BBC, NYT, etc.)
      │   ├─> src/sources/google_trends.py — Google Trends real-time searches
      │   ├─> src/sources/events.py        — Public holidays + Ticketmaster events
      │   ├─> src/sources/wikipedia.py     — Wikipedia Portal:Current_events
      │   └─> src/sources/economic.py      — FRED API + economic RSS feeds
      │
      ├─> AI Analysis
      │   └─> src/intelligence/analyzer.py — Claude Opus 4.7 with IAB taxonomy
      │
      ├─> Deduplication
      │   └─> src/utils/dedup.py           — n-gram similarity against 30-day history
      │
      ├─> Output
      │   └─> src/output/reporter.py       — JSON, CSV, Markdown + git commit
      │
      └─> Notifications
          └─> src/output/notifier.py       — Slack webhook + SMTP email
```

### Step-by-Step Flow

**1. Signal Gathering**

The pipeline pulls ~150–200 signals per run from five sources:

| Source | Module | Auth | Default |
|--------|--------|------|---------|
| RSS Feeds (Reuters, BBC, NYT, TechCrunch, Guardian, ESPN, Sky) | `news_feeds.py` | None | 12 feeds, 10 items each |
| Google Trends | `google_trends.py` | None | US, daily |
| Public Holidays (Nager.Date API) | `events.py` | None | 30-day window |
| Ticketmaster Sports Events | `events.py` | `TICKETMASTER_API_KEY` (optional) | Disabled |
| Wikipedia Current Events | `wikipedia.py` | None | Up to 50 items |
| FRED Economic Indicators | `economic.py` | `FRED_API_KEY` (optional) | Fallback: Reuters/NYT economic RSS |

All sources are wrapped in try/except — a failing source is skipped silently, and the pipeline continues with whatever signals were collected.

**2. AI Analysis (Claude Opus 4.7)**

Signals are assembled into a structured "Daily Signal Digest" prompt and sent to Claude. The system prompt includes the complete IAB Content Taxonomy 3.0 (cached server-side to reduce cost).

Claude performs five tasks (B1–B5):
- **B1 — IAB Classification**: Maps each segment to an exact IAB Tier 1 and Tier 2 category
- **B2 — Segment Scoring**: Scores 0–100 based on audience size, commercial intent, advertiser demand, and novelty
- **B3 — Intent Inference**: Identifies downstream commercial behaviours (what this audience will buy/search for in the next 7–30 days)
- **B4 — Temporal Tagging**: Labels each segment as `evergreen`, `seasonal`, `event-triggered`, or `news-cycle`
- **B5 — Overlap Detection**: Flags duplicate audience coverage within the proposed set

Claude returns a JSON object with a `segments` array. Segments scoring below `min_score` (default: 40) are dropped.

**3. Deduplication**

Before writing output, proposed segments are compared against the last 30 days of `proposals.json` files using character trigram similarity. Any segment with >80% similarity to a previously-proposed one is suppressed. This prevents daily repetition of perennial segments.

**4. Output**

For each run, three files are written to `segments/YYYY-MM-DD/`:

| File | Format | Contents |
|------|--------|---------|
| `proposals.json` | JSON | Full metadata for all segments |
| `proposals.csv` | CSV | Tabular view of key fields |
| `digest.md` | Markdown | Human-readable digest; top-10 summary table + full details |

The output directory is automatically git-committed (configurable).

**5. Notifications** (optional)

If configured, the top-N segments are posted to a Slack channel and/or emailed via SMTP.

---

## Project Structure

```
wlodek/
├── run.py                          # CLI entry point
├── config.yaml                     # All pipeline settings
├── requirements.txt                # Python dependencies
├── .env.example                    # Template for secrets
├── .github/
│   └── workflows/
│       └── daily.yml               # GitHub Actions — runs daily at 06:00 UTC
└── src/
    ├── pipeline.py                 # Main orchestrator
    ├── intelligence/
    │   ├── analyzer.py             # Claude API integration + SegmentProposal dataclass
    │   └── iab_taxonomy.py         # IAB Content Taxonomy 3.0 reference (static)
    ├── sources/
    │   ├── news_feeds.py           # RSS aggregation; defines the Signal dataclass
    │   ├── google_trends.py        # Google Trends via pytrends
    │   ├── events.py               # Holidays + Ticketmaster events
    │   ├── wikipedia.py            # Wikipedia current events scraper
    │   └── economic.py             # FRED API + economic RSS fallback
    ├── output/
    │   ├── reporter.py             # write_json / write_csv / write_markdown / git_commit
    │   └── notifier.py             # send_slack / send_email
    └── utils/
        ├── cost_guard.py           # Daily Claude API spend tracker (hard limit)
        └── dedup.py                # Rolling 30-day deduplication
```

---

## Setup & Installation

### Prerequisites

- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com) (required)
- Git (for auto-commit output feature)

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd wlodek
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `urllib3<2.0` is pinned intentionally — `pytrends` is incompatible with urllib3 v2.

### 3. Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` and set your credentials:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional — enables richer economic data
FRED_API_KEY=your_fred_key          # https://fred.stlouisfed.org/docs/api/api_key.html

# Optional — enables sports event signals
TICKETMASTER_API_KEY=your_tm_key   # https://developer.ticketmaster.com

# Optional — Slack notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Optional — email notifications
NOTIFICATION_EMAIL=recipient@example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=sender@example.com
SMTP_PASSWORD=your_app_password
```

---

## Running the Pipeline

### Basic run (today's date)

```bash
python run.py
```

### Dry run — analyse signals without writing files

```bash
python run.py --dry-run
```

### Backfill a specific date

```bash
python run.py --date 2025-06-01
```

### Add extra advertiser verticals

```bash
python run.py --vertical gaming --vertical crypto
```

### Override output directory

```bash
python run.py --output-dir /tmp/segments
```

### Use a custom config file

```bash
python run.py --config my-config.yaml
```

---

## Configuration (`config.yaml`)

All behaviour is controlled from `config.yaml`. Key sections:

```yaml
intelligence:
  model: "claude-opus-4-7"   # Claude model to use
  max_tokens: 8000           # Max tokens in Claude's response
  max_segments: 30           # Max segments to propose per run
  min_score: 40              # Minimum score (0-100) to include a segment

output:
  dir: "segments"            # Root output directory
  formats: [json, csv, markdown]
  git_commit: true           # Auto-commit output files to git

dedup:
  lookback_days: 30          # Compare against last N days of history
  similarity_threshold: 0.8  # Suppress segments with >80% name similarity

cost:
  daily_limit_usd: 5.00      # Hard daily Claude API spend cap
  warn_at_usd: 3.00          # Warning threshold

events:
  lookahead_days: 30         # How far ahead to look for upcoming events
  ticketmaster_enabled: false # Set to true if TICKETMASTER_API_KEY is set

economic:
  fred_enabled: false        # Set to true if FRED_API_KEY is set
```

---

## Output Format

Each run produces files in `segments/YYYY-MM-DD/`:

### `proposals.json`

```json
{
  "date": "2026-04-24",
  "generated_at": "2026-04-24T06:01:23.456789+00:00",
  "total": 18,
  "segments": [
    {
      "name": "Spring Home Improvement Shoppers",
      "description": "Consumers actively researching home renovation projects...",
      "iab_tier1_id": "IAB13",
      "iab_tier1_name": "Home & Garden",
      "iab_tier2_id": "IAB13-7",
      "iab_tier2_name": "Remodeling & Construction",
      "score": 87,
      "commercial_intent": ["product research", "contractor search", "purchase intent"],
      "target_advertisers": ["retail", "finance", "real_estate"],
      "temporal_tag": "seasonal",
      "expiry_days": 45,
      "expiry_date": "2026-06-08",
      "estimated_audience_size": "large",
      "source_signals": ["BBC Business: Home improvement boom...", "..."],
      "overlap_with": null,
      "reasoning": "Spring seasonality + rising material costs driving early purchase decisions.",
      "date_proposed": "2026-04-24"
    }
  ]
}
```

### Segment Score Interpretation

| Score | Tier | Meaning |
|-------|------|---------|
| 70–100 | Premium | High audience size + strong commercial intent |
| 50–69 | Standard | Moderate reach and relevance |
| 40–49 | Low priority | Included, but limited buyer demand expected |
| < 40 | Dropped | Filtered out before output |

### Temporal Tags

| Tag | Badge | Meaning |
|-----|-------|---------|
| `evergreen` | 🟢 | Sustained interest, no expiry |
| `seasonal` | 🟡 | Recurs annually |
| `event-triggered` | 🔵 | Tied to a specific upcoming event |
| `news-cycle` | 🔴 | Breaking news; 3–7 day shelf life |

---

## GitHub Actions

The pipeline runs automatically via `.github/workflows/daily.yml`:

- **Schedule**: Daily at 06:00 UTC (after overnight news cycle, before US market open)
- **Manual trigger**: Go to Actions → "Daily Segment Proposals" → "Run workflow"

### Required GitHub Secrets

Add these in your repo Settings → Secrets and Variables → Actions:

| Secret | Required |
|--------|---------|
| `ANTHROPIC_API_KEY` | Yes |
| `FRED_API_KEY` | No |
| `TICKETMASTER_API_KEY` | No |
| `SLACK_WEBHOOK_URL` | No |
| `NOTIFICATION_EMAIL` | No |
| `SMTP_HOST` | No |
| `SMTP_PORT` | No |
| `SMTP_USER` | No |
| `SMTP_PASSWORD` | No |

After each run, the pipeline auto-commits the output files and pushes them back to the repo.

---

## Cost Management

The pipeline uses Claude Opus 4.7, charged per token. Approximate costs per run:

| Component | Pricing |
|-----------|---------|
| Input tokens (incl. IAB taxonomy) | $5.00 / 1M tokens |
| Output tokens (segment JSON) | $25.00 / 1M tokens |
| Cache write (first run, taxonomy) | $6.25 / 1M tokens |
| Cache read (subsequent runs) | $0.50 / 1M tokens |
| **Typical run cost** | **~$0.05–$0.50** |

The `CostGuard` class tracks spending in `.cost_state.json` (reset daily at UTC midnight):
- If `warn_at_usd` is exceeded, a warning is printed
- If `daily_limit_usd` is exceeded, the pipeline aborts before calling the API

---

## Troubleshooting

### `RuntimeError: ANTHROPIC_API_KEY is not set`

Create a `.env` file in the project root:
```bash
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
```

### `[google_trends] Skipped: The request failed: Google returned a response with code 404`

This is a known issue: Google deprecated the `/trends/trendingsearches/daily/rss` endpoint that `pytrends` uses. The pipeline handles this gracefully — it skips Google Trends and continues with the other 4 sources (~130+ signals).

### `[pipeline] No signals collected — aborting`

All 5 data sources failed. Check your internet connection and verify the RSS feed URLs in `config.yaml` are reachable.

### `[cost_guard] Daily cost limit reached`

The pipeline spent `daily_limit_usd` today. Delete `.cost_state.json` to reset (or wait until UTC midnight). Consider raising `daily_limit_usd` in `config.yaml`.

### `git commit failed: nothing to commit`

Output files for this date already exist and have not changed. This is harmless.

### `ModuleNotFoundError: No module named 'anthropic'`

Activate your virtual environment before running:
```bash
source .venv/bin/activate
```

---

## Key Design Decisions

- **IAB Taxonomy is prompt-cached**: The large taxonomy text is sent as a cached system prompt block. After the first call, cache hits cost ~10× less than regular input tokens.
- **Adaptive thinking enabled**: Claude uses adaptive extended thinking, letting it reason through complex signal combinations before generating the JSON output.
- **No database**: Output is plain files committed to git. The git history is the audit trail.
- **Graceful degradation**: Every data source is wrapped in try/except. A broken feed or blocked API never takes down the whole pipeline.
- **Dedup is name-based**: Deduplication uses character trigram similarity on segment names, not semantic similarity. This is fast and deterministic but relies on Claude naming segments consistently across runs.
