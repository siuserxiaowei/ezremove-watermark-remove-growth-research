#!/usr/bin/env python3
"""Build public Markdown and HTML research artifacts."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"
PROCESSED = ROOT / "data" / "processed"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_num(value):
    return "" if value is None else str(value)


def build_source_table(x_manifest: dict, browser_manifest: dict) -> str:
    browser_by_id = {item["tweet_id"]: item for item in browser_manifest["items"]}
    rows = [
        "| 资料 | 来源 | Views | Likes | Bookmarks | Replies | Quotes | 已抓对话/回复候选 | 已抓引用候选 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in x_manifest["items"]:
        browser = browser_by_id.get(item["tweet_id"], {})
        metrics = item.get("main_metrics", {})
        rows.append(
            "| {label} | [X]({url}) | {views} | {likes} | {bookmarks} | {replies} | {quotes} | {reply_fetched} | {quote_fetched} |".format(
                label=item["label"],
                url=item["source_url"],
                views=fmt_num(metrics.get("views")),
                likes=fmt_num(metrics.get("likes")),
                bookmarks=fmt_num(metrics.get("bookmarks")),
                replies=fmt_num(metrics.get("replies")),
                quotes=fmt_num(metrics.get("quotes")),
                reply_fetched=fmt_num(browser.get("reply_candidates_fetched")),
                quote_fetched=fmt_num(browser.get("quote_candidates_fetched")),
            )
        )
    return "\n".join(rows)


def semrush_summary() -> dict:
    return {
        "date": "2026-06-07",
        "overview_url": "https://www.semrush.com/analytics/overview/?q=ezremove.ai&searchType=domain",
        "backlinks_url": "https://www.semrush.com/analytics/backlinks/overview/?q=ezremove.ai&searchType=domain",
        "authority_score": "48",
        "organic_traffic": "640K (+16%)",
        "organic_keywords": "94.9K (-1.9%)",
        "paid_traffic": "0",
        "ref_domains": "1.3K",
        "backlinks": "22.4K",
        "top_keywords": [
            ("watermark remover", "I", "5", "110K", "$0.59", "5.13%"),
            ("ai image editor", "C", "5", "90.5K", "$0.76", "4.22%"),
            ("delete watermark photo", "C", "1", "14.8K", "$0.72", "3.89%"),
            ("ezremove", "N", "1", "4.4K", "$5.27", "3.73%"),
            ("remove watermark", "I", "3", "40.5K", "$0.65", "3.52%"),
        ],
        "top_linked_pages": [
            ("https://ezremove.ai/", "773"),
            ("https://ezremove.ai/video-watermark-remover/", "286"),
            ("https://ezremove.ai/photo-enhancer/", "172"),
            ("https://ezremove.ai/watermark-remover/", "167"),
            ("https://ezremove.ai/magic-eraser/", "162"),
        ],
        "mcp_note": "Semrush 网页登录态可用；Semrush MCP 返回当前套餐不包含 MCP Access。",
    }


def build_markdown(x_manifest: dict, browser_manifest: dict) -> str:
    s = semrush_summary()
    total_replies = sum(item.get("reply_candidates_fetched", 0) for item in browser_manifest["items"])
    total_quotes = sum(item.get("quote_candidates_fetched", 0) for item in browser_manifest["items"])
    total_network = sum(item.get("network_response_count", 0) for item in browser_manifest["items"])

    keyword_rows = "\n".join(
        f"| {kw} | {intent} | {pos} | {vol} | {cpc} | {traffic} |"
        for kw, intent, pos, vol, cpc, traffic in s["top_keywords"]
    )
    link_rows = "\n".join(f"| [{url}]({url}) | {refs} |" for url, refs in s["top_linked_pages"])

    return f"""# EzRemove `watermark remove` 增长研究：术法道器势拆解

