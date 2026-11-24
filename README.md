# the-world-today

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/nmlyz/the-world-today/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/nmlyz/the-world-today/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A single-file Python program that draws a newspaper front page summing up the world news of Tuesday 24 November 2026 — the Ukrainian sea drone sinking a Russian corvette at Benghazi, three more ships hit in the Strait of Hormuz, EU sanctions aimed at 60 Russian banks, the Democrats taking 258 House seats, aid workers killed in Gaza, drones striking Khartoum again, the student marches sweeping Europe, and Seoul naming new top diplomats — as one 1024x1024 PNG, drawn entirely with code (a hand-made bitmap font, no external assets) using only the Python standard library.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program writes `entry.png` to the output directory. It uses no network and is fully deterministic: every run produces the same bytes.
