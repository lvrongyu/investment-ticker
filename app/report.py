from __future__ import annotations

from datetime import datetime

from .providers import (
    get_quote,
    etf_spot,
)


def classify_signal(
    price,
    valuation,
):

    if price is None:
        return "⚪ 无价格"


    buy = valuation.get(
        "buy",
        {}
    )

    sell = valuation.get(
        "sell",
        {} 
    )


    if buy.get(
        "extreme"
    ) and price <= buy["extreme"]:

        return "🟢 极限买入"


    if buy.get(
        "strong"
    ) and price <= buy["strong"]:

        return "🟢 强买"


    if buy.get(
        "normal"
    ) and price <= buy["normal"]:

        return "🟡 关注"


    if sell.get(
        "take_profit"
    ) and price >= sell["take_profit"]:

        return "🔴 止盈"


    if sell.get(
        "reduce"
    ) and price >= sell["reduce"]:

        return "🟠 减仓"


    return "⚪ 持有"



def build_snapshot(
    cfg,
    valuations,
):

    rows = []

    etfs = []


    for symbol, meta in cfg["symbols"].items():

        market = meta.get(
            "market",
            "",
        )


        # ======================
        # ETF
        # ======================

        if market == "ETF":

            result = etf_spot(
                symbol,
                meta.get(
                    "name",
                    symbol,
                ),
            )

            etfs.append(
                result
            )

            continue



        quote = get_quote(
            symbol,
            market,
        )


        valuation = valuations.get(
            symbol,
            {},
        )


        rows.append(
            {
                "symbol": symbol,

                "name": meta.get(
                    "name",
                    symbol,
                ),

                "market": market,

                "price": quote.price,

                "change_pct":
                    quote.change_pct,

                "source":
                    quote.source,

                "signal":
                    classify_signal(
                        quote.price,
                        valuation,
                    ),

                "valuation":
                    valuation,

                "error":
                    quote.error,

            }
        )


    return rows, etfs



def format_report_text(
    cfg,
    rows,
    etfs,
    title,
):

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )


    lines = []

    lines.append(
        f"{title} | {now}"
    )

    lines.append(
        ""
    )


    lines.append(
        "🇺🇸🇭🇰 股票监控"
    )


    for row in rows:

        lines.append(
            (
                f"{row['symbol']} "
                f"{row['price']} "
                f"{row['signal']} "
                f"({row['source']})"
            )
        )


    lines.append(
        ""
    )

    lines.append(
        "🇨🇳 ETF溢价"
    )


    for etf in etfs:

        premium = etf.get(
            "premium"
        )


        if premium is not None:

            premium = (
                f"{premium*100:.2f}%"
            )


        lines.append(
            (
                f"{etf['code']} "
                f"{etf.get('price')} "
                f"溢价 {premium}"
            )
        )


    return "\n".join(
        lines
    )



def format_report_html(
    cfg,
    rows,
    etfs,
    title,
):

    html = []

    html.append(
        f"<h2>{title}</h2>"
    )


    html.append(
        "<h3>🇺🇸🇭🇰 股票监控</h3>"
    )


    for row in rows:

        html.append(
            (
                f"<p>"
                f"<b>{row['symbol']}</b> "
                f"{row['price']} "
                f"{row['signal']}"
                f"</p>"
            )
        )


    html.append(
        "<h3>🇨🇳 ETF</h3>"
    )


    for etf in etfs:

        premium = etf.get(
            "premium"
        )

        if premium is not None:
            premium = (
                f"{premium*100:.2f}%"
            )


        html.append(
            (
                f"<p>"
                f"{etf['code']} "
                f"{etf['price']} "
                f"溢价:{premium}"
                f"</p>"
            )
        )


    return "\n".join(
        html
    )
