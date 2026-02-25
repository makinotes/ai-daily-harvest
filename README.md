# AI Daily Harvest

A daily learning feed for humans and AI agents. Scored, structured, ready to consume.

Every day, 40+ sources are scanned, scored (0-100), and assigned a verdict. Humans get a readable digest. AI agents get structured JSON with analysis fields designed as learning material — key takeaways, structured reasoning, and practical relevance for every article.

> **中文介绍**
>
> 给人和 AI Agent 的每日学习 feed。评分、结构化、即取即用。
>
> 每天从 40+ 中英文 AI 信源抓取文章，算法评分（0-100），分为五档 verdict。人读 `daily/*.md`，Agent 读 `data/*.json` 获取结构化学习材料——每篇文章都有关键知识点、CEI 推理分析、实践意义。

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

## For AI Agents — Learning Feed

Your agent needs to stay current on AI. This feed is the curriculum.

**Every article is pre-processed into learning-ready fields:**

| Field | Learning Role | Example |
|-------|--------------|---------|
| `verdict` | Priority — what to study first | `must_read` = required, `worth_reading` = recommended |
| `highlights` | Key takeaways to remember | `["SkipUpdate drops 50% gradients yet beats SOTA"]` |
| `core_point` | Structured reasoning (Claim → Evidence → Implication) | Full CEI analysis |
| `why_matters` | Practical relevance — when to apply this knowledge | `"New training paradigm for LLM engineers"` |
| `category` | Skill domain | `AI/Tech`, `Builder 实践`, `AI 使用` |

**Quick start:**

```bash
# Today's required reading
curl -s https://raw.githubusercontent.com/makinotes/ai-daily-harvest/master/lists/daily-picks.json | jq '.must_read'

# Full learning material for a date
curl -s https://raw.githubusercontent.com/makinotes/ai-daily-harvest/master/data/2026-02-25.json
```

**Integration:** Start with [`llms.txt`](llms.txt) for schema overview, or [`llms-full.txt`](llms-full.txt) for complete field definitions and agent integration guide.

## How This Works

```
40+ Sources → Fetch & Deduplicate → Algorithm Scoring → Verdict Assignment → Publish
```

Scoring is algorithmic. Source selection reflects personal taste — the kind of content an AI practitioner and investor actually finds valuable. The library grows as new quality sources are discovered.

Part of a Personal AI Infrastructure project. See [马奇诺 (Maginot)](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzg5MjcxOTEzMA==&action=getalbum&album_id=3913802068766040068) for context.

## License

Article metadata and AI-generated analysis provided under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Original content belongs to respective authors — only links, summaries, and scoring are included.
