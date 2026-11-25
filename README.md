# The World in One Day — Wednesday 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Bruskots/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Bruskots/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A program that draws one newspaper-style poster summing up the world's news of **Wednesday 25 November 2026** — seven stories from every region — and writes it to `/output/entry.png`.

## The day in the poster

1. **US spy agencies hit by cyberattack** — CNN reports the CIA and the Office of the Director of National Intelligence were breached, with unclassified information compromised.
2. **First Pakistani reaches orbit** — Muhammad Zeeshan Ali flies aboard China's Shenzhou-24 to the Tiangong station, the first Pakistani in space.
3. **Drone hits Riyadh tower** — a Houthi drone hits the capital's tallest tower, wounding 11 people.
4. **Ukraine hits Russian ships** — Kyiv hits a Russian cargo ship in the Gulf of Finland and sinks a warship off Libya.
5. **Ebola teams pulled from fighting** — health workers leave a hospital in Ituri, DR Congo, after three days of fighting at the centre of the Ebola outbreak.
6. **NATO sends warning jets to Poland** — the alliance plans surveillance flights after missiles land in Poland.
7. **Earliest quasar ever seen found** — astronomers find a quasar from 630 million years after the Big Bang.

## How it works

`main.py` (Python 3, standard library only) draws a 1024×1024 infographic poster: a navy masthead naming the day, a lead story with a globe pictogram, a six-story grid with a small drawn icon per story, and a sources footer.

- The PNG is encoded by hand (zlib + struct) and the text is rendered with a small built-in 5×7 bitmap font, so the program runs in a standard-library-only sandbox with no network and no installed packages.
- Fully deterministic: two runs produce byte-identical PNGs.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Then check `out/entry.png`: 1024×1024, at most 1 MiB, and identical across runs.

## License

MIT — see [LICENSE](LICENSE).
