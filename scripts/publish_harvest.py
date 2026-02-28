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
    api/{date}.json            # full article data (public)
    digest/{YYYY-MM}/{date}.md  # readable version (public)
    lists/daily-picks.json     # red/black list (public)
    sources/source_stats.json  # source stats (private, .gitignore)
"""

import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta
from xml.sax.saxutils import escape as xml_escape

# Paths — resolve relative to script location
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HARVEST_DIR = os.path.dirname(_SCRIPT_DIR)  # parent of scripts/
WORKSPACE = os.path.dirname(HARVEST_DIR)     # parent of ai-daily-harvest/
CACHE_DIR = os.path.join(WORKSPACE, "briefing", "cache")

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
    path = os.path.join(HARVEST_DIR, "api", f"{date_str}.json")
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


def extract_theme(summary, max_len=40):
    """Extract short theme from article summary for overview digest."""
    if not summary:
        return ""
    if len(summary) <= max_len:
        return summary.rstrip("。")
    # Try cutting at Chinese comma/period, but only if segment is informative (>15 chars)
    for sep in ["，", "。", "；"]:
        idx = summary.find(sep)
        if 15 < idx <= max_len:
            return summary[:idx]
    # Fallback: truncate, avoid cutting mid-word
    truncated = summary[:max_len]
    if truncated[-1].isascii() and truncated[-1].isalpha():
        last_space = truncated.rfind(" ")
        if last_space > max_len // 2:
            truncated = truncated[:last_space]
    return truncated.rstrip("，。；、 ") + "…"


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

    # Compute groups
    must_reads = sorted(
        [a for a in articles if a["verdict"] == "must_read"],
        key=lambda x: x["score"],
        reverse=True,
    )
    # Compute stats
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

    # Thematic digest + stats blockquote
    MAX_THEMES = 3
    if must_reads:
        themes = [extract_theme(a["summary"]) for a in must_reads[:MAX_THEMES]]
        extra = len(must_reads) - MAX_THEMES
        digest = " · ".join(themes)
        if extra > 0:
            digest += f" (+{extra} more)"
        lines.append(f"> **Must Read** — {digest}")
    if must_reads:
        lines.append(">")
    lines.append(f"> {len(articles)} articles: {' · '.join(verdict_parts)}")
    lines.append(">")
    lines.append(f"> Top sources: {top_str}")
    lines.append("")

    # Top picks list (must_read articles)
    if must_reads:
        for a in must_reads[:5]:
            title_short = a["title"][:60] + "..." if len(a["title"]) > 60 else a["title"]
            lines.append(f"- **{a['score']}** [{title_short}]({a['link']}) — {a['source']}")
        lines.append("")

    # Group by verdict (skip noise/overhyped from readable output)
    for verdict in VERDICT_ORDER:
        if verdict in ("noise", "overhyped"):
            continue
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

            title_display = title[:80] + "…" if len(title) > 80 else title
            lines.append(f"### [{title_display}]({link}) — {score}/100")
            lines.append(f"**{source}** · {category} · {level}")
            lines.append(f"> {summary}")
            lines.append("")
            if core_point:
                # Strip internal annotations that may leak from source data
                core_point_clean = core_point.replace("疑似PR稿。", "").replace("疑似 PR 稿。", "").replace("疑似PR稿", "").replace("疑似 PR 稿", "").strip()
                if core_point_clean:
                    lines.append(f"{core_point_clean}")
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

    month_dir = os.path.join(HARVEST_DIR, "digest", date_str[:7])
    os.makedirs(month_dir, exist_ok=True)
    path = os.path.join(month_dir, f"{date_str}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  [ok] {path}")
    return path


def append_dataset(articles, date_str):
    """Append today's articles to cumulative JSONL dataset. Idempotent."""
    datasets_dir = os.path.join(HARVEST_DIR, "datasets")
    os.makedirs(datasets_dir, exist_ok=True)
    jsonl_path = os.path.join(datasets_dir, "scored-articles.jsonl")

    # Load existing entries for dedup (date+title)
    existing = set()
    if os.path.exists(jsonl_path):
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    existing.add((entry.get("pub_date", ""), entry.get("title", "")))
                except json.JSONDecodeError:
                    continue

    # Append new articles
    new_count = 0
    with open(jsonl_path, "a", encoding="utf-8") as f:
        for a in sorted(articles, key=lambda x: x["score"], reverse=True):
            key = (a.get("pub_date", ""), a.get("title", ""))
            if key in existing:
                continue
            f.write(json.dumps(a, ensure_ascii=False) + "\n")
            new_count += 1

    total = len(existing) + new_count
    print(f"  [ok] {jsonl_path} (+{new_count} new, {total} total)")
    return jsonl_path


