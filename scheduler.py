"""Scheduler that runs the check loop and manages symbol evaluation."""
from __future__ import annotations

import schedule
import time
from typing import Any
from logger import get_logger
from exchange import DeltaExchangeClient
from strategy import evaluate_signal
from state import StateManager
from telegram_bot import TelegramBot
from datetime import datetime

LOG = get_logger(__name__)


class Scheduler:
    def __init__(self, config, state: StateManager):
        self.config = config
        self.state = state
        self.exchange = DeltaExchangeClient()
        self.telegram = TelegramBot(config.telegram_token, config.chat_id, state)

    def start(self, run_once: bool = False) -> None:
        self.check_all()
        if run_once:
            return
        schedule.every(self.config.check_interval).seconds.do(self.check_all)
        LOG.info("Scheduler started: checking every %s seconds", self.config.check_interval)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def check_all(self) -> None:
        LOG.info("Running scheduled check for symbols: %s", ",".join(self.config.symbols))
        for symbol in self.config.symbols:
            try:
                self._check_symbol(symbol)
            except Exception as exc:
                LOG.exception("Error checking %s: %s", symbol, exc)
                self.telegram.send_error(f"Error checking {symbol}: {exc}")

        # poll telegram commands
        try:
            self.telegram.poll_commands()
        except Exception:
            LOG.exception("Telegram polling failed")

    def _check_symbol(self, symbol: str) -> None:
        df = self.exchange.fetch_ohlcv(symbol, timeframe=self.config.timeframe, limit=200)
        if df.empty:
            LOG.warning("No data for %s", symbol)
            return

        result = evaluate_signal(df)
        signal = result.get("signal")
        ts = result.get("timestamp")
        price = result.get("price")

        sym_state = self.state.get_symbol_state(symbol)
        last_ts = sym_state.get("last_candle_timestamp")

        # Only alert for a new closed candle
        ts_str = str(ts)
        if last_ts and last_ts == ts_str:
            LOG.debug("No new candle for %s (timestamp unchanged)", symbol)
            return

        # update last candle timestamp
        self.state.update_symbol(symbol, last_candle_timestamp=ts_str)

        if not signal:
            LOG.info("No signal for %s at %s", symbol, ts)
            return

        last_signal = sym_state.get("last_signal")
        if last_signal == signal:
            LOG.info("Duplicate %s signal for %s ignored", signal, symbol)
            return

        # send alert
        if signal == "buy":
            self.telegram.send_buy(symbol, self.config.timeframe, price, ts)
        elif signal == "sell":
            self.telegram.send_sell(symbol, self.config.timeframe, price, ts)

        LOG.info("Sent %s alert for %s at %s price=%s", signal, symbol, ts, price)
        self.state.update_symbol(symbol, last_signal=signal, last_alert=str(datetime.utcnow()))
