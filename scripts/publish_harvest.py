#!/usr/bin/env python3
"""
publish_harvest.py — Extract daily AI articles from briefing ODS cache,
assign verdicts, and publish as structured JSON + readable Markdown.

Usage:
    python3 publish_harvest.py                  # today
    python3 publish_harvest.py --date 2026-02-25  # specific date

Reads from:
    briefing/cache/overseas/briefing_data_{date}.json
    briefing/cache/wechat-ai/briefing_data_{date}.json

Outputs to:
    ai-daily-harvest/data/{date}.json           # full article data (public)
    ai-daily-harvest/daily/{date}.md            # readable version (public)
    ai-daily-harvest/lists/daily-picks.json     # red/black list (public)
    ai-daily-harvest/sources/source_stats.json  # source stats (private, .gitignore)
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

# Verdict display labels
VERDICT_LABELS = {
    "must_read": "Must Read",
    "worth_reading": "Worth Reading",
    "neutral": "Neutral",
    "noise": "Noise",
    "overhyped": "Overhyped",
}

VERDICT_ORDER = ["must_read", "worth_reading", "neutral", "noise", "overhyped"]


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


def assign_verdict(article):
    """Assign verdict based on scoring dimensions. Returns verdict string."""
    score = article.get("score", 0)
    novelty = article.get("novelty", 0)
    depth = article.get("depth", 0)
    noise = article.get("noise", 0)
    credibility = article.get("credibility", 0)

    if score >= 85:
        return "must_read"
    if 75 <= score <= 84 and (novelty >= 2 or depth >= 2):
        return "worth_reading"
    if 60 <= score <= 69 and noise <= 1:
        return "noise"
    if score >= 70 and novelty == 0 and credibility <= 1:
        return "overhyped"
    return "neutral"


def clean_article(article, channel):
    """Extract public fields from an ODS article. No scoring dimensions exposed."""
    verdict = assign_verdict(article)
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
        "verdict": verdict,
    }


def generate_json(articles, date_str):
    """Write structured JSON output."""
    sorted_articles = sorted(articles, key=lambda x: x["score"], reverse=True)
    verdict_counts = {}
    for a in sorted_articles:
        v = a["verdict"]
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    output = {
        "date": date_str,
        "total": len(sorted_articles),
        "verdict_counts": verdict_counts,
        "articles": sorted_articles,
    }
    path = os.path.join(HARVEST_DIR, "data", f"{date_str}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  [ok] {path} ({len(articles)} articles)")
    return path


def generate_daily_picks(articles, date_str):
    """Write daily red/black list JSON."""
    picks = {"date": date_str}
    for v in VERDICT_ORDER:
        group = [a for a in articles if a["verdict"] == v]
        group.sort(key=lambda x: x["score"], reverse=True)
        picks[v] = [
            {
                "title": a["title"],
                "link": a["link"],
                "source": a["source"],
                "score": a["score"],
                "why": a.get("why_matters", ""),
            }
            for a in group
        ]

    lists_dir = os.path.join(HARVEST_DIR, "lists")
    os.makedirs(lists_dir, exist_ok=True)
    path = os.path.join(lists_dir, "daily-picks.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(picks, f, ensure_ascii=False, indent=2)
    print(f"  [ok] {path}")
    return path


def update_source_stats(articles, date_str):
    """Update cumulative per-source statistics (private, not pushed to GitHub)."""
    sources_dir = os.path.join(HARVEST_DIR, "sources")
    os.makedirs(sources_dir, exist_ok=True)
    stats_path = os.path.join(sources_dir, "source_stats.json")

    # Load existing stats
    stats = {}
    if os.path.exists(stats_path):
        with open(stats_path, "r", encoding="utf-8") as f:
            stats = json.load(f)

    sources_data = stats.get("sources", {})

    # Aggregate today's data per source
    today_by_source = {}
    for a in articles:
        src = a["source"]
        if src not in today_by_source:
            today_by_source[src] = {"scores": [], "verdicts": []}
        today_by_source[src]["scores"].append(a["score"])
        today_by_source[src]["verdicts"].append(a["verdict"])

    # Update cumulative stats
    for src, data in today_by_source.items():
        if src not in sources_data:
            sources_data[src] = {
                "articles_count": 0,
                "total_score": 0,
                "must_read_count": 0,
                "noise_count": 0,
                "first_seen": date_str,
                "last_seen": date_str,
            }
        s = sources_data[src]
        s["articles_count"] += len(data["scores"])
        s["total_score"] += sum(data["scores"])
        s["must_read_count"] += data["verdicts"].count("must_read")
        s["noise_count"] += (
            data["verdicts"].count("noise") + data["verdicts"].count("overhyped")
        )
        s["last_seen"] = date_str
        # Computed fields
        s["avg_score"] = round(s["total_score"] / s["articles_count"], 1)
        s["must_read_rate"] = round(s["must_read_count"] / s["articles_count"] * 100, 1)
        s["noise_rate"] = round(s["noise_count"] / s["articles_count"] * 100, 1)

    stats["sources"] = sources_data
    stats["updated"] = date_str

    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"  [ok] {stats_path} ({len(sources_data)} sources tracked)")
    return stats_path


def generate_markdown(articles, date_str):
    """Write human-readable Markdown, grouped by verdict."""
    all_sources = set(a["source"] for a in articles)

    # Count verdicts
    verdict_counts = {}
    for a in articles:
        v = a["verdict"]
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    lines = []
    lines.append(f"# AI Daily Harvest — {date_str}")
    lines.append("")

    # Overview section
    lines.append("## Overview")
    lines.append("")

    # Top picks table (must_read articles)
    must_reads = sorted(
        [a for a in articles if a["verdict"] == "must_read"],
        key=lambda x: x["score"],
        reverse=True,
    )
    if must_reads:
        lines.append("| Score | Article | Source |")
        lines.append("|------:|---------|--------|")
        for a in must_reads[:5]:
            title_short = a["title"][:60] + "..." if len(a["title"]) > 60 else a["title"]
            lines.append(f"| **{a['score']}** | [{title_short}]({a['link']}) | {a['source']} |")
        lines.append("")

    # Stats + sources in blockquote
    verdict_parts = []
    for v in VERDICT_ORDER:
        c = verdict_counts.get(v, 0)
        if c > 0:
            verdict_parts.append(f"**{c}** {VERDICT_LABELS[v].lower()}")
    source_counts = {}
    for a in articles:
        source_counts[a["source"]] = source_counts.get(a["source"], 0) + 1
    top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_str = " · ".join(f"{name} ({count})" for name, count in top_sources)
    lines.append(f"> {len(articles)} articles: {' · '.join(verdict_parts)}")
    lines.append(">")
    lines.append(f"> Top sources: {top_str}")
    lines.append("")

    # Group by verdict
    for verdict in VERDICT_ORDER:
        group = [a for a in articles if a["verdict"] == verdict]
        if not group:
            continue
        group.sort(key=lambda x: x["score"], reverse=True)

        label = VERDICT_LABELS[verdict]
        lines.append(f"## {label}")
        lines.append("")

        for a in group:
            title = a["title"]
            link = a["link"]
            score = a["score"]
            source = a["source"]
            category = a["category"]
            level = a["level"]
            summary = a["summary"]
            core_point = a["core_point"]
            highlights = a["highlights"]
            why_matters = a["why_matters"]

            lines.append(f"### [{title}]({link}) — {score}/100")
            lines.append(f"**{source}** · {category} · {level}")
            lines.append(f"> {summary}")
            lines.append("")
            if core_point:
                lines.append(f"{core_point}")
                lines.append("")
            if highlights:
                for h in highlights:
                    lines.append(f"- {h}")
                lines.append("")
            if why_matters:
                lines.append(f"**Why it matters:** {why_matters}")
                lines.append("")
            lines.append("---")
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

    # Ensure output dirs exist
    for subdir in ["data", "daily", "lists", "sources"]:
        os.makedirs(os.path.join(HARVEST_DIR, subdir), exist_ok=True)

    # Collect articles from all channels
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
    generate_daily_picks(all_articles, date_str)
    generate_markdown(all_articles, date_str)
    update_source_stats(all_articles, date_str)

    # Summary
    verdicts = {}
    for a in all_articles:
        v = a["verdict"]
        verdicts[v] = verdicts.get(v, 0) + 1
    v_summary = ", ".join(f"{v}={c}" for v, c in sorted(verdicts.items()))
    print(f"Done. {len(all_articles)} articles published. [{v_summary}]")


if __name__ == "__main__":
    main()
