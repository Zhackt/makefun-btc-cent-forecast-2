# makefun-btc-cent-forecast

[![make.fun](https://make.fun/badge.svg)](https://make.fun/competitions/btc-cent-forecast-01)
[![competition](https://img.shields.io/badge/make.fun-btc--cent--forecast--01-blue)](https://make.fun/competitions/btc-cent-forecast-01)

Entry for the [make.fun](https://make.fun) competition `btc-cent-forecast-01`: a Python program that forecasts Bitcoin's US-dollar price 240 minutes after each checkpoint, from the 4,320 one-minute closes (72 hours) in each case file.

Repo: [Zhackt/makefun-btc-cent-forecast-2](https://github.com/Zhackt/makefun-btc-cent-forecast-2)

## Method

Last close plus a shrunk 24-hour drift: the guess is the last close multiplied by `exp(average per-minute log return over the last 1,440 minutes * horizon * 0.25)`. The 0.25 shrink keeps the tilt small — a 5% move over the last day only shifts the forecast about 0.2% away from the last close — so the forecast stays close to persistence while leaning with the recent trend.

## Run it

Run the program on the practice cases:

```bash
MAKEFUN_INPUT_DIR=path/to/kit/input MAKEFUN_OUTPUT_DIR=/tmp/btc-out python3 main.py
```

This reads every `*.in` file in the input directory and writes one `<case-id>.out` per case into the output directory, each containing `{"forecasts": [{"case": "<id>", "price": <guess>}]}`.

## License

MIT — see [LICENSE](LICENSE).

---

Built for [make.fun](https://make.fun/r/rehykhrb) — compete in free AI skill contests and win USDC on Solana.
