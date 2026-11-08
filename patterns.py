def body_size(c):
    return abs(c["close"] - c["open"])


def total_range(c):
    return c["high"] - c["low"]


def is_bullish(c):
    return c["close"] > c["open"]


def is_bearish(c):
    return c["close"] < c["open"]


def detect_all_patterns(ohlc_list):
    if len(ohlc_list) < 5:
        return []

    patterns = []
    c0, c1, c2, c3, c4 = ohlc_list[-1], ohlc_list[-2], ohlc_list[-3], ohlc_list[-4], ohlc_list[-5]

    patterns += _doji(c0)
    patterns += _hammer(c0)
    patterns += _inverted_hammer(c0)
    patterns += _spinning_top(c0)
    patterns += _marubozu(c0)
    patterns += _shooting_star(c0, c1)
    patterns += _engulfing(c0, c1)
    patterns += _harami(c0, c1)
    patterns += _piercing_line(c0, c1)
    patterns += _dark_cloud_cover(c0, c1)
    patterns += _tweezer_tops_bottoms(c0, c1)
    patterns += _morning_star(c0, c1, c2)
    patterns += _evening_star(c0, c1, c2)
    patterns += _three_white_soldiers(c0, c1, c2)
    patterns += _three_black_crows(c0, c1, c2)
    patterns += _three_inside_up_down(c0, c1, c2)

    # Tendência de curto prazo
    closes = [c["close"] for c in ohlc_list[-10:]]
    if len(closes) >= 10:
        if all(closes[i] > closes[i - 1] for i in range(1, 5)):
            patterns.append(("Tendência de Alta Curta", "CALL", 0.55))
        elif all(closes[i] < closes[i - 1] for i in range(1, 5)):
            patterns.append(("Tendência de Baixa Curta", "PUT", 0.55))

    return patterns


def _doji(c):
    tr = total_range(c)
    if tr == 0:
        return []
    body = body_size(c)
    if body / tr < 0.05:
        return [("Doji", "NEUTRO", 0.5)]
    return []


def _hammer(c):
    body = body_size(c)
    if body == 0:
        return []
    upper = c["high"] - max(c["open"], c["close"])
    lower = min(c["open"], c["close"]) - c["low"]
    if lower >= 2 * body and upper < body * 0.5:
        if is_bullish(c):
            return [("Martelo de Alta", "CALL", 0.65)]
        return [("Martelo de Baixa", "PUT", 0.60)]
    return []


def _inverted_hammer(c):
    body = body_size(c)
    if body == 0:
        return []
    upper = c["high"] - max(c["open"], c["close"])
    lower = min(c["open"], c["close"]) - c["low"]
    if upper >= 2 * body and lower < body * 0.5:
        if is_bullish(c):
            return [("Martelo Invertido de Alta", "CALL", 0.60)]
        return [("Estrela Cadente", "PUT", 0.65)]
    return []


def _spinning_top(c):
    body = body_size(c)
    tr = total_range(c)
    if tr == 0:
        return []
    upper = c["high"] - max(c["open"], c["close"])
    lower = min(c["open"], c["close"]) - c["low"]
    if body / tr < 0.3 and upper > body and lower > body:
        return [("Spinning Top", "NEUTRO", 0.5)]
    return []


def _marubozu(c):
    body = body_size(c)
    tr = total_range(c)
    if tr == 0:
        return []
    upper = c["high"] - max(c["open"], c["close"])
    lower = min(c["open"], c["close"]) - c["low"]
    if upper / tr < 0.05 and lower / tr < 0.05:
        if is_bullish(c):
            return [("Marubozu de Alta", "CALL", 0.70)]
        return [("Marubozu de Baixa", "PUT", 0.70)]
    return []


def _shooting_star(c0, c1):
    if not is_bearish(c0) or not is_bullish(c1):
        return []
    body = body_size(c0)
    if body == 0:
        return []
    upper = c0["high"] - max(c0["open"], c0["close"])
    lower = min(c0["open"], c0["close"]) - c0["low"]
    if upper >= 2 * body and lower < body * 0.5 and c0["open"] > c1["close"]:
        return [("Estrela Cadente Confirmada", "PUT", 0.70)]
    return []


