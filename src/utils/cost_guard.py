"""D5: Cost guard — tracks daily Claude API spend and enforces a hard limit."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class CostGuard:
    def __init__(self, daily_limit: float, warn_at: float, state_file: str = ".cost_state.json"):
        self.daily_limit = daily_limit
        self.warn_at = warn_at
        self._state_file = Path(state_file)
        self._today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self._spent = self._load()

    def _load(self) -> float:
        if not self._state_file.exists():
            return 0.0
        try:
            data = json.loads(self._state_file.read_text())
            if data.get("date") == self._today:
                return float(data.get("spent_usd", 0.0))
        except Exception:
            pass
        return 0.0

    def _save(self) -> None:
        self._state_file.write_text(
            json.dumps({"date": self._today, "spent_usd": round(self._spent, 6)})
        )

    def check(self) -> None:
        if self._spent >= self.daily_limit:
            raise RuntimeError(
                f"Daily cost limit ${self.daily_limit:.2f} reached "
                f"(spent ${self._spent:.4f}). Aborting."
            )
        if self._spent >= self.warn_at:
            print(
                f"[cost_guard] ⚠ Approaching daily limit: "
                f"${self._spent:.4f} / ${self.daily_limit:.2f}"
            )

    def record(self, cost_usd: float) -> None:
        self._spent += cost_usd
        self._save()
        print(f"[cost_guard] Cost this run: ${cost_usd:.4f} | Daily total: ${self._spent:.4f}")

    @property
    def spent(self) -> float:
        return self._spent
