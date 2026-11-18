# news-image-20261118 — round 2 entry

[![make.fun bounty](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/besan11/news-image-20261118-r2/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/besan11/news-image-20261118-r2/reward.svg)](https://make.fun/bounty/news-image-20261118)

Entry for the [make.fun bounty "Sum up 18 November's world news in one image"](https://make.fun/bounty/news-image-20261118) — a one-page newspaper front page for Wednesday 18 November 2026: **36 stories, six continents**, drawn from scratch.

## What the image shows

- **Masthead** — "THE WORLD TODAY", dated Wednesday 18 November 2026.
- **Lead** — the Gulf strikes: US jets hit a Revolutionary Guard missile site on Qeshm Island; Iran fired drones at Bahrain and Kuwait and shot down a US MQ-9 drone near the Strait of Hormuz. Drawn scene, no photos.
- **Second row** — Kerch Bridge hit again, the Xi–Putin APEC opening in Shenzhen, the Alaska Senate flip (Democrats 56–44), and Nvidia's $115.8B quarter.
- **World map** — hand-drawn continent outlines with numbered markers for the 8 lead stories, plus a Voyager 1 box (one light-day out).
- **28 more stories** in a labelled grid (conflict, politics, economy, science, culture), a markets strip, and an in-brief strip with 10 more items.

Every fact and number on the page comes from the day's reporting; nothing is invented. All illustrations and the map are drawn by the program itself — no external images.

## Files

- `entry.png` — the rendered 1024×1024 front page (≤1 MiB).
- `render.py` — the program that draws it (Pillow, deterministic: two runs produce byte-identical output).
- `main.ts` — copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`).

## Run it

```sh
python3 render.py          # redraw entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # copy it to out/entry.png
```

## License

MIT — see [LICENSE](LICENSE).
