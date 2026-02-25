# AI Daily Harvest

An opinionated daily AI content feed. Algorithm-driven, shaped by personal taste, growing.

This is not a neutral aggregator. Every article is scored, judged, and assigned a verdict — **must-read**, **worth reading**, **noise**, or **overhyped**. The goal: tell you what's worth your time and what isn't.

> **中文介绍**
>
> 一个有态度的 AI 内容精选。算法驱动，个人品味加权，持续扩充。
>
> 每天从 40+ 中英文信源抓取文章，自动评分（0-100），分为"必读 / 值得看 / 一般 / 噪音 / 过誉"五档。人读 `daily/*.md`，AI 读 `data/*.json`，快速筛选读 `lists/daily-picks.json`。

## What You Get

| File | For | Content |
|------|-----|---------|
| `daily/{date}.md` | Humans | Formatted digest, grouped by verdict |
| `data/{date}.json` | Agents | Full scored articles with analysis |
| `lists/daily-picks.json` | Both | Today's red list (must-read) and black list (noise) |
| `llms.txt` | LLMs | Schema overview for AI consumption |

## Verdicts

Every article gets one:

| Verdict | Meaning |
|---------|---------|
| **must_read** | Exceptionally high quality, novel insights |
| **worth_reading** | Good quality with notable depth or novelty |
| **neutral** | Acceptable, nothing remarkable |
| **noise** | Low signal-to-noise ratio, skip |
| **overhyped** | Looks important but lacks substance |

## Article Schema

```json
{
  "title": "Article title",
  "link": "https://...",
  "source": "Publisher name",
  "source_channel": "overseas | wechat-ai",
  "category": "AI/Tech",
  "pub_date": "2026-02-25",
  "summary": "One-line summary",
  "core_point": "Structured analysis (Claim → Evidence → Implication)",
  "highlights": ["Key insight 1", "Key insight 2"],
  "why_matters": "Why this matters to practitioners",
  "score": 83,
  "level": "精读",
  "verdict": "worth_reading"
}
```

## For AI Agents

Start with [`llms.txt`](llms.txt) for a quick schema overview, or [`llms-full.txt`](llms-full.txt) for complete field definitions and usage examples.

Quick access to today's must-reads:
```
GET https://raw.githubusercontent.com/makinotes/ai-daily-harvest/master/lists/daily-picks.json
```

## How This Works

```
40+ Sources → Fetch & Deduplicate → Algorithm Scoring → Verdict Assignment → Publish
```

Scoring is algorithmic. Source selection reflects personal taste — the kind of content an AI practitioner and investor actually finds valuable. The library grows as new quality sources are discovered.

Part of a Personal AI Infrastructure project. See [马奇诺 (Maginot)](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzg5MjcxOTEzMA==&action=getalbum&album_id=3913802068766040068) for context.

## License

Article metadata and AI-generated analysis provided under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Original content belongs to respective authors — only links, summaries, and scoring are included.
