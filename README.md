# Investment Ticker — final architecture

## What is dynamic?

- Market price: fetched from Yahoo Finance / AKShare whenever the report runs.
- US analyst target: daily via Finnhub when configured and licensed; otherwise fallback target remains cached/configured.
- HK analyst target + technical supports/resistances: daily via MarketScreener pages.
- A-share ETF premium: realtime price/IOPV from AKShare and calculated locally.
- Buy/sell levels are **derived from the latest target/technical data**, not manually hardcoded in the alert engine.

For Hong Kong stocks, MarketScreener technical analysis exposes short/mid/long-term trend, support and resistance; the code uses these as a technical confirmation layer rather than pretending support is intrinsic value. MarketScreener also publishes consensus target-price pages for covered names.

## Install

```bash
cd ~/investment_ticker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp secrets/pushplus.env.example secrets/pushplus.env
chmod 600 secrets/pushplus.env
```

Fill `secrets/pushplus.env`:

```text
PUSHPLUS_TOKEN=...
PUSHPLUS_TOPIC=...
FINNHUB_TOKEN=...
```

## Test

```bash
source .venv/bin/activate
python -m app.cli once
python -m app.cli refresh-valuations
python -m app.cli pushplus-test
python -m app.cli morning
```

## Daily schedule

- 21:00 refresh valuation targets/MarketScreener technical data
- 09:20 morning report
- 21:30 evening report

`install_launchd.sh` replaces the current username automatically when installing the plist files.

## Notes

Finnhub's Price Target and EPS Estimates are premium estimates endpoints; without the corresponding estimates entitlement the code falls back cleanly. MarketScreener is scraped once per day only, not intraday.
