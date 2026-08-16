from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_config
from .notifier import macos_notify
from .pushplus_sender import send_pushplus
from .report import (
    build_snapshot,
    format_report_html,
    format_report_text,
)
from .valuation import build_valuation


ROOT = Path(__file__).resolve().parents[1]


def load_state(cfg):

    path = ROOT / cfg["app"]["state_file"]

    if not path.exists():
        return {}

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception:
        return {}


def save_state(
    cfg,
    state,
):

    path = ROOT / cfg["app"]["state_file"]

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            state,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def build_valuations(cfg):

    return {
        symbol: build_valuation(
            symbol,
            meta,
            cfg,
        )
        for symbol, meta
        in cfg["symbols"].items()
    }


def run(
    title: str,
    send: bool,
):

    cfg = load_config()

    # ============================
    # valuation
    # ============================

    valuations = build_valuations(
        cfg
    )


    # ============================
    # market snapshot
    # ============================

    rows, etfs = build_snapshot(
        cfg,
        valuations,
    )


    # ============================
    # report
    # ============================

    text = format_report_text(
        cfg,
        rows,
        etfs,
        title,
    )

    html = format_report_html(
        cfg,
        rows,
        etfs,
        title,
    )


    # ============================
    # state
    # ============================

    state = load_state(
        cfg
    )

    state["valuations"] = valuations
    state["latest_report"] = text

    save_state(
        cfg,
        state,
    )


    print(text)


    # ============================
    # notification
    # ============================

    if not send:
        return


    if cfg.get(
        "notifications",
        {},
    ).get(
        "macos",
        True,
    ):

        macos_notify(
            title,
            text[:240],
        )


    pcfg = cfg.get(
        "pushplus",
        {},
    )


    if pcfg.get(
        "enabled",
        False,
    ):

        result = send_pushplus(
            title,
            html[
                :pcfg.get(
                    "max_chars",
                    5000,
                )
            ],
            pcfg.get(
                "token",
                "",
            ),
            pcfg.get(
                "topic",
                "",
            ),
            pcfg.get(
                "template",
                "html",
            ),
        )

        print(
            "PushPlus:",
            result,
        )


def refresh_valuations():

    cfg = load_config()

    valuations = build_valuations(
        cfg
    )

    state = load_state(
        cfg
    )

    state["valuations"] = valuations

    save_state(
        cfg,
        state,
    )


    for symbol, value in valuations.items():

        print(
            symbol,
            "fair=",
            value.get(
                "fair_value"
            ),
            "buy=",
            value.get(
                "buy",
                {}
            ),
            "sell=",
            value.get(
                "sell",
                {}
            ),
        )



def pushplus_test():

    cfg = load_config()

    html = """
    <h3>📈 Investment Ticker</h3>

    <p>
    ✅ PushPlus 测试成功
    </p>

    <p>
    动态目标价、港股技术面、
    A股ETF溢价监控已接入。
    </p>
    """

    result = send_pushplus(
        "📈 Investment Ticker 测试",
        html,
        cfg["pushplus"].get(
            "token",
            "",
        ),
        cfg["pushplus"].get(
            "topic",
            "",
        ),
        "html",
    )

    print(result)



def main():

    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(
        dest="cmd",
        required=True,
    )


    sub.add_parser(
        "once"
    )

    sub.add_parser(
        "morning"
    )

    sub.add_parser(
        "evening"
    )

    sub.add_parser(
        "refresh-valuations"
    )

    sub.add_parser(
        "pushplus-test"
    )


    args = parser.parse_args()


    if args.cmd == "once":

        run(
            "📊 投资监控",
            False,
        )


    elif args.cmd == "morning":

        run(
            "🌅 早间投资监控",
            True,
        )


    elif args.cmd == "evening":

        run(
            "🌙 晚间投资监控",
            True,
        )


    elif args.cmd == "refresh-valuations":

        refresh_valuations()


    elif args.cmd == "pushplus-test":

        pushplus_test()



if __name__ == "__main__":
    main()
