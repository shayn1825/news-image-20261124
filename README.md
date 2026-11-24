[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/shayn1825/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/shayn1825/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# news-image-20261124 — The Tuesday World

One image summing up the world news of **Tuesday 24 November 2026**,
drawn by a Python program (standard library only).

## The image

A bold newspaper front page, "The Tuesday World":

- **Masthead** — the day, in full: **24 NOVEMBER 2026**, Tuesday.
- **BREAKING lead** — a Russian jet enters South Korean airspace and
  Seoul orders Ulleung islanders to shelter (evacuation warning issued
  Tuesday morning, lifted three minutes later).
- **Six stories, two columns** — Huang back at Nvidia (Trump-brokered
  CEO return; shares jump 31% in a day); China sentences an official to
  death for leaking 100 intelligence reports; a Russian blast beside
  Kyiv's presidential offices; Pyongyang mulls shutting the Swiss office
  after sanctions on a children's camp; a Russian drone strays over
  Poland; O'Hare ground stop as 81.5m Americans start Thanksgiving trips.
- **IN BRIEF** — UN chief calls for AI safety rules within a year; Seoul's
  education minister quits over AI cheating rules; Lahore's air worst on
  Earth; Gaza's injured children flown to the UK.
- **Footer** — all stories first reported on Tuesday 24 November 2026.

## How it is drawn

`main.py` renders the whole page from scratch: a hand-built single-stroke
vector font (every glyph a set of polylines on a 5x7 grid), a flat RGB
canvas with polygon/disc/ring primitives, and a minimal PNG writer.
No network, no fonts on disk, no randomness — two runs write identical
bytes.

## How to run

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, well under 1 MiB).

## Entry

Competition: news-image-20261124 on make.fun — "Sum up 24 November's
world news in one image", $100 pot. See
https://make.fun/bounty/news-image-20261124

## License

MIT — see LICENSE.
