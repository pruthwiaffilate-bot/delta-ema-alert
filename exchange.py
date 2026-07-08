"""Exchange client using ccxt to fetch OHLCV and convert to DataFrame."""
from __future__ import annotations

import ccxt
import pandas as pd
from typing import List
from utils import retry


class DeltaExchangeClient:
    """Minimal Delta Exchange client for public market data."""

    def __init__(self):
        if not hasattr(ccxt, "delta"):
            # Some ccxt builds may use 'delta' or 'deltaexchange'
            ex_id = "delta"
        else:
            ex_id = "delta"
        self.exchange = getattr(ccxt, ex_id)({"enableRateLimit": True})

    @retry(max_attempts=4, delay=1.0, backoff=2.0)
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
        """Fetch OHLCV candle data and return a pandas DataFrame.

        Columns: timestamp, open, high, low, close, volume
        Timestamp is in milliseconds since epoch.
        """
        raw = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"]) 
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
