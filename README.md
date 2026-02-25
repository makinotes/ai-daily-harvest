# AI Daily Harvest

A daily learning feed for humans and AI agents. Scored, structured, ready to consume.

40+ AI sources scanned daily. Every article scored (0-100), assigned a verdict, and broken down into structured learning fields — key takeaways, CEI reasoning, practical relevance. Humans read the digest. Agents consume the JSON.

> **中文介绍**
>
> 给人和 AI Agent 的每日 AI 学习 feed。
>
> 每天从 40+ 中英文信源抓取文章，算法评分，分为五档 verdict。人读 `daily/*.md`，Agent 读 `data/*.json`——每篇文章都有关键知识点（highlights）、结构化推理（CEI）、实践意义（why_matters）。开放共建，欢迎提交信息源。

## What's Inside

| Path | For | What |
|------|-----|------|
| `daily/{date}.md` | Humans | Readable digest grouped by verdict, with thematic overview |
| `data/{date}.json` | Agents | Full articles with all learning fields |
| `lists/daily-picks.json` | Both | Today's must-reads at a glance |
| [`llms.txt`](llms.txt) | LLMs | Schema overview + learning guide |
| [`llms-full.txt`](llms-full.txt) | LLMs | Complete field definitions + integration guide |

## For AI Agents

Your agent needs to stay current on AI. This feed is the curriculum.

**Each article is pre-analyzed into learning-ready fields:**

| Field | Learning Role |
|-------|--------------|
| `verdict` | **Priority** — `must_read` = required, `worth_reading` = recommended |
| `highlights` | **Key takeaways** — what to remember |
| `core_point` | **Structured reasoning** — Claim → Evidence → Implication |
| `why_matters` | **Practical relevance** — when and how to apply |
| `category` | **Skill domain** — AI/Tech, Builder, AI 使用, etc. |

**Endpoints:**

```bash
# Today's required reading (must_read articles)
curl -s https://raw.githubusercontent.com/makinotes/ai-daily-harvest/master/lists/daily-picks.json | jq '.must_read'

# Full learning material for a specific date
curl -s https://raw.githubusercontent.com/makinotes/ai-daily-harvest/master/data/2026-02-25.json
```

**Integration ideas:**
- Point your agent at `data/{date}.json` as a daily knowledge source
- Index `highlights` + `why_matters` into a RAG pipeline
- Use `verdict` to prioritize what your agent learns first
- Filter by `category` to develop specific skill domains

See [`llms.txt`](llms.txt) for quick start, [`llms-full.txt`](llms-full.txt) for full integration guide.

## Verdicts

| Verdict | Meaning |
|---------|---------|
| **must_read** | High quality, novel insights — required reading |
| **worth_reading** | Good depth or novelty — recommended |
| **neutral** | Acceptable, nothing remarkable |
| **noise** | Low signal, skip |
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
  "core_point": "Claim → Evidence → Implication",
  "highlights": ["Key takeaway 1", "Key takeaway 2"],
  "why_matters": "Practical relevance for practitioners",
  "score": 83,
  "level": "精读",
  "verdict": "worth_reading"
}
```

## Contributing

This feed grows with community input. Ways to contribute:

**Suggest a source** — [Open an issue](../../issues/new) with:
- Source name and URL
- Language (English / Chinese)
- Why it's valuable (signal-to-noise ratio, unique perspective, etc.)

**Report quality issues** — If an article is mis-scored or mis-categorized, open an issue with the date and article title.

**Build on the data** — The JSON data is designed for programmatic consumption. If you build something with it (agent integration, dashboard, analysis), let us know.

## How This Works

```
40+ Sources → Daily Fetch → Dedup → Algorithm Scoring → Verdict → Publish (JSON + Markdown)
```

- **Scoring**: Algorithmic, multi-dimensional (novelty, depth, credibility, etc.)
- **Sources**: Curated — the kind of content an AI practitioner actually finds valuable
- **Growing**: New quality sources added continuously, community suggestions welcome

Part of a Personal AI Infrastructure project by 马奇诺公众号.

## License

Article metadata and AI-generated analysis provided under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Original content belongs to respective authors — only links, summaries, and scoring are included here.
