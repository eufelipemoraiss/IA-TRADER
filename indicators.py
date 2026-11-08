import numpy as np


def sma(values, window):
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def ema(values, window):
    if len(values) < window:
        return None
    arr = np.array(values)
    alpha = 2 / (window + 1)
    return np.mean(arr[-window:] * alpha + np.roll(arr, 1)[-window:] * (1 - alpha))


def rsi(values, window=14):
    if len(values) < window + 1:
        return None
    deltas = np.diff(values)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-window:])
    avg_loss = np.mean(losses[-window:])
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(values, fast=12, slow=26, signal=9):
    if len(values) < slow + signal:
        return None, None, None
    ema_fast = ema(values, fast)
    ema_slow = ema(values, slow)
    if ema_fast is None or ema_slow is None:
        return None, None, None
    macd_line = ema_fast - ema_slow
    signal_line = ema(values[-signal:], signal) or 0
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger_bands(values, window=20, num_std=2):
    if len(values) < window:
        return None, None, None
    recent = values[-window:]
    middle = np.mean(recent)
    std = np.std(recent)
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower


def evaluate_all_indicators(closes, highs=None, lows=None):
    signals = []

    rsi_value = rsi(closes, 14)
    if rsi_value is not None:
        if rsi_value < 30:
            signals.append(("RSI sobrevendido (<30)", "CALL", 0.65))
        elif rsi_value > 70:
            signals.append(("RSI sobrecomprado (>70)", "PUT", 0.65))

    ema9 = ema(closes, 9)
    ema21 = ema(closes, 21)
    if ema9 is not None and ema21 is not None:
        if ema9 > ema21:
            signals.append(("EMA9 > EMA21", "CALL", 0.60))
        else:
            signals.append(("EMA9 < EMA21", "PUT", 0.60))

    macd_line, signal_line, histogram = macd(closes)
    if macd_line is not None and signal_line is not None:
        if macd_line > signal_line and histogram > 0:
            signals.append(("MACD bullish", "CALL", 0.60))
        elif macd_line < signal_line and histogram < 0:
            signals.append(("MACD bearish", "PUT", 0.60))

    upper, middle, lower = bollinger_bands(closes)
    if upper is not None and lower is not None:
        last_close = closes[-1]
        if last_close <= lower:
            signals.append(("Preço tocou banda inferior de Bollinger", "CALL", 0.60))
        elif last_close >= upper:
            signals.append(("Preço tocou banda superior de Bollinger", "PUT", 0.60))

    if len(closes) >= 20:
        recent = closes[-20:]
        if max(recent) == recent[-1]:
            signals.append(("Novo topo recente", "PUT", 0.50))
        elif min(recent) == recent[-1]:
            signals.append(("Novo fundo recente", "CALL", 0.50))

    return signals
