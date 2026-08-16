from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .providers import (
    fetch_finnhub_eps_estimate,
    fetch_finnhub_price_target,
    fetch_marketscreener_consensus,
    fetch_marketscreener_technical,
)


ROOT = Path(__file__).resolve().parents[1]

VALUATION_FILE = (
    ROOT
    / "data"
    / "valuations.json"
)


def load_valuations() -> dict:
    if not VALUATION_FILE.exists():
        return {}

    try:
        return json.loads(
            VALUATION_FILE.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return {}


def save_valuations(
    data: dict,
) -> None:

    VALUATION_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    VALUATION_FILE.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _fallback_value(
    meta: dict,
) -> dict:

    fallback = meta.get(
        "fallback",
        {},
    )

    return {
        "fair_value": fallback.get(
            "fair_value"
        ),
        "buy": fallback.get(
            "buy",
            {},
        ),
        "sell": fallback.get(
            "sell",
            {},
        ),
        "source": "fallback",
    }


def build_valuation(
    symbol: str,
    meta: dict,
    cfg: dict,
) -> dict[str, Any]:

    market = str(
        meta.get(
            "market",
            "",
        )
    ).upper()

    valuation = meta.get(
        "valuation",
        {},
    )

    method = valuation.get(
        "method",
        "fallback",
    )

    # ========================================================
    # US
    # ========================================================

    if (
        market == "US"
        and method == "analyst"
    ):

        token = (
            cfg
            .get("finnhub", {})
            .get("token", "")
        )

        try:

            target = (
                fetch_finnhub_price_target(
                    symbol,
                    token,
                )
            )

            target_price = (
                target.get(
                    "targetMean"
                )
            )

            if target_price is not None:

                return build_from_fair_value(
                    float(target_price),
                    meta,
                    source="finnhub",
                    extra={
                        "target_high":
                            target.get(
                                "targetHigh"
                            ),
                        "target_low":
                            target.get(
                                "targetLow"
                            ),
                        "last_updated":
                            target.get(
                                "lastUpdated"
                            ),
                    },
                )

        except Exception as exc:

            print(
                f"[valuation] "
                f"{symbol} Finnhub target failed: "
                f"{exc}"
            )

    # ========================================================
    # HK
    # ========================================================

    if (
        market == "HK"
        and method == "marketscreener"
    ):

        technical_url = (
            valuation.get(
                "technical_url"
            )
        )

        consensus_url = (
            valuation.get(
                "consensus_url"
            )
        )

        cached = {}

        try:

            if consensus_url:

                cached.update(
                    fetch_marketscreener_consensus(
                        consensus_url
                    )
                )

        except Exception as exc:

            print(
                f"[valuation] "
                f"{symbol} MarketScreener "
                f"consensus failed: {exc}"
            )

        try:

            if technical_url:

                cached["technical"] = (
                    fetch_marketscreener_technical(
                        technical_url
                    )
                )

        except Exception as exc:

            print(
                f"[valuation] "
                f"{symbol} MarketScreener "
                f"technical failed: {exc}"
            )

        target = cached.get(
            "average_target"
        )

        if target:

            result = build_from_fair_value(
                float(target),
                meta,
                source="marketscreener",
                extra=cached,
            )

            return result

    # ========================================================
    # Fallback
    # ========================================================

    return _fallback_value(
        meta
    )


def build_from_fair_value(
    fair_value: float,
    meta: dict,
    source: str,
    extra: dict | None = None,
) -> dict:

    valuation = meta.get(
        "valuation",
        {},
    )

    buy_cfg = valuation.get(
        "buy_margin",
        {
            "normal": 0.90,
            "strong": 0.85,
            "extreme": 0.78,
        },
    )

    sell_cfg = valuation.get(
        "sell_multiple",
        {
            "take_profit": 1.15,
            "reduce": 1.25,
        },
    )

    result = {
        "fair_value": fair_value,

        "buy": {
            "normal":
                fair_value
                * float(
                    buy_cfg.get(
                        "normal",
                        0.90,
                    )
                ),

            "strong":
                fair_value
                * float(
                    buy_cfg.get(
                        "strong",
                        0.85,
                    )
                ),

            "extreme":
                fair_value
                * float(
                    buy_cfg.get(
                        "extreme",
                        0.78,
                    )
                ),
        },

        "sell": {
            "take_profit":
                fair_value
                * float(
                    sell_cfg.get(
                        "take_profit",
                        1.15,
                    )
                ),

            "reduce":
                fair_value
                * float(
                    sell_cfg.get(
                        "reduce",
                        1.25,
                    )
                ),
        },

        "source": source,
    }

    if extra:
        result.update(extra)

    return result


def refresh_all_valuations(
    cfg: dict,
) -> dict:

    current = load_valuations()

    new_data = {}

    for symbol, meta in (
        cfg["symbols"].items()
    ):

        try:

            result = build_valuation(
                symbol,
                meta,
                cfg,
            )

            new_data[symbol] = result

        except Exception as exc:

            print(
                f"[valuation] "
                f"{symbol} failed: {exc}"
            )

            # 失败不覆盖上一次有效数据
            if symbol in current:

                new_data[symbol] = (
                    current[symbol]
                )

            else:

                new_data[symbol] = (
                    _fallback_value(meta)
                )

    save_valuations(
        new_data
    )

    return new_data
