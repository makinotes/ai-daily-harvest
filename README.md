# AI Daily Harvest

> **40+ AI sources, one structured feed.** Scored, categorized, and ready for both humans and AI agents — so you don't have to build a pipeline just to stay informed.

Every day, articles from 40+ Chinese and English sources are scored 0-100, assigned a verdict (`must_read` / `worth_reading` / `neutral`), and broken down into key takeaways, structured reasoning, and practical relevance. Humans read the digest; agents consume the JSON. Built for my own use, published openly in case it's useful to others.

Sources are continuously expanding. Suggestions welcome via [issues](../../issues/new).

[中文版 →](README_CN.md)

## What You Get

**Humans** — Skip the 40+ sources, read one digest. Each day's must-read articles are surfaced with a one-line summary and a "why it matters" — so you can decide in seconds whether to click through. Browse [`digest/`](digest/), subscribe via [`feeds/rss.xml`](feeds/rss.xml), or check the weekly trend analysis in [`feeds/weekly/`](feeds/weekly/).

**AI Agents** — Give your agent a daily knowledge update without building a scraping pipeline. Each article comes with pre-extracted learning fields: key takeaways (`highlights`), structured reasoning (`core_point`: Claim → Evidence → Implication), and practical relevance (`why_matters`). Use verdict to prioritize what your agent processes first, and category to build domain-specific knowledge. Fetch [`lists/daily-picks.json`](lists/daily-picks.json) for today's picks, or [`api/{date}.json`](api/) for full data.

**Model Training** — A labeled dataset for content quality research. Each article has a multi-dimensional score, a verdict label, and structured analysis fields — useful for training scoring models, summarization, or content classification. Download [`datasets/scored-articles.jsonl`](datasets/scored-articles.jsonl) or [`scored-articles.csv`](datasets/scored-articles.csv) for Excel.

## Quick Start

```bash
# Today's picks grouped by verdict
curl -s https://raw.githubusercontent.com/makinotes/ai-daily-harvest/master/lists/daily-picks.json | jq '.must_read'

# Full data for a date
curl -s https://raw.githubusercontent.com/makinotes/ai-daily-harvest/master/api/2026-02-27.json

# 30-day articles by category
curl -s https://raw.githubusercontent.com/makinotes/ai-daily-harvest/master/indexes/by-category.json | jq '.categories["AI/Tech"][:3]'

# Trending keywords this week
curl -s https://raw.githubusercontent.com/makinotes/ai-daily-harvest/master/indexes/trending.json
```

For LLMs: [`llms.txt`](llms.txt) for quick start, [`llms-full.txt`](llms-full.txt) for the full guide.

## Data Overview

| Metric | Value |
|--------|-------|
| Sources | 40+ (English tech blogs + Chinese WeChat AI accounts) |
| Daily articles | ~25-40 after filtering |
| Cumulative dataset | 427+ scored articles |
| History | Since 2026-01-26, updated most weekdays |

## What's Inside

| Path | For | What |
|------|-----|------|
| `api/{date}.json` | Agents | Full articles with all learning fields |
| `digest/{date}.md` | Humans | Readable digest grouped by verdict |
| `lists/daily-picks.json` | Both | Today's picks at a glance |
| `datasets/scored-articles.jsonl` | Models | Cumulative scored dataset (JSONL + CSV) |
| `feeds/rss.xml` | Humans | RSS feed, rolling 50 high-quality items |
| `feeds/weekly/{year}-W{week}.md` | Humans | Weekly digest with trend analysis |
| `indexes/by-category.json` | Agents | 30-day articles by topic |
| `indexes/trending.json` | Agents | 7-day trending keywords |

## Verdicts

| Verdict | Meaning |
|---------|---------|
| **must_read** | High quality, novel insights |
| **worth_reading** | Good depth or novelty |
| **neutral** | Acceptable, nothing remarkable |
| **noise** | Low signal-to-noise |
| **overhyped** | Looks important but lacks substance |

## Article Schema

```json
{
  "title": "Article title",
  "link": "https://...",
  "source": "Publisher name",
  "source_channel": "overseas | wechat-ai",
  "category": "AI/Tech | Builder 实践 | AI 使用",
  "pub_date": "2026-02-27",
  "summary": "One-line summary",
  "core_point": "Claim → Evidence → Implication",
  "highlights": ["Key takeaway 1", "Key takeaway 2"],
  "why_matters": "When and how this applies to you",
  "score": 85,
  "level": "精读 | 收藏 | 速览",
  "verdict": "must_read"
}
```

## How It Works

```
40+ Sources → Daily Fetch → Dedup → Multi-dimensional Scoring → Verdict → Publish
```

Scoring is algorithmic and multi-dimensional (novelty, depth, credibility, signal-to-noise). Sources are curated for quality — English tech blogs (Simon Willison, Latent Space, etc.) and Chinese WeChat AI accounts. Same pipeline outputs JSON, Markdown, and JSONL.

## Contributing

**Suggest a source** — [Open an issue](../../issues/new) with the source name, URL, language, and what makes it good.

**Report quality issues** — Article mis-scored or mis-categorized? Open an issue with the date and title.

**Build on the data** — The JSON is designed for programmatic use. If you build something with it, let us know.

## License

Article metadata and AI-generated analysis under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Original content belongs to respective authors.

---

Part of a Personal AI Infrastructure project by [马奇诺](https://mp.weixin.qq.com/s?__biz=MzkyMDE5ODYwMw==).
