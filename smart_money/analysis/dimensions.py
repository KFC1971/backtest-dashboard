from typing import Dict, Any, List
import math
try:
    import pandas as pd  # type: ignore
except Exception:
    pd = None  # type: ignore


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _safe_score(value: float, min_val: float, max_val: float) -> float:
    try:
        if math.isnan(value) or math.isinf(value):
            return 0.0
    except Exception:
        pass
    scaled = (value - min_val) / (max_val - min_val) if max_val != min_val else 0
    return float(_clip(scaled * 100, 0, 100))


def analyze_13f_holdings(holdings: List[Dict[str, Any]]) -> float:
    # Placeholder: if we have many entries, score higher
    count = len(holdings or [])
    return _safe_score(count, 0, 50)


def analyze_insider_activity(insider: List[Dict[str, Any]]) -> float:
    # Sum positive values minus negatives; placeholder structure
    total_value = 0.0
    for row in (insider or []):
        form = str(row.get("form", ""))
        value = float(row.get("value", 0) or 0)
        # Assume form 4 positive as placeholder
        sign = 1.0 if form == "4" else 0.0
        total_value += sign * value
    return _safe_score(total_value, 0, 1_000_000)


def analyze_volume_profile(price_df) -> float:
    if price_df is None or getattr(price_df, 'empty', True) or pd is None:
        return 50.0
    vol = price_df["Volume"].fillna(0)
    ma20 = vol.rolling(20).mean()
    spikes = (vol > ma20 * 2.5).tail(30).sum()
    vol_std = float(vol.tail(60).std() or 0.0)
    vol_mean = float(vol.tail(60).mean() or 1.0)
    consistency = 1.0 - min(vol_std / max(vol_mean, 1.0), 1.0)
    spike_score = min(spikes / 10.0, 1.0)
    composite = (consistency * 0.3 + spike_score * 0.4 + 0.3) * 100
    return float(_clip(composite, 0, 100))


def analyze_technical_indicators(price_df) -> float:
    if price_df is None or getattr(price_df, 'empty', True) or pd is None:
        return 50.0
    close = price_df["Close"].astype(float)
    rsi = _compute_rsi(close, 14)
    rsi_score = 100 - abs(rsi - 55) * 2  # Favor 40-70 centered at 55
    rsi_score = float(_clip(rsi_score, 0, 100))

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_score = 50 + math.tanh(((macd - signal).iloc[-1]) / max(close.iloc[-1] * 0.01, 1e-9)) * 50

    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]
    ma200 = close.rolling(200).mean().iloc[-1]
    ma_score = 50
    if ma20 > ma50 > ma200:
        ma_score = 80
    elif ma20 < ma50 < ma200:
        ma_score = 20

    composite = rsi_score * 0.3 + float(_clip(macd_score, 0, 100)) * 0.3 + ma_score * 0.4
    return float(_clip(composite, 0, 100))


def _compute_rsi(series, window: int = 14) -> float:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0.0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window).mean()
    rs = gain.iloc[-1] / max(loss.iloc[-1], 1e-9)
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)


def analyze_sector_flows(symbol: str) -> float:
    # Without external data, assume neutral baseline
    return 50.0


def analyze_macro_environment() -> float:
    # Placeholder macro score neutral
    return 50.0


def analyze_crypto_whales(whale_data: List[Dict[str, Any]]) -> float:
    # Count large tx; more activity could signal risk-on/off; stay neutral
    count = len(whale_data or [])
    # Slightly penalize extreme activity as risk
    base = 50.0
    adj = max(min((10 - count) * 2.0, 10), -10)
    return float(_clip(base + adj, 0, 100))