def generate_rss(articles, date_str):
    """Generate RSS 2.0 feed with rolling 50 items (must_read + worth_reading)."""
    feeds_dir = os.path.join(HARVEST_DIR, "feeds")
    os.makedirs(feeds_dir, exist_ok=True)
    rss_path = os.path.join(feeds_dir, "rss.xml")

    # Load existing items from old RSS (if any)
    old_items = []
    if os.path.exists(rss_path):
        with open(rss_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Extract existing <item> blocks
        old_items = re.findall(r"<item>.*?</item>", content, re.DOTALL)

    # Build new items from today's high-quality articles
    quality = [a for a in articles if a["verdict"] in ("must_read", "worth_reading")]
    quality.sort(key=lambda x: x["score"], reverse=True)

    new_items = []
    for a in quality:
        desc = a.get("summary", "")
        if a.get("highlights"):
            hl_list = "".join(
                "<li>{}</li>".format(xml_escape(h)) for h in a["highlights"]
            )
            desc += "<ul>{}</ul>".format(hl_list)

        # Format pubDate as RFC 822 (fallback to harvest date if empty/invalid)
        pub_date_str = a.get("pub_date", "") or ""
        try:
            dt = datetime.strptime(pub_date_str, "%Y-%m-%d")
            rfc822_date = dt.strftime("%a, %d %b %Y 00:00:00 GMT")
        except ValueError:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            rfc822_date = dt.strftime("%a, %d %b %Y 00:00:00 GMT")

        item = (
            "<item>\n"
            "  <title>{title}</title>\n"
            "  <link>{link}</link>\n"
            "  <description><![CDATA[{desc}]]></description>\n"
            "  <category>{cat}</category>\n"
            "  <pubDate>{date}</pubDate>\n"
            "  <source url=\"{link}\">{source}</source>\n"
            "</item>"
        ).format(
            title=xml_escape(a.get("title", "")),
            link=xml_escape(a.get("link", "")),
            desc=desc,
            cat=xml_escape(a.get("category", "")),
            date=rfc822_date,
            source=xml_escape(a.get("source", "")),
        )
        new_items.append(item)

    # Fix empty pubDate in old items (backfill with harvest date)
    fallback_rfc822 = datetime.strptime(date_str, "%Y-%m-%d").strftime(
        "%a, %d %b %Y 00:00:00 GMT"
    )
    fixed_old = []
    for item in old_items:
        if "<pubDate></pubDate>" in item:
            item = item.replace(
                "<pubDate></pubDate>",
                "<pubDate>{}</pubDate>".format(fallback_rfc822),
            )
        fixed_old.append(item)

    # Merge: new items first, then old (dedup by link)
    seen_links = set()
    merged = []
    for item in new_items + fixed_old:
        link_match = re.search(r"<link>(.*?)</link>", item)
        if link_match:
            link = link_match.group(1)
            if link in seen_links:
                continue
            seen_links.add(link)
        merged.append(item)
    merged = merged[:50]  # Rolling window

    items_xml = "\n".join(merged)
    rss_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "<channel>\n"
        "  <title>AI Daily Harvest</title>\n"
        "  <link>https://github.com/makinotes/ai-daily-feed</link>\n"
        "  <description>Daily AI learning feed. 40+ sources scored and structured.</description>\n"
        "  <language>zh-cn</language>\n"
        "  <lastBuildDate>{date}</lastBuildDate>\n"
        "{items}\n"
        "</channel>\n"
        "</rss>"
    ).format(date=xml_escape(date_str), items=items_xml)

    with open(rss_path, "w", encoding="utf-8") as f:
        f.write(rss_xml)
    print(f"  [ok] {rss_path} ({len(merged)} items)")
    return rss_path


def load_recent_data(days=30):
    """Load articles from recent api/*.json files."""
    data_dir = os.path.join(HARVEST_DIR, "api")
    all_articles = []
    today = datetime.now()
    for i in range(days):
        d = today - timedelta(days=i)
        path = os.path.join(data_dir, f"{d.strftime('%Y-%m-%d')}.json")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        all_articles.extend(data.get("articles", []))
    return all_articles


# English stop words for trending analysis
_STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to",
    "for", "of", "and", "or", "not", "with", "from", "by", "as", "it",
    "its", "this", "that", "be", "has", "have", "had", "will", "can",
    "do", "does", "did", "but", "if", "so", "than", "more", "about",
    "how", "what", "when", "where", "who", "which", "all", "your", "you",
    "new", "one", "two", "up", "out", "just", "into",
}

