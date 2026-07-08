"""Simple JSON-backed state manager to persist last alerts and candle timestamps."""
from __future__ import annotations

import json
import threading
from typing import Any, Dict
from pathlib import Path


class StateManager:
    def __init__(self, path: str | Path = "state.json"):
        self.path = Path(path)
        self.lock = threading.RLock()
        self._state: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self._state = {}
            return
        with self.path.open("r", encoding="utf-8") as fh:
            try:
                self._state = json.load(fh)
            except Exception:
                self._state = {}

    def save(self) -> None:
        with self.lock:
            with self.path.open("w", encoding="utf-8") as fh:
                json.dump(self._state, fh, indent=2, default=str)

    def get(self, key: str, default=None):
        return self._state.get(key, default)

    def set(self, key: str, value) -> None:
        with self.lock:
            self._state[key] = value
            self.save()

    def get_symbol_state(self, symbol: str) -> Dict[str, Any]:
        return self._state.setdefault("symbols", {}).setdefault(symbol, {})

    def update_symbol(self, symbol: str, **kwargs) -> None:
        with self.lock:
            sym = self._state.setdefault("symbols", {}).setdefault(symbol, {})
            sym.update(kwargs)
            self.save()
