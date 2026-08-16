from __future__ import annotations


def classify_price(price: float | None, valuation: dict) -> tuple[str, str]:
    if price is None:
        return "UNKNOWN", "⚪"
    if price <= valuation["buy_extreme"]:
        return "EXTREME_BUY", "🔥"
    if price <= valuation["buy_strong"]:
        return "STRONG_BUY", "🟢"
    if price <= valuation["buy_normal"]:
        return "BUY", "🟢"
    if price >= valuation["reduce"]:
        return "REDUCE", "🔴"
    if price >= valuation["take_profit"]:
        return "TAKE_PROFIT", "🟠"
    return "HOLD", "🟡"


def premium_state(premium: float | None, meta: dict) -> tuple[str, str]:
    if premium is None:
        return "UNKNOWN", "⚪"
    t = meta.get("premium_thresholds", {})
    if premium >= t.get("extreme", 0.10):
        return "EXTREME", "🚨"
    if premium >= t.get("very_high", 0.08):
        return "VERY_HIGH", "🔴"
    if premium >= t.get("high", 0.05):
        return "HIGH", "🟠"
    return "NORMAL", "🟢"
