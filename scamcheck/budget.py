"""A daily spending cap for Claude API calls, so a public demo can't drain the credit."""
import json
import threading
from datetime import date
from pathlib import Path


class DailyBudget:
    def __init__(self, path: Path, limit_usd: float):
        self.path, self.limit = Path(path), float(limit_usd)
        self._lock = threading.Lock()

    def _load(self) -> dict:
        try:
            return json.loads(self.path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def spent_today(self) -> float:
        return self._load().get(date.today().isoformat(), 0.0)

    def can_spend(self) -> bool:
        return self.spent_today() < self.limit

    def add(self, usd: float) -> None:
        with self._lock:
            data = self._load()
            today = date.today().isoformat()
            data = {today: data.get(today, 0.0) + usd}   # keep only today
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(data))