# Chinese stop words / particles
_CN_STOP = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
    "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会",
    "着", "没有", "看", "好", "自己", "这", "他", "她", "它", "吗", "什么",
    "我们", "那", "被", "让", "把", "还", "对", "用", "能", "与", "及",
    "等", "从", "为", "之", "而", "以", "如", "中", "大", "年", "月", "日",
}


def extract_keywords(title):
    """Extract keywords from a title. Uses known terms + English proper nouns."""
    words = set()
    # English words (3+ chars, lowered) — keep original case for proper nouns
    for w in re.findall(r"[A-Za-z][A-Za-z0-9]+", title):
        w_lower = w.lower()
        if len(w_lower) >= 3 and w_lower not in _STOP_WORDS:
            words.add(w if w[0].isupper() or w.isupper() else w_lower)
    # Chinese: match known compound terms (3+ chars) from title
    for term in _CN_KNOWN_TERMS:
        if term in title:
            words.add(term)
    return words


# Known Chinese compound terms for trending extraction (curated, not bigrams)
_CN_KNOWN_TERMS = {
    # AI core concepts
    "大模型", "大语言模型", "多模态", "生成式", "预训练", "微调", "蒸馏",
    "推理", "训练", "对齐", "强化学习", "注意力机制", "上下文窗口",
    # Agent & applications
    "智能体", "多智能体", "工作流", "自动化", "代码生成", "代码审查",
    "知识图谱", "向量数据库", "检索增强", "提示工程", "函数调用",
    # Companies & products
    "谷歌", "百度", "腾讯", "阿里", "字节", "华为", "苹果", "微软", "英伟达",
    "开源", "闭源",
    # Industry
    "融资", "估值", "芯片", "算力", "数据中心", "端侧", "云端",
    "安全", "隐私", "版权", "监管",
}


def update_indexes(date_str):
    """Generate by-category.json and trending.json from recent data."""
    indexes_dir = os.path.join(HARVEST_DIR, "indexes")
    os.makedirs(indexes_dir, exist_ok=True)

    # --- by-category.json (30 days, score >= 75) ---
    articles_30d = load_recent_data(30)
    categories = {}
    for a in articles_30d:
        if a.get("score", 0) < 75:
            continue
        cat = a.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "title": a["title"],
            "link": a["link"],
            "source": a.get("source", ""),
            "score": a["score"],
            "verdict": a.get("verdict", ""),
            "pub_date": a.get("pub_date", ""),
            "why_matters": a.get("why_matters", ""),
        })

    # Sort each category by score desc
    for cat in categories:
        categories[cat].sort(key=lambda x: x["score"], reverse=True)

    cat_output = {"updated": date_str, "categories": categories}
    cat_path = os.path.join(indexes_dir, "by-category.json")
    with open(cat_path, "w", encoding="utf-8") as f:
        json.dump(cat_output, f, ensure_ascii=False, indent=2)

    total_indexed = sum(len(v) for v in categories.values())
    print(f"  [ok] {cat_path} ({len(categories)} categories, {total_indexed} articles)")

    # --- trending.json (7-day keyword frequency) ---
    articles_7d = load_recent_data(7)
    quality_7d = [a for a in articles_7d if a.get("score", 0) >= 70]

    keyword_counts = {}
    for a in quality_7d:
        for kw in extract_keywords(a.get("title", "")):
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

    # Sort by count, take top 20
    sorted_kw = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    # Filter: at least 2 mentions
    trending_list = [
        {"keyword": kw, "count": cnt}
        for kw, cnt in sorted_kw
        if cnt >= 2
    ][:20]

    trending_output = {
        "updated": date_str,
        "window": "7d",
        "article_count": len(quality_7d),
        "trending": trending_list,
    }
    trending_path = os.path.join(indexes_dir, "trending.json")
    with open(trending_path, "w", encoding="utf-8") as f:
        json.dump(trending_output, f, ensure_ascii=False, indent=2)
    print(f"  [ok] {trending_path} ({len(trending_list)} keywords)")


