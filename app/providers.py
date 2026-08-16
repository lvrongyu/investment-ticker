from __future__ import annotations

import json
import os
import socket
import time

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
import yfinance as yf


ROOT = Path(__file__).resolve().parents[1]

STATE_FILE = (
    ROOT /
    "data" /
    "state.json"
)


@dataclass
class Quote:

    price: float | None

    change_pct: float | None

    source: str

    error: str | None = None



# =========================================================
# state
# =========================================================


def load_state():

    try:

        if STATE_FILE.exists():

            return json.loads(
                STATE_FILE.read_text(
                    encoding="utf-8"
                )
            )

    except Exception:

        pass


    return {}



def save_state(
    state
):

    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    STATE_FILE.write_text(
        json.dumps(
            state,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )



# =========================================================
# utils
# =========================================================


def to_float(
    value: Any
):

    try:

        if value is None:
            return None


        if isinstance(
            value,
            str
        ):

            value = (
                value
                .replace(",","")
                .replace("%","")
                .strip()
            )


        return float(value)


    except Exception:

        return None



# =========================================================
# Finnhub
# =========================================================


def finnhub_quote(
    symbol:str,
    token:str|None=None,
):


    token = (
        token
        or os.getenv(
            "FINNHUB_TOKEN",
            ""
        )
    )


    if not token:

        raise RuntimeError(
            "FINNHUB_TOKEN missing"
        )



    last_error=None



    for retry in range(3):

        try:

            r=requests.get(

                "https://finnhub.io/api/v1/quote",

                params={

                    "symbol":symbol,

                    "token":token,

                },

                timeout=10,

            )


            r.raise_for_status()


            data=r.json()


            price=to_float(
                data.get("c")
            )


            previous=to_float(
                data.get("pc")
            )


            if price is None:

                raise RuntimeError(
                    str(data)
                )



            change=None


            if previous:

                change=(
                    price /
                    previous -
                    1
                )*100



            return Quote(

                price=price,

                change_pct=change,

                source="finnhub",

            )


        except Exception as e:


            last_error=e

            time.sleep(2)



    raise RuntimeError(
        f"Finnhub failed {last_error}"
    )



# =========================================================
# Yahoo fallback
# =========================================================


def yahoo_quote(
    symbol:str
):


    socket.setdefaulttimeout(
        5
    )


    ticker=yf.Ticker(
        symbol
    )


    hist=ticker.history(

        period="5d",

        interval="1d",

        timeout=5,

        auto_adjust=False,

    )


    if hist.empty:

        raise RuntimeError(
            "Yahoo empty"
        )


    close=hist["Close"].dropna()


    price=float(
        close.iloc[-1]
    )


    change=None


    if len(close)>1:

        old=float(
            close.iloc[-2]
        )


        if old:

            change=(
                price /
                old -
                1
            )*100



    return Quote(

        price=price,

        change_pct=change,

        source="yahoo",

    )



# =========================================================
# HK stock AKShare
# =========================================================


def akshare_hk_quote(
    symbol:str
):


    import akshare as ak



    code=(
        symbol
        .replace(
            ".HK",
            ""
        )
    )


    df=ak.stock_hk_spot_em()



    row=df[

        df["代码"]
        .astype(str)
        ==
        code

    ]



    if row.empty:

        raise RuntimeError(
            f"{symbol} not found"
        )


    price=to_float(
        row.iloc[0]["最新价"]
    )


    change=to_float(
        row.iloc[0]["涨跌幅"]
    )



    return Quote(

        price=price,

        change_pct=change,

        source="akshare_hk",

    )



# =========================================================
# unified quote
# =========================================================


def get_quote(
    symbol:str,
    market:str,
):


    state=load_state()


    errors=[]


    market=market.upper()



    quote=None



    if market=="US":


        try:

            quote=finnhub_quote(
                symbol
            )


        except Exception as e:

            errors.append(
                str(e)
            )



            try:

                quote=yahoo_quote(
                    symbol
                )


            except Exception as e:

                errors.append(
                    str(e)
                )



    elif market=="HK":


        try:

            quote=akshare_hk_quote(
                symbol
            )


        except Exception as e:

            errors.append(
                str(e)
            )



    if quote:


        state.setdefault(
            "quotes",
            {}
        )[symbol]={

            "price":
                quote.price,

            "change_pct":
                quote.change_pct,

            "source":
                quote.source,

        }


        save_state(
            state
        )


        return quote



    cache=(
        state
        .get(
            "quotes",
            {}
        )
        .get(
            symbol
        )
    )


    if cache:


        return Quote(

            price=cache.get(
                "price"
            ),

            change_pct=cache.get(
                "change_pct"
            ),

            source="cache",

            error=";".join(errors),

        )



    return Quote(

        price=None,

        change_pct=None,

        source="unavailable",

        error=";".join(errors),

    )



# =========================================================
# ETF
# =========================================================


def etf_spot(
    code:str,
    name:str=""
):


    import akshare as ak


    code=str(code).zfill(6)



    df=ak.fund_etf_spot_em()



    row=df[

        df["代码"]
        .astype(str)
        .str.zfill(6)
        ==
        code

    ]



    if row.empty:

        return {

            "code":code,

            "name":name,

            "price":None,

            "iopv":None,

            "premium":None,

        }



    r=row.iloc[0]


    price=to_float(
        r.get(
            "最新价"
        )
    )


    iopv=to_float(
        r.get(
            "IOPV实时估值"
        )
    )



    premium=None


    if price and iopv:

        premium=(
            price/iopv-1
        )



    return {

        "code":code,

        "name":
            name
            or r.get(
                "名称"
            ),

        "price":price,

        "iopv":iopv,

        "premium":premium,

        "source":
            "akshare",

    }
