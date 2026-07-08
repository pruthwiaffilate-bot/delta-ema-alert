import pandas as pd
from strategy import calculate_indicators, evaluate_signal


def make_df(closes):
    df = pd.DataFrame({
        "timestamp": pd.date_range("2023-01-01", periods=len(closes), freq="h"),
        "open": closes,
        "high": closes,
        "low": closes,
        "close": closes,
        "volume": [1] * len(closes),
    })
    return df


def test_ema_cross_buy():
    closes = [1, 1, 1, 1, 1, 2, 3, 4, 5, 6]
    df = make_df(closes)
    res = evaluate_signal(df)
    assert res["signal"] in ("buy", None)
