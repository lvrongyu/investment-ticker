#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path.home() / "investment_ticker"
STATE = ROOT / "data" / "state.json"

if not STATE.exists():
    print("📈 Ticker")
    print("---")
    print("state.json not found")
    raise SystemExit

state = json.loads(STATE.read_text(encoding="utf-8"))
vals = state.get("valuations", {})
print("📈 Ticker")
print("---")
for symbol, v in vals.items():
    fair = v.get("fair_value")
    if fair:
        print(f"{symbol}  Fair {fair:.2f} | Buy {v.get('buy_normal',0):.2f} | Strong {v.get('buy_strong',0):.2f}")
