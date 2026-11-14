# Per-case runtime limit: 8 seconds (this program finishes in well under a second).
# BTC 4-hour price forecaster for make.fun btc-cent-forecast-01.
#
# Method: start from the last close and add a small drift tilt. The tilt comes
# from the average per-minute log return over the last 24 hours (1,440
# minutes), stretched out over the forecast horizon and shrunk by a factor of
# 0.25 so a single day's move only nudges the guess a little. In a falling
# market the guess lands slightly below the last close; in a rising market,
# slightly above it. If the series is too short or unusable, fall back to the
# plain last close (persistence). Everything is standard library only and
# each case runs in a fraction of a second, far under the 8 second limit.
#
# Usage: MAKEFUN_INPUT_DIR=<dir with *.in files> MAKEFUN_OUTPUT_DIR=<dir>
#        python3 main.py
# Output: one <case-id>.out per case, {"forecasts": [{"case": id,
#         "price": guess}]}.

import json
import math
import os
import sys

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input/")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output/")
WINDOW_MINUTES = 1440          # look back 24 hours of one-minute closes
SHRINK = 0.25                  # shrink the extrapolated drift by 75%
MAX_PRICE = 10_000_000         # hard guard: guess must stay below this


def valid_prices(raw):
    """Keep only finite positive numbers, in order, as floats."""
    out = []
    for p in raw or []:
        try:
            value = float(p)
        except (TypeError, ValueError):
            continue
        if math.isfinite(value) and value > 0:
            out.append(value)
    return out


def forecast(prices, horizon_minutes):
    """Forecast the price horizon_minutes ahead from a list of closes."""
    if not prices:
        return None
    last = prices[-1]
    guess = last
    if len(prices) >= 2 and horizon_minutes and horizon_minutes > 0:
        # Use up to the last WINDOW_MINUTES intervals of the series.
        steps = min(WINDOW_MINUTES, len(prices) - 1)
        earlier = prices[-1 - steps]
        if earlier > 0:
            avg_per_minute_log_return = (
                math.log(last) - math.log(earlier)
            ) / steps
            drift = avg_per_minute_log_return * horizon_minutes * SHRINK
            candidate = last * math.exp(drift)
            if math.isfinite(candidate) and candidate > 0:
                guess = candidate
    if not (math.isfinite(guess) and guess > 0):
        guess = last
    if guess >= MAX_PRICE:
        guess = last if last < MAX_PRICE else MAX_PRICE - 0.01
    return round(guess, 2)


def process_case(path):
    """Read one .in file, return (case_id, guess) or None to skip it."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    case_id = data.get("case")
    if not isinstance(case_id, str) or not case_id:
        case_id = os.path.splitext(os.path.basename(path))[0]
    horizon = data.get("horizon_minutes", 240)
    try:
        horizon = int(horizon)
    except (TypeError, ValueError):
        horizon = 240
    markets = data.get("markets") or []
    raw_prices = []
    if markets and isinstance(markets[0], dict):
        raw_prices = markets[0].get("prices") or []
    prices = valid_prices(raw_prices)
    guess = forecast(prices, horizon)
    if guess is None:
        return None
    return case_id, guess


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        names = sorted(os.listdir(INPUT_DIR))
    except OSError as exc:
        print(f"cannot list input directory {INPUT_DIR}: {exc}",
              file=sys.stderr)
        return 1
    for name in names:
        if not name.endswith(".in"):
            continue
        path = os.path.join(INPUT_DIR, name)
        if not os.path.isfile(path):
            continue
        try:
            result = process_case(path)
        except Exception as exc:  # keep one bad case from killing the run
            print(f"skipping {name}: {exc}", file=sys.stderr)
            continue
        if result is None:
            print(f"skipping {name}: no usable price", file=sys.stderr)
            continue
        case_id, guess = result
        out_path = os.path.join(OUTPUT_DIR, f"{case_id}.out")
        payload = {"forecasts": [{"case": case_id, "price": guess}]}
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
            fh.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
