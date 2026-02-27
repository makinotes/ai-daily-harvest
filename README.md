# AI Daily Feed

> **40+ AI 信源，一份结构化日报，工作日持续更新。** 评分、分类、开箱即用——人看摘要，Agent 吃 JSON，不用自己建爬虫。

## 为什么做这个

自己每天要看 40+ 信源，手动刷太慢，就搭了个管道自动抓、评分、结构化。既然已经在跑了，顺手公开，边际成本为零。

**"我自己用 xx 爬虫搭一个不就行了？"** ——当然可以。但筛选 40+ 信源、维护挂掉的 RSS、对每篇文章跑结构化分析、然后每个工作日坚持更新几个月——大多数人第三天就不想干了。

信源持续新增中，欢迎通过 [issue](../../issues/new) 推荐。

[English →](README_EN.md)

## 你能得到什么

**读者** — 不用刷 40+ 信源，看一份日报就够。每篇文章都有一句话摘要和"为什么重要"，几秒钟就能判断值不值得点进去。打开 [`digest/`](digest/) 直接看，RSS 订阅 [`feeds/rss.xml`](feeds/rss.xml)，每周趋势看 [`feeds/weekly/`](feeds/weekly/)。

**Agent 开发者** — 不用自己建抓取管道，直接给 Agent 喂每日知识更新。每篇文章预提取了关键要点（`highlights`）、结构化推理（`core_point`：论点 → 论据 → 启示）、实践意义（`why_matters`）。用 verdict 决定 Agent 先处理什么，用 category 按领域积累知识。拿 [`lists/daily-picks.json`](lists/daily-picks.json) 看今天的精选，或者 [`api/{date}.json`](api/) 取完整数据。

**模型训练** — 一个带标注的内容质量数据集。每篇文章有多维度评分、verdict 标签、结构化分析字段，可以用来训练评分模型、摘要生成、内容分类。下载 [`datasets/scored-articles.jsonl`](datasets/scored-articles.jsonl)，也有 [`CSV 版本`](datasets/scored-articles.csv) 可直接用 Excel 打开。

## 快速开始

```bash
# 今天的精选，按 verdict 分组
curl -s https://raw.githubusercontent.com/makinotes/ai-daily-feed/master/lists/daily-picks.json | jq '.must_read'

# 某天的完整数据（替换为任意可用日期）
curl -s https://raw.githubusercontent.com/makinotes/ai-daily-feed/master/api/$(date +%Y-%m-%d).json

# 按分类看最近 30 天
curl -s https://raw.githubusercontent.com/makinotes/ai-daily-feed/master/indexes/by-category.json | jq '.categories["AI/Tech"][:3]'

# 这周在聊什么
curl -s https://raw.githubusercontent.com/makinotes/ai-daily-feed/master/indexes/trending.json
```

给 LLM 看：[`llms.txt`](llms.txt) 快速了解，[`llms-full.txt`](llms-full.txt) 完整指南。

## 数据规模

| 指标 | 数值 |
|------|------|
| 信源 | 40+（英文 tech blog + 微信公众号 AI 账号）|
| 每日文章 | 过滤后约 25-40 篇 |
| 累计数据集 | 427+ 篇带标注文章 |
| 历史 | 2026-01-26 起，工作日更新 |
| 缺失 | 部分日期可能缺失（节假日、维护）|

## 文件说明

| 路径 | 受众 | 内容 |
|------|------|------|
| `api/{date}.json` | Agent | 完整文章数据，含所有分析字段 |
| `digest/{date}.md` | 人 | 可读日报，按 verdict 分组 |
| `lists/daily-picks.json` | 通用 | 今日精选 |
| `datasets/scored-articles.jsonl` | 模型 | 累积数据集（JSONL + CSV）|
| `feeds/rss.xml` | 人 | RSS 订阅，滚动 50 条 |
| `feeds/weekly/{year}-W{week}.md` | 人 | 周报 + 趋势分析 |
| `indexes/by-category.json` | Agent | 30 天分类索引 |
| `indexes/trending.json` | Agent | 7 天热词 |

## Verdict 体系

| Verdict | 意思 |
|---------|------|
| **must_read** | 质量高，有新东西 |
| **worth_reading** | 有深度或新意 |
| **neutral** | 还行，没啥特别 |
| **noise** | 信噪比低 |
| **overhyped** | 看着重要其实没料 |

## 文章 Schema

```json
{
  "title": "文章标题",
  "link": "https://...",
  "source": "来源名",
  "source_channel": "overseas | wechat-ai",
  "category": "AI/Tech | Builder 实践 | AI 使用",
  "pub_date": "2026-02-27",
  "summary": "一句话摘要",
  "core_point": "论点 → 论据 → 启示",
  "highlights": ["关键要点 1", "关键要点 2"],
  "why_matters": "跟你有什么关系、怎么用",
  "score": 85,
  "level": "精读 | 收藏 | 速览",
  "verdict": "must_read"
}
```

## 运作方式

```
40+ 信源 → 每日抓取 → 去重 → 多维度评分 → Verdict 判定 → 发布
```

评分算法多维度（新颖度、深度、可信度、信噪比），信源精选高信噪比的。同一管道出三种格式：JSON、Markdown、JSONL。

## 参与贡献

**推荐信源** — [提 issue](../../issues/new)，写上来源名、URL、语言、为什么好。

**反馈质量** — 评分不对或分类错误？提 issue，注明日期和标题。

**基于数据构建** — JSON 可编程消费，做了什么有意思的东西可以告诉我们。

## License

文章元数据和 AI 分析内容遵循 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)。**非商业用途，仅限个人使用。** 原始内容版权归原作者。如果您是内容所有者并希望移除相关文章，请[提 issue](../../issues/new)。

---

马奇诺的个人 AI 基础设施项目。

<img src="assets/wechat-qr.png" alt="公众号二维码" width="200">
