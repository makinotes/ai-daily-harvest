#!/usr/bin/env python3
"""
publish_harvest.py — Extract daily AI articles from briefing ODS cache
and publish as structured JSON + readable Markdown.

Usage:
    python3 publish_harvest.py                  # today
    python3 publish_harvest.py --date 2026-02-25  # specific date

Reads from:
    briefing/cache/overseas/briefing_data_{date}.json
    briefing/cache/wechat-ai/briefing_data_{date}.json

Outputs to:
    ai-daily-harvest/data/{date}.json
    ai-daily-harvest/daily/{date}.md
"""

import json
import os
import sys
from datetime import datetime

# Paths
WORKSPACE = "/Users/makino/Desktop/claude code"
CACHE_DIR = os.path.join(WORKSPACE, "briefing", "cache")
HARVEST_DIR = os.path.join(WORKSPACE, "ai-daily-harvest")

# Channels to include (AI-related only)
CHANNELS = ["overseas", "wechat-ai"]

# Fields to keep in public output
PUBLIC_FIELDS = {
    "title", "link", "source", "category", "pub_date",
    "summary", "core_point", "highlights", "why_matters",
    "score", "level",
    # scoring dimensions (nested separately)
    "novelty", "depth", "actionability", "credibility",
    "logic", "timeliness", "noise",
}

# Channel display names
CHANNEL_NAMES = {
    "overseas": "Overseas",
    "wechat-ai": "WeChat AI",
}


def load_cache(channel, date_str):
    """Load ODS cache for a channel and date."""
    path = os.path.join(CACHE_DIR, channel, f"briefing_data_{date_str}.json")
    if not os.path.exists(path):
        print(f"  [skip] {path} not found")
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    articles = []
    for tier_key in ["tier1", "tier2", "tier3", "hn"]:
        articles.extend(data.get(tier_key, []))
    return articles


def clean_article(article, channel):
    """Extract public fields from an ODS article."""
    scoring = {
        "novelty": article.get("novelty", 0),
        "depth": article.get("depth", 0),
        "actionability": article.get("actionability", 0),
        "credibility": article.get("credibility", 0),
        "logic": article.get("logic", 0),
        "timeliness": article.get("timeliness", 0),
        "noise": article.get("noise", 0),
    }
    return {
        "title": article.get("title", ""),
        "link": article.get("link", ""),
        "source": article.get("source", ""),
        "source_channel": channel,
        "category": article.get("category", ""),
        "pub_date": article.get("pub_date", ""),
        "summary": article.get("summary", ""),
        "core_point": article.get("core_point", ""),
        "highlights": article.get("highlights", []),
        "why_matters": article.get("why_matters", ""),
        "score": article.get("score", 0),
        "level": article.get("level", ""),
        "scoring": scoring,
    }


def generate_json(articles, date_str):
    """Write structured JSON output."""
    output = {
        "date": date_str,
        "total": len(articles),
        "articles": sorted(articles, key=lambda x: x["score"], reverse=True),
    }
    path = os.path.join(HARVEST_DIR, "data", f"{date_str}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  [ok] {path} ({len(articles)} articles)")
    return path


def generate_markdown(articles, date_str):
    """Write human-readable Markdown output."""
    # Group by channel
    by_channel = {}
    for a in articles:
        ch = a["source_channel"]
        by_channel.setdefault(ch, []).append(a)

    # Count unique sources
    all_sources = set(a["source"] for a in articles)

    lines = []
    lines.append(f"# AI Daily Harvest — {date_str}")
    lines.append("")
    lines.append(f"> {len(articles)} articles curated from {len(all_sources)} sources")
    lines.append("")

    for channel in CHANNELS:
        channel_articles = by_channel.get(channel, [])
        if not channel_articles:
            continue
        channel_articles.sort(key=lambda x: x["score"], reverse=True)
        lines.append(f"## {CHANNEL_NAMES.get(channel, channel)}")
        lines.append("")
        for a in channel_articles:
            title = a["title"]
            link = a["link"]
            score = a["score"]
            source = a["source"]
            category = a["category"]
            level = a["level"]
            summary = a["summary"]
            lines.append(f"### [{title}]({link}) — {score}/100")
            lines.append(f"**{source}** · {category} · {level}")
            lines.append(f"> {summary}")
            lines.append("")

    path = os.path.join(HARVEST_DIR, "daily", f"{date_str}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  [ok] {path}")
    return path


def main():
    # Parse date argument
    date_str = datetime.now().strftime("%Y-%m-%d")
    if "--date" in sys.argv:
        idx = sys.argv.index("--date")
        if idx + 1 < len(sys.argv):
            date_str = sys.argv[idx + 1]

    print(f"AI Daily Harvest — publishing {date_str}")

    # Collect articles from all channels
    # Filter: not rejected, score >= 60 (skip unscored HN items and noise)
    all_articles = []
    for channel in CHANNELS:
        raw = load_cache(channel, date_str)
        cleaned = []
        for a in raw:
            if a.get("rejected"):
                continue
            if a.get("score", 0) < 60:
                continue
            cleaned.append(clean_article(a, channel))
        print(f"  {channel}: {len(cleaned)} articles (filtered from {len(raw)})")
        all_articles.extend(cleaned)

    if not all_articles:
        print("  [warn] No articles found, skipping")
        return

    # Generate outputs
    generate_json(all_articles, date_str)
    generate_markdown(all_articles, date_str)
    print(f"Done. {len(all_articles)} articles published.")


if __name__ == "__main__":
    main()
