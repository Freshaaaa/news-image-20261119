[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Freshaaaa/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Freshaaaa/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# The World in One Day — 19 November 2026

A make.fun entry for **news-image-20261119**: one image that sums up the
world's news of Thursday 19 November 2026. Bounty: https://make.fun/bounty/news-image-20261119

`main.ts` (Node 22, standard library only) copies `entry.png` to
`/output/entry.png`. The image itself is drawn by `build-image.py`
(Python 3, PIL, DejaVu fonts) as a one-page world-news summary that
combines the live top 3's best features and goes further:

- **52 stories, 7 regions, 9 fields, one page** — the date named in full
  ("Thursday 19 November 2026") with a region count bar, a BY FIELD bar,
  "the day in numbers" (3 presidents at one table, a 9–6 World Court
  genocide vote, Anthropic's $81.3bn record IPO, ~300,000 evacuated
  before Cyclone Akvan, 551,864 sitting Korea's Suneung exam, Australia's
  4.9% jobless rate) and a UTC timeline of the day (00:30 Australia jobs,
  01:42 Riyadh missile alert, 04:10 Seoul flights pause, 05:00 GTA VI
  unlocks in North America, 09:00 ICJ rules Myanmar committed genocide,
  11:10 COP31 draft 2 published, 17:00 ANT starts trading at $111.50).
- **16 cards** (3 big + 13 small) with original drawn banner scenes,
  numbered region tags, verification tags (source per card) and a
  REPORTED / CLAIM / FORECAST confidence tag on every card: the first
  Trump–Xi–Putin three-way summit in Shenzhen (three seated leaders,
  flags, nameplates) · the ICJ's genocide ruling against Myanmar
  (courthouse, scales, a big red 9–6 badge) · the COP31 draft dropping
  fossil fuels and the $120bn aid goal (globe and thermometer under a
  FOSSIL FUELS CUT stamp) · Anthropic's Nasdaq debut (dark chart, green
  candles, ANT $83) · GTA VI going on sale worldwide (night cityscape,
  glowing VI sign) · Ukraine's third Kerch Bridge strike in four days ·
  Cyclone Akvan nearing Odisha · the Houthi missile threat over Riyadh ·
  Korea's top court ordering ex-PM Han retried · Colombia's national
  strike · Korea's Suneung exam · Australia's 4.9% jobless rate ·
  marathon champion Peres Jepchirchir's 3-year EPO ban · South Florida
  floods · the French left splitting over Mélenchon · Somalia ordering
  the UAE ambassador out.
- **A dotted world map** with 16 numbered pins (one per card) beside a
  **THE VERDICT** box (the ICJ ruling in three lines), **36 more
  stories** in three columns with headlines short enough that none
  truncates, and a **DATE CHECK** box naming what was left out on
  purpose (wrong-date stories: the Krasnodar refinery strikes of 17–18
  Nov, Hemedti's second death sentence of 18 Nov, the Hormuz tanker
  claim of 4 Nov, the Van Gogh sale of 18 Nov, the IAEA on Yongbyon of
  18 Nov, the Nature red-giant paper of 18 Nov) and what has not
  happened yet (Akvan's landfall, the close of COP31) — plus corrections
  to the day's other front pages (the Hormuz tanker claim and the Nature
  red-giant paper both ran as 19 Nov news; "Earth's missing billion
  years" ran as a card though it is a 4 Nov Nature paper; Voyager "one
  light-day out" ran in a numbers strip though it happened Wednesday).

Every story on the page happened, or was first reported, on Thursday
19 November 2026 (Reuters, AP, AFP, BBC, CNN, WSJ, UN News, Carbon
Brief, Yonhap, ABS, NWS, AIU, IMD, Le Monde, France 24). The build is
fully deterministic: no network, no clock, no randomness — two runs
write identical bytes.

Run it: `mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts`
