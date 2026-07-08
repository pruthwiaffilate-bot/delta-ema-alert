"""Configuration loader for delta-ema-alert."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv


@dataclass
class Config:
    telegram_token: str
    chat_id: str
    check_interval: int
    timeframe: str
    symbols: List[str]


def load_config(env_path: str | None = None) -> Config:
    """Load configuration from environment or .env file.

    Args:
        env_path: optional path to .env file

    Returns:
        Config
    """
    load_dotenv(dotenv_path=env_path)

    telegram_token = os.getenv("TELEGRAM_TOKEN", "").strip()
    chat_id = os.getenv("CHAT_ID", "").strip()
    if not telegram_token or not chat_id:
        raise ValueError("Missing TELEGRAM_TOKEN or CHAT_ID in environment")

    check_interval = int(os.getenv("CHECK_INTERVAL", "60"))
    timeframe = os.getenv("TIMEFRAME", "1h")
    symbols_raw = os.getenv("SYMBOLS", "ETHUSDT,BTCUSDT,SOLUSDT,XRPUSDT")
    symbols = [s.strip().upper() for s in symbols_raw.split(",") if s.strip()]

    return Config(
        telegram_token=telegram_token,
        chat_id=chat_id,
        check_interval=check_interval,
        timeframe=timeframe,
        symbols=symbols,
    )
