"""Telegram notification helper with basic command handling (/status, /ping)."""
from __future__ import annotations

import requests
import time
from typing import Optional
from utils import retry
from state import StateManager
from pytz import timezone
from datetime import datetime


class TelegramBot:
    def __init__(self, token: str, chat_id: str, state: StateManager):
        self.token = token
        self.chat_id = chat_id
        self.base = f"https://api.telegram.org/bot{self.token}"
        self.state = state
        self.update_offset = int(self.state.get("telegram_update_offset", 0) or 0)

    @retry(max_attempts=3, delay=1.0, backoff=2.0)
    def send_message(self, text: str) -> dict:
        url = f"{self.base}/sendMessage"
        resp = requests.post(url, json={"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _format_common(self, exchange: str, pair: str, timeframe: str, price: float, ts: datetime) -> str:
        ist = timezone("Asia/Kolkata")
        ts_local = ts.astimezone(ist)
        time_str = ts_local.strftime("%Y-%m-%d %H:%M:%S %Z")
        return f"Exchange: {exchange}\nPair: {pair}\nTimeframe: {timeframe}\nPrice: {price:.8f}\nTime: {time_str}"

    def send_buy(self, pair: str, timeframe: str, price: float, ts: datetime) -> None:
        body = "🟢 <b>BUY SIGNAL</b>\nEMA9 crossed ABOVE EMA50\n"
        body += self._format_common("Delta", pair, timeframe.upper(), price, ts)
        self.send_message(body)

    def send_sell(self, pair: str, timeframe: str, price: float, ts: datetime) -> None:
        body = "🔴 <b>SELL SIGNAL</b>\nEMA9 crossed BELOW EMA50\n"
        body += self._format_common("Delta", pair, timeframe.upper(), price, ts)
        self.send_message(body)

    def send_error(self, text: str) -> None:
        body = f"⚠️ <b>ERROR</b>\n{text}"
        try:
            self.send_message(body)
        except Exception:
            # swallow - errors in notifier should not crash
            pass

    def poll_commands(self) -> None:
        """Poll for simple bot commands and respond to /status and /ping."""
        url = f"{self.base}/getUpdates"
        try:
            resp = requests.get(url, params={"offset": self.update_offset, "timeout": 5}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            for upd in data.get("result", []):
                self.update_offset = int(upd["update_id"]) + 1
                self.state.set("telegram_update_offset", self.update_offset)
                msg = upd.get("message") or {}
                text = msg.get("text", "")
                from_id = msg.get("from", {}).get("id")
                if not text:
                    continue
                if text.strip() == "/ping":
                    self.send_message("Pong")
                elif text.strip() == "/status":
                    last = self.state.get("last_run") or "never"
                    last_signal = self.state.get("last_signal") or "none"
                    symbols = ",".join(self.state.get("symbols", [])) or ""
                    self.send_message(f"Running\nLast run: {last}\nLast signal: {last_signal}\nSymbols: {symbols}")
        except Exception:
            # don't crash for telegram polling issues
            return
