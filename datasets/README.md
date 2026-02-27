# AI Daily Harvest — Scored Articles Dataset

## Overview

A cumulative dataset of Chinese and English AI articles, each scored (0-100) and analyzed by LLM. Updated daily.

- **Format**: JSONL (one JSON object per line)
- **File**: `scored-articles.jsonl`
- **Update frequency**: Daily append
- **Source**: 40+ AI-focused RSS feeds and newsletters

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Article title |
| `link` | string | Original URL |
| `source` | string | Publisher name |
| `source_channel` | string | Feed channel (`overseas` or `wechat-ai`) |
| `category` | string | Topic category (e.g., `AI/Tech`, `Builder 实践`, `AI 使用`, `YouTube`) |
| `pub_date` | string | Publication date (YYYY-MM-DD) |
| `summary` | string | One-line summary |
| `core_point` | string | Structured analysis: Claim → Evidence → Implication |
| `highlights` | list[string] | Key takeaways |
| `why_matters` | string | Practical relevance for practitioners |
| `score` | int | Quality score (0-100), only articles >= 60 included |
| `level` | string | Chinese quality tier (`收藏`, `精读`, `速览`) |
| `verdict` | string | Priority label: `must_read`, `worth_reading`, `neutral`, `noise`, `overhyped` |

## Scoring

Scores are **LLM-generated** (not human-annotated), based on four dimensions:
- Novelty (0-3): How new is this information?
- Depth (0-3): How deep is the analysis?
- Credibility (0-3): How reliable is the source/evidence?
- Noise (0-3): How much filler vs signal?

The final score (0-100) is a weighted composite. Articles below 60 are excluded.

## Verdict Distribution

| Verdict | Criteria | Typical % |
|---------|----------|-----------|
| `must_read` | score >= 85 | ~20% |
| `worth_reading` | 75-84 with high novelty or depth | ~20% |
| `neutral` | default | ~50% |
| `noise` | 60-69, low noise dimension | ~5% |
| `overhyped` | high score but zero novelty | ~5% |

## Use Cases

- **Train a quality scorer**: Use (article metadata, score) pairs to fine-tune a scoring model
- **Summarization training**: Use (title + link, summary + highlights + core_point) as generation targets
- **Content classification**: Use (title + summary, category + verdict) for multi-label classification
- **Trend analysis**: Aggregate by date and category to track topic evolution

## CSV Version

`scored-articles.csv` contains the same data as the JSONL, formatted for Excel / Google Sheets.

- Encoding: UTF-8 with BOM (opens correctly in Excel without garbled Chinese text)
- Field names match the JSONL schema exactly (`pub_date`, `source_channel`, etc.)
- `highlights` array is joined with ` | ` separator into a single cell
- Multi-line text fields are flattened to single lines
- Sorted by date (newest first), then by score (highest first)
- Deduplicated by (pub_date, title), regenerated from JSONL on each pipeline run

## Limitations

- Summaries and analyses are LLM-generated, not human-written
- Full article text is not included; use the `link` field to fetch original content
- Scoring reflects one opinionated rubric, not universal quality consensus
- Dataset starts from January 2026; historical coverage is limited
- Early articles (before mid-February 2026) may have empty `why_matters` and `core_point` fields — these analysis fields were added to the pipeline later and not backfilled

## License

Same as repository: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