> 目标站点：[https://ezremove.ai/](https://ezremove.ai/)  
> 目标词：`watermark remove`  
> 输出日期：2026-06-08  
> 公开版说明：本报告分析了可访问的 X/Twitter 主贴、回复、引用搜索与 Semrush 网页数据。原始 X 响应仅保存在本地 `data/raw`，公开文档只保留来源链接、指标、摘要和短摘录，避免整段复制平台内容。

## 结论

EzRemove 当前不是“刚起步站”，而是已经具备较强自然搜索资产的站点。Semrush 页面在 2026-06-07 显示：Authority Score {s["authority_score"]}、自然流量 {s["organic_traffic"]}、自然关键词 {s["organic_keywords"]}、Referring Domains {s["ref_domains"]}、Backlinks {s["backlinks"]}。因此下一阶段不应把重点放在“虚假刷搜索”，而应把 PR、KOL、免费工具和内容集群合起来，制造真实品牌搜索需求，并把权重导向 `watermark remover / remove watermark / watermark remove` 这一组核心商业词。

“PR 刷词”的可复刻部分是：先用免费工具降低体验门槛，再通过真实 KOL 和社媒内容形成品牌记忆，最后用内容集群、垂直外链和站内转化承接需求。不可复刻也不建议做的是机器人搜索、虚假点击、低质账号矩阵和规避平台风控。

## 数据来源

X/Twitter 抓取结果：12 条核心资料，浏览器登录态抓到 {total_network} 个 GraphQL 网络响应，解析出 {total_replies} 条对话/回复候选、{total_quotes} 条引用候选。Semrush MCP 当前套餐不可用，但网页登录态可打开 Domain Overview 与 Backlink Overview；Organic Positions 页面被套餐/营销页挡住。

{build_source_table(x_manifest, browser_manifest)}

## Semrush 关键事实

来源：[{s["overview_url"]}]({s["overview_url"]})、[{s["backlinks_url"]}]({s["backlinks_url"]})。数据日期：{s["date"]}。

| 指标 | 数值 |
|---|---:|
| Authority Score | {s["authority_score"]} |
| Organic Traffic | {s["organic_traffic"]} |
| Organic Keywords | {s["organic_keywords"]} |
| Paid Traffic | {s["paid_traffic"]} |
| Referring Domains | {s["ref_domains"]} |
| Backlinks | {s["backlinks"]} |

Top Organic Keywords（US 卡片）：

| Keyword | Intent | Pos. | Volume | CPC | Traffic % |
|---|---:|---:|---:|---:|---:|
{keyword_rows}

Backlink Overview 显示的 Top Pages：

| URL | Referring Domains |
|---|---:|
{link_rows}

## 作者 SEO 框架复盘

1. 选词是 SEO 的第一层杠杆。核心词用于首页和功能落地页，非核心词用于博客、对比页、教程页和场景页，后者通过内链把权重传给核心页。
2. 新站优先打难度低但需求明确、趋势上升的词。Semrush 只是第三方估算，仍要用 Google Trends、GSC 和真实 SERP 做二次确认。
3. 竞品品牌词可以做，但要做成事实型对比、替代方案和迁移教程，不应伪装成对方官网，也不要误导用户。
4. 外链的关键不是数量，而是垂直相关性和带来的真实用户质量。低相关流量如果停留差，可能反而拖累站点质量信号。
5. 产品和流量不是二选一。产品达到行业平均后，流量与营销决定增长上限；产品体验决定转化和复购下限。
6. 社媒冷启动不能完全照搬 SEO 逻辑。小红书、X、YouTube 等平台更偏内容供给和需求创造，SEO 更偏需求承接。
7. 没有直接数据的平台，可以用相邻平台、竞品词、搜索建议和成交端数据做代理判断。

## EzRemove 可执行方案

### 1. 首页与核心页

首页继续承接大词，不要频繁改 URL。核心页建议保持并强化：

- `/watermark-remover/`：主承接 `watermark remover`、`watermark remove`、`remove watermark`。
- `/video-watermark-remover/`：承接 video 场景，继续争取视频类外链。
- `/photo-enhancer/`、`/magic-eraser/`：作为横向工具页，给主词页传递内链。
- 新增或强化：`remove watermark from image`、`remove watermark from video`、`remove logo from photo`、`remove tiktok watermark`、`remove text from image`、`watermark remover online free`。

每个核心页都要有：上传入口、示例前后对比、适用场景、限制说明、FAQ、HowTo Schema、SoftwareApplication Schema、指向相关工具页的内链。

### 2. 内容集群

围绕 `watermark remove` 先做三层内容：

- 需求层：how to remove watermark from photo/video/pdf、free watermark remover、online watermark remover。
- 对比层：EzRemove vs alternatives、best watermark remover、brand alternatives。
- 问题层：is it legal、quality loss、batch remove、AI watermark、logo/text/date stamp removal。

文章不要只堆关键词。每篇至少要有实际步骤、截图或示例、适用/不适用边界、工具入口和内链。

### 3. PR 与 KOL

推荐执行“真实品牌搜索”而不是“刷搜索”：

- 中小 KOL 重点找图片编辑、跨境电商、短视频剪辑、设计工具、学生作业和社媒运营账号。
- 视频标题和口播可以强调 `ezremove` 品牌名，但 CTA 应该是“搜索或访问 EzRemove 体验免费工具”，不要求用户做虚假搜索。
- KOL 链接必须带 UTM，落地页可做免费额度或模板包，方便区分真实转化。
- 前 2 周以免费体验和口碑扩散为目标，不急着限流；数据稳定后再做商业化限制。

### 4. 外链

优先级从高到低：

1. 垂直工具目录、AI 图片编辑目录、视频剪辑教程站。
2. KOL 的教程稿、YouTube 描述、博客复盘、Newsletter。
3. 可被引用的数据页，如“watermark remover comparison benchmark”。
4. 开源/模板资源页，如示例素材、批处理脚本、API 文档。

不要买大量无关站群链接。链接带来的用户停留、二跳和转化比 DA 数字更重要。

### 5. GEO / AI Search

面向 ChatGPT、Gemini、AI Overview 的页面要短句清楚、答案前置、实体一致：

- 建立 `About EzRemove`、`How EzRemove works`、`EzRemove alternatives`、`Watermark removal FAQ`。
- 每页明确产品实体：EzRemove 是在线 AI watermark remover，支持图片/视频场景，提供免费入口。
- FAQ 用自然问法：`What is the best free watermark remover?`、`Can EzRemove remove watermark from video?`。
- 保持品牌、URL、功能描述在站内、社媒、目录站和 PR 稿中一致。

## 术法道器势

### 术

用免费工具完成低摩擦体验，用 KOL 和内容制造品牌记忆，用 SEO 页面承接搜索需求，用内链和外链把非核心流量传到核心商业页。

### 法

选词分层、页面分工、内容集群、真实 KOL 传播、垂直外链、GSC/Semrush 复盘、转化漏斗优化。每个动作都要能落到关键词、页面、渠道、指标四张表。

### 道

增长的底线是真实用户价值。可以引导用户搜索品牌，但不能依赖虚假点击和机器人行为。长期排名靠可用工具、可验证内容、相关链接和正向用户行为。

### 器

Semrush、Google Search Console、GA4、Google Trends、Ahrefs/DataForSEO、X 抓取脚本、UTM、Looker Studio、飞书周报、GitHub 研究仓库。

### 势

AI 图片编辑、短视频剪辑、电商素材处理和社媒内容生产仍在增长。`watermark remover` 已有大词资产，`ezremove` 品牌词也有搜索量，下一阶段的机会是把免费工具的传播势能转成品牌搜索和核心词排名稳定性。

## 30/60/90 天计划

30 天：完成追踪基建、核心页改版、10 篇高意图内容、20 个 KOL 小样本投放、GSC/Semrush 基线表。

60 天：扩展到 40-60 篇内容，跑出 3-5 个有效 KOL 垂类，建立对比页和工具目录外链，优化免费额度与注册转化。

90 天：沉淀品牌搜索资产，做横向工具矩阵，建立 AI Search/GEO 页面，按国家和语言扩展高 ROI 页面。

## 验收指标

- `ezremove` 品牌词搜索量和 GSC impressions 持续增长。
- `watermark remover`、`remove watermark`、`watermark remove` 维持或提升排名。
- 核心页自然流量、上传成功率、注册率、付费转化率同步提升。
- KOL 渠道产生可归因访问和品牌搜索提升，而不是只有短期点击。
- 新增外链来自垂直相关页面，并能带来真实访问。
"""


def build_html(markdown: str) -> str:
    cards = [
        ("术", "免费工具 + KOL + 品牌搜索", "把低摩擦体验变成真实需求，而不是虚假点击。"),
        ("法", "选词分层 + 内容集群 + 内外链", "每个动作都映射到关键词、页面、渠道和指标。"),
        ("道", "真实用户价值", "排名增长建立在可用工具、可信内容和相关链接上。"),
        ("器", "Semrush / GSC / GA4 / 抓取脚本", "用数据判断词、页、渠道和转化，不凭感觉。"),
        ("势", "AI 图片编辑需求上升", "把免费工具传播势能转化为品牌搜索和核心词稳定性。"),
    ]
    card_html = "\n".join(
        f"<section class='card'><div class='glyph'>{html.escape(k)}</div><h2>{html.escape(t)}</h2><p>{html.escape(d)}</p></section>"
        for k, t, d in cards
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EzRemove watermark remove 增长拆解：术法道器势</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #14213d;
      --muted: #5d6472;
      --line: #d9dee8;
      --accent: #0d9488;
      --accent-2: #f59e0b;
      --bg: #f7f8fb;
      --panel: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.65;
    }}
    header {{
      background: #0f172a;
      color: #fff;
      padding: 56px 24px 40px;
    }}
    .wrap {{ width: min(1120px, calc(100% - 40px)); margin: 0 auto; }}
    h1 {{ margin: 0 0 14px; font-size: clamp(32px, 5vw, 56px); line-height: 1.08; letter-spacing: 0; }}
    .lead {{ max-width: 820px; color: #d8dee9; font-size: 18px; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }}
    .pill {{ border: 1px solid rgba(255,255,255,.25); padding: 7px 11px; border-radius: 6px; color: #eef2ff; }}
    main {{ padding: 36px 0 64px; }}
    .grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 26px; }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      min-height: 210px;
    }}
    .glyph {{
      width: 44px;
      height: 44px;
      border-radius: 6px;
      display: grid;
      place-items: center;
      background: #ccfbf1;
      color: #115e59;
      font-weight: 800;
      font-size: 22px;
      margin-bottom: 14px;
    }}
    .card h2 {{ font-size: 18px; line-height: 1.25; margin: 0 0 10px; }}
    .card p {{ margin: 0; color: var(--muted); font-size: 14px; }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 26px;
      margin: 16px 0;
    }}
    .metrics {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; }}
    .metric {{ border-left: 4px solid var(--accent); background: #f8fafc; padding: 14px; }}
    .metric b {{ display: block; font-size: 24px; }}
    .metric span {{ color: var(--muted); font-size: 13px; }}
    h2 {{ margin-top: 0; letter-spacing: 0; }}
    ul {{ padding-left: 20px; }}
    a {{ color: #0f766e; }}
    @media (max-width: 900px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .metrics {{ grid-template-columns: 1fr 1fr; }}
      header {{ padding-top: 38px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>EzRemove 增长拆解：术法道器势</h1>
      <p class="lead">目标词 <strong>watermark remove</strong>。这份在线版把 X/Twitter 资料、Semrush 数据和可执行 SEO/PR/GEO 方案压缩成一个决策视图。</p>
      <div class="meta">
        <span class="pill">站点：ezremove.ai</span>
        <span class="pill">关键词：watermark remove</span>
        <span class="pill">日期：2026-06-08</span>
      </div>
    </div>
  </header>
  <main class="wrap">
    <div class="grid">{card_html}</div>
    <section class="panel">
      <h2>当前 Semrush 基线</h2>
      <div class="metrics">
        <div class="metric"><b>48</b><span>Authority Score</span></div>
        <div class="metric"><b>640K</b><span>Organic Traffic</span></div>
        <div class="metric"><b>94.9K</b><span>Organic Keywords</span></div>
        <div class="metric"><b>1.3K</b><span>Ref. Domains</span></div>
        <div class="metric"><b>22.4K</b><span>Backlinks</span></div>
        <div class="metric"><b>#3</b><span>remove watermark</span></div>
      </div>
    </section>
    <section class="panel">
      <h2>核心判断</h2>
      <ul>
        <li>EzRemove 已经有搜索资产，下一阶段应做真实品牌需求和核心页稳定性，而不是虚假搜索。</li>
        <li>免费工具是传播钩子，KOL 是需求放大器，SEO 页面是承接器，内外链是权重分配器。</li>
        <li>GEO 要让 AI 搜索能稳定识别 EzRemove 的实体、功能、场景和替代关系。</li>
      </ul>
    </section>
    <section class="panel">
      <h2>90 天打法</h2>
      <ul>
        <li>30 天：核心页、追踪、10 篇高意图内容、20 个 KOL 小样本。</li>
        <li>60 天：扩展内容集群和垂直外链，筛出有效 KOL 垂类。</li>
        <li>90 天：沉淀品牌搜索资产，扩展多语言/多场景工具矩阵。</li>
      </ul>
    </section>
    <section class="panel">
      <h2>完整文档</h2>
      <p>完整 Markdown 研究文档见 <a href="./ezremove-watermark-remove-growth-research.md">ezremove-watermark-remove-growth-research.md</a>。</p>
    </section>
  </main>
</body>
</html>
"""


def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)
    SITE.mkdir(parents=True, exist_ok=True)
    x_manifest = load_json(PROCESSED / "x_crawl_manifest.json")
    browser_manifest = load_json(PROCESSED / "x_browser_crawl_manifest.json")
    markdown = build_markdown(x_manifest, browser_manifest)
    public_metrics = {
        "generated_at": "2026-06-08",
        "site": "https://ezremove.ai/",
        "target_keyword": "watermark remove",
        "x_sources": [
            {
                "label": item["label"],
                "tweet_id": item["tweet_id"],
                "source_url": item["source_url"],
                "metrics": item.get("main_metrics", {}),
                "conversation_or_reply_candidates_fetched": next(
                    (
                        browser_item.get("reply_candidates_fetched", 0)
                        for browser_item in browser_manifest["items"]
                        if browser_item["tweet_id"] == item["tweet_id"]
                    ),
                    0,
                ),
                "quote_candidates_fetched": next(
                    (
                        browser_item.get("quote_candidates_fetched", 0)
                        for browser_item in browser_manifest["items"]
                        if browser_item["tweet_id"] == item["tweet_id"]
                    ),
                    0,
                ),
            }
            for item in x_manifest["items"]
        ],
        "semrush": semrush_summary(),
    }
    (DOCS / "ezremove-watermark-remove-growth-research.md").write_text(markdown, encoding="utf-8")
    (ROOT / "README.md").write_text(markdown.split("## 数据来源")[0], encoding="utf-8")
    html_doc = build_html(markdown)
    (SITE / "index.html").write_text(html_doc, encoding="utf-8")
    (DOCS / "index.html").write_text(html_doc, encoding="utf-8")
    (PROCESSED / "public_metrics.json").write_text(
        json.dumps(public_metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(DOCS / "ezremove-watermark-remove-growth-research.md")
    print(SITE / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
