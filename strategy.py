"""Strategy implementation: EMA calculations and signal evaluation."""
from __future__ import annotations

import pandas as pd
from typing import Optional


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate EMA9 and EMA50 and attach to DataFrame.

    Args:
        df: DataFrame with `close` column and datetime `timestamp` index/column.

    Returns:
        DataFrame with `ema9` and `ema50` columns.
    """
    df = df.copy()
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    return df


def evaluate_signal(df: pd.DataFrame) -> dict:
    """Evaluate the EMA crossover signal on the last closed candle.

    Returns a dict: {"signal": "buy"|"sell"|None, "timestamp": pd.Timestamp, "price": float}
    """
    if df.shape[0] < 2:
        return {"signal": None, "timestamp": None, "price": None}

    df = calculate_indicators(df)
    # last closed candle is the last row
    last = df.iloc[-1]
    prev = df.iloc[-2]

    signal: Optional[str] = None
    if prev["ema9"] <= prev["ema50"] and last["ema9"] > last["ema50"]:
        signal = "buy"
    elif prev["ema9"] >= prev["ema50"] and last["ema9"] < last["ema50"]:
        signal = "sell"

    return {"signal": signal, "timestamp": last["timestamp"], "price": float(last["close"]) }