def _engulfing(c0, c1):
    b0, b1 = body_size(c0), body_size(c1)
    if b1 == 0:
        return []
    if is_bullish(c0) and is_bearish(c1):
        if c0["open"] <= c1["close"] and c0["close"] >= c1["open"] and b0 > b1:
            return [("Engolfo de Alta", "CALL", 0.75)]
    if is_bearish(c0) and is_bullish(c1):
        if c0["open"] >= c1["close"] and c0["close"] <= c1["open"] and b0 > b1:
            return [("Engolfo de Baixa", "PUT", 0.75)]
    return []


def _harami(c0, c1):
    b0, b1 = body_size(c0), body_size(c1)
    if b0 == 0:
        return []
    if is_bullish(c0) and is_bearish(c1):
        if c0["open"] > c1["close"] and c0["close"] < c1["open"]:
            return [("Harami de Alta", "CALL", 0.65)]
    if is_bearish(c0) and is_bullish(c1):
        if c0["open"] < c1["close"] and c0["close"] > c1["open"]:
            return [("Harami de Baixa", "PUT", 0.65)]
    return []


def _piercing_line(c0, c1):
    if not is_bullish(c0) or not is_bearish(c1):
        return []
    mid = (c1["open"] + c1["close"]) / 2
    if c0["open"] < c1["low"] and c0["close"] > mid:
        return [("Linha de Perfuração", "CALL", 0.70)]
    return []


def _dark_cloud_cover(c0, c1):
    if not is_bearish(c0) or not is_bullish(c1):
        return []
    mid = (c1["open"] + c1["close"]) / 2
    if c0["open"] > c1["high"] and c0["close"] < mid:
        return [("Nuvem Negra", "PUT", 0.70)]
    return []


def _tweezer_tops_bottoms(c0, c1):
    if is_bearish(c0) and is_bullish(c1):
        if abs(c0["high"] - c1["high"]) < body_size(c0) * 0.2:
            return [("Tweezer Top", "PUT", 0.65)]
    if is_bullish(c0) and is_bearish(c1):
        if abs(c0["low"] - c1["low"]) < body_size(c0) * 0.2:
            return [("Tweezer Bottom", "CALL", 0.65)]
    return []


def _morning_star(c0, c1, c2):
    if not is_bullish(c0) or not is_bearish(c2):
        return []
    b1 = body_size(c1)
    if b1 < body_size(c2) * 0.5 and c0["close"] > (c2["open"] + c2["close"]) / 2:
        return [("Estrela da Manhã", "CALL", 0.75)]
    return []


def _evening_star(c0, c1, c2):
    if not is_bearish(c0) or not is_bullish(c2):
        return []
    b1 = body_size(c1)
    if b1 < body_size(c2) * 0.5 and c0["close"] < (c2["open"] + c2["close"]) / 2:
        return [("Estrela da Noite", "PUT", 0.75)]
    return []


def _three_white_soldiers(c0, c1, c2):
    if is_bullish(c0) and is_bullish(c1) and is_bullish(c2):
        if c0["close"] > c1["close"] > c2["close"]:
            return [("Três Soldados Brancos", "CALL", 0.75)]
    return []


def _three_black_crows(c0, c1, c2):
    if is_bearish(c0) and is_bearish(c1) and is_bearish(c2):
        if c0["close"] < c1["close"] < c2["close"]:
            return [("Três Corvos Negros", "PUT", 0.75)]
    return []


def _three_inside_up_down(c0, c1, c2):
    if is_bullish(c0) and is_bearish(c1) and is_bearish(c2):
        if c0["close"] > c1["open"] and c1["open"] > c1["close"] > c2["close"]:
            return [("Three Inside Up", "CALL", 0.70)]
    if is_bearish(c0) and is_bullish(c1) and is_bullish(c2):
        if c0["close"] < c1["open"] and c1["open"] < c1["close"] < c2["close"]:
            return [("Three Inside Down", "PUT", 0.70)]
    return []