def generate_csv(jsonl_path):
    """Regenerate CSV from JSONL for Excel users. Full rebuild each time."""
    csv_path = jsonl_path.replace(".jsonl", ".csv")
    fieldnames = [
        "date", "title", "source", "channel", "category",
        "score", "verdict", "level", "summary", "why_matters",
        "highlights", "core_point", "link",
    ]

    rows = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows.append({
                "date": a.get("pub_date", ""),
                "title": a.get("title", ""),
                "source": a.get("source", ""),
                "channel": a.get("source_channel", ""),
                "category": a.get("category", ""),
                "score": a.get("score", 0),
                "verdict": a.get("verdict", ""),
                "level": a.get("level", ""),
                "summary": a.get("summary", ""),
                "why_matters": a.get("why_matters", ""),
                "highlights": " | ".join(a.get("highlights", [])),
                "core_point": a.get("core_point", ""),
                "link": a.get("link", ""),
            })

    # Sort by date desc, then score desc for human browsing
    rows.sort(key=lambda r: (r["date"], r["score"]), reverse=True)

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  [ok] {csv_path} ({len(rows)} rows)")


def generate_folder_readmes():
    """Generate README.md for api/ and digest/ with reverse-chronological file lists."""
    # --- api/ README ---
    api_dir = os.path.join(HARVEST_DIR, "api")
    json_files = sorted(
        [f for f in os.listdir(api_dir) if f.endswith(".json")],
        reverse=True,
    )
    lines = [
        "# API Data — for Agents",
        "",
        "Full article data with all analysis fields. One JSON file per day.",
        "",
        "| Date | Articles | Must Read |",
        "|------|----------|-----------|",
    ]
    for fname in json_files:
        fpath = os.path.join(api_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            total = data.get("total", 0)
            must_read = data.get("verdict_counts", {}).get("must_read", 0)
        except Exception as e:
            print(f"  [warn] Failed to read {fpath}: {e}", file=sys.stderr)
            total = "?"
            must_read = "?"
        date = fname.replace(".json", "")
        lines.append("| [{}]({}) | {} | {} |".format(date, fname, total, must_read))

    readme_path = os.path.join(api_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  [ok] {readme_path}")

    # --- digest/ README ---
    digest_dir = os.path.join(HARVEST_DIR, "digest")
    # Collect all .md files from monthly subdirectories
    all_files = []  # list of (date_str, relative_path)
    for entry in sorted(os.listdir(digest_dir), reverse=True):
        sub = os.path.join(digest_dir, entry)
        if os.path.isdir(sub) and entry.startswith("20"):
            for fname in os.listdir(sub):
                if fname.endswith(".md"):
                    all_files.append((fname.replace(".md", ""), f"{entry}/{fname}"))
    all_files.sort(key=lambda x: x[0], reverse=True)

    # Group by month
    months = {}  # "2026-02" -> [(date_str, rel_path), ...]
    for date_str_f, rel_path in all_files:
        month_key = date_str_f[:7]
        months.setdefault(month_key, []).append((date_str_f, rel_path))

    lines = [
        "# 每日日报 / Daily Digest",
        "",
        "每天一份结构化 AI 日报，按 verdict 分组，人类可读。",
        "",
        "---",
    ]
    for month_key in sorted(months.keys(), reverse=True):
        y, m = month_key.split("-")
        lines.append("")
        lines.append(f"## {y} 年 {int(m)} 月")
        lines.append("")
        lines.append("| 日期 | 日报 | 说明 |")
        lines.append("|------|------|------|")
        for date_str_f, rel_path in months[month_key]:
            day = date_str_f[5:]  # "02-27"
            fname = os.path.basename(rel_path)
            lines.append(f"| {day} | [{fname}]({rel_path}) | |")

    readme_path = os.path.join(digest_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  [ok] {readme_path}")


def main():
    # Parse date argument
    date_str = datetime.now().strftime("%Y-%m-%d")
    if "--date" in sys.argv:
        idx = sys.argv.index("--date")
        if idx + 1 < len(sys.argv):
            date_str = sys.argv[idx + 1]

    print(f"AI Daily Harvest — publishing {date_str}")

    # Ensure output dirs exist
    for subdir in ["api", "digest", "lists", "sources", "datasets", "feeds", "indexes"]:
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

    # Generate outputs (existing)
    generate_json(all_articles, date_str)
    generate_daily_picks(all_articles, date_str)
    generate_markdown(all_articles, date_str)
    update_source_stats(all_articles, date_str)

    # Generate new outputs
    jsonl_path = append_dataset(all_articles, date_str)
    generate_csv(jsonl_path)
    generate_rss(all_articles, date_str)
    update_indexes(date_str)
    generate_folder_readmes()

    # Summary
    verdicts = {}
    for a in all_articles:
        v = a["verdict"]
        verdicts[v] = verdicts.get(v, 0) + 1
    v_summary = ", ".join(f"{v}={c}" for v, c in sorted(verdicts.items()))
    print(f"Done. {len(all_articles)} articles published. [{v_summary}]")


if __name__ == "__main__":
    main()
