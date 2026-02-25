# AI Daily Harvest

A curated daily feed of AI-related articles, scored and structured by an automated briefing system.

Every day, this repo is updated with hand-picked articles from top tech blogs and Chinese AI WeChat accounts — each article scored on 7 dimensions, summarized, and enriched with core insights.

> **中文介绍**
>
> 这是一个每日自动更新的 AI 内容精选库。数据来源于一套自建的简报系统（Personal AI Infra），覆盖海外科技博客和国内 AI 公众号。每篇文章经过 7 维度自动评分、摘要提炼和核心观点提取。
>
> 两种消费方式：机器读 `data/*.json`，人读 `daily/*.md`。

## Data Sources

| Channel | Coverage | Language |
|---------|----------|----------|
| **Overseas** | Tech blogs, HN, research papers (Simon Willison, Modal, Anthropic, etc.) | EN |
| **WeChat AI** | Top Chinese AI/Tech accounts (PaperAgent, 赛博禅心, etc.) | CN |

## Daily Output

### JSON (`data/{date}.json`)

Structured for programmatic consumption. Each article includes:

```json
{
  "title": "Directory Snapshots: Resumable project state for Sandboxes",
  "link": "https://modal.com/blog/...",
  "source": "Modal Labs Blog",
  "source_channel": "overseas",
  "category": "Builder 实践",
  "pub_date": "2026-02-24",
  "summary": "One-line summary in Chinese",
  "core_point": "CEI-format analysis: Claim → Evidence → Implication",
  "highlights": ["Key insight 1", "Key insight 2"],
  "why_matters": "Why this matters to practitioners",
  "score": 83,
  "level": "精读",
  "scoring": {
    "novelty": 2,
    "depth": 2,
    "actionability": 3,
    "credibility": 3,
    "logic": 3,
    "timeliness": 3,
    "noise": 3
  }
}
```

### Markdown (`daily/{date}.md`)

Human-readable daily digest, grouped by channel, sorted by score.

## Scoring System

Each article is evaluated on 7 dimensions (1-3 scale):

| Dimension | What it measures |
|-----------|-----------------|
| **Novelty** | How new is the information? |
| **Depth** | How deep is the analysis? |
| **Actionability** | Can you act on this today? |
| **Credibility** | Is the source trustworthy? |
| **Logic** | Is the reasoning sound? |
| **Timeliness** | Is this time-sensitive? |
| **Noise** | Signal-to-noise ratio (3 = clean) |

**Total score** = weighted composite (0-100). Articles are tiered:

| Level | Score Range | Meaning |
|-------|------------|---------|
| 收藏 (Bookmark) | 90+ | Must-read, high long-term value |
| 精读 (Deep Read) | 75-89 | Worth reading in full |
| 速览 (Skim) | 60-74 | Scan the summary |

## How This Works

This repo is updated daily by an automated pipeline:

```
Information Sources → Fetch & Deduplicate → AI Scoring (7-dim)
    → Summarize & Extract Insights → Publish to GitHub
```

The system is part of a Personal AI Infrastructure project. For details, see the [马奇诺 (Maginot)](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzg5MjcxOTEzMA==&action=getalbum&album_id=3913802068766040068) WeChat account.

## Usage

**For humans**: Read the daily markdown files in `daily/`.

**For agents/scripts**:
```python
import json
with open("data/2026-02-25.json") as f:
    feed = json.load(f)
for article in feed["articles"]:
    if article["score"] >= 85:
        print(article["title"], article["core_point"])
```

## License

The article metadata and AI-generated summaries in this repository are provided under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Original article content belongs to their respective authors — only links, summaries, and scoring are included here.
