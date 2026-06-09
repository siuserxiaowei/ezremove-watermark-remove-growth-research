#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"
SOURCE = ROOT / "content" / "curated-report.md"
REPORT = DOCS / "ezremove-watermark-remove-growth-research.md"


def markdown_to_html(markdown: str) -> str:
    result = subprocess.run(
        ["pandoc", "-f", "gfm", "-t", "html"],
        input=markdown,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def build_html(markdown: str) -> str:
    body = markdown_to_html(markdown)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EzRemove 增长研究：遗产内容完整拆解</title>
  <style>
    :root {{
      --ink: #111827;
      --muted: #4b5563;
      --line: #d8dee9;
      --accent: #0f766e;
      --bg: #f8fafc;
      --panel: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.72;
    }}
    header {{
      background: #0f172a;
      color: white;
      padding: 44px 24px 34px;
      border-bottom: 4px solid var(--accent);
    }}
    .wrap {{ width: min(1180px, calc(100% - 42px)); margin: 0 auto; }}
    header h1 {{ margin: 0 0 12px; font-size: clamp(32px, 5vw, 56px); line-height: 1.1; letter-spacing: 0; }}
    header p {{ margin: 0; color: #dbeafe; font-size: 18px; max-width: 880px; }}
    main {{ padding: 28px 0 72px; }}
    article {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 34px;
      overflow-wrap: anywhere;
    }}
    h1 {{ font-size: 36px; line-height: 1.18; letter-spacing: 0; }}
    h2 {{ margin-top: 42px; padding-top: 16px; border-top: 1px solid var(--line); font-size: 28px; letter-spacing: 0; }}
    h3 {{ margin-top: 26px; font-size: 21px; }}
    p, li {{ font-size: 16px; }}
    a {{ color: var(--accent); }}
    blockquote, callout {{
      display: block;
      margin: 18px 0;
      padding: 14px 18px;
      border-left: 4px solid var(--accent);
      background: #f0fdfa;
      color: #334155;
      white-space: pre-line;
    }}
    callout::before {{
      content: attr(emoji) " 原文材料";
      display: block;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 8px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      display: block;
      overflow-x: auto;
      margin: 18px 0 26px;
      font-size: 14px;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 9px 10px;
      vertical-align: top;
      white-space: normal;
      text-align: left;
    }}
    th {{ background: #f1f5f9; }}
    code {{
      background: #eef2f7;
      padding: 2px 5px;
      border-radius: 4px;
      font-size: .92em;
    }}
    img {{
      display: block;
      max-width: min(100%, 920px);
      height: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 18px 0 10px;
      background: #f8fafc;
    }}
    @media (max-width: 760px) {{
      article {{ padding: 22px; }}
      h1 {{ font-size: 28px; }}
      h2 {{ font-size: 23px; }}
      th, td {{ white-space: normal; min-width: 120px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>遗产内容完整拆解</h1>
      <p>基于 X/Twitter 原文素材、外部资料和案例研究，重写成 EzRemove 可执行的 SEO / PR / GEO 增长判断。</p>
    </div>
  </header>
  <main class="wrap">
    <article>
{body}
    </article>
  </main>
</body>
</html>
"""


def build_readme() -> str:
    return """# EzRemove `watermark remove` 增长研究

本仓库保存对 ZaneWynn_SEO 公开内容的结构化拆解，并映射到 EzRemove 的 `watermark remove` 增长执行方案。

- 完整 Markdown 文档：[docs/ezremove-watermark-remove-growth-research.md](docs/ezremove-watermark-remove-growth-research.md)
- GitHub Pages 入口：[docs/index.html](docs/index.html)
- 内容源：[content/curated-report.md](content/curated-report.md)
- 目标站点：[https://ezremove.ai/](https://ezremove.ai/)

公开网页保留原文材料、配图、评论/引用洞察、结构化拆解和 EzRemove 执行映射；抓取过程、逐屏日志、楼层流水账等调试信息不进入最终页面。
"""


def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)
    SITE.mkdir(parents=True, exist_ok=True)
    markdown = SOURCE.read_text(encoding="utf-8")
    REPORT.write_text(markdown, encoding="utf-8")
    html = build_html(markdown)
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    (SITE / "index.html").write_text(html, encoding="utf-8")
    (ROOT / "README.md").write_text(build_readme(), encoding="utf-8")
    print(REPORT)
    print(DOCS / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
