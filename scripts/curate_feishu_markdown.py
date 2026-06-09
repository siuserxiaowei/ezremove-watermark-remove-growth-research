#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import mimetypes
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MEDIA_DIR = DOCS / "assets" / "feishu-media"
CONTENT_DIR = ROOT / "content"
OUTPUT = CONTENT_DIR / "curated-report.md"

IMAGE_RE = re.compile(r"!\[([^\]]*)\]\((https://internal-api-drive-stream\.feishu\.cn/[^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

SKIP_SECTION_TITLES = {
    "浏览器逐屏可见内容归档",
    "逐屏可见内容归档",
    "主贴与楼层逐条拆解",
    "主贴与楼层拆解",
    "抓取结论",
}

SKIP_PREFIXES = (
    "- 抓取结构：",
    "- 媒体：已归档",
    "- 逐屏可见归档：",
    "- 抓取方式：",
    "- 原始 raw：",
    "- 本轮抓取统计：",
    "- 逐屏可见统计：",
    "- 结构化结果：",
)


def suffix_from_headers(headers: object) -> str:
    content_type = ""
    if hasattr(headers, "get_content_type"):
        content_type = headers.get_content_type()
    elif hasattr(headers, "get"):
        content_type = headers.get("Content-Type", "").split(";", 1)[0].strip()
    suffix = mimetypes.guess_extension(content_type or "") or ".jpg"
    if suffix == ".jpe":
        suffix = ".jpg"
    return suffix


def download_image(url: str, index: int) -> str:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    existing = sorted(MEDIA_DIR.glob(f"feishu_{index:03d}_{digest}.*"))
    if existing:
        return f"assets/feishu-media/{existing[0].name}"

    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
        suffix = suffix_from_headers(response.headers)
    filename = f"feishu_{index:03d}_{digest}{suffix}"
    (MEDIA_DIR / filename).write_bytes(data)
    return f"assets/feishu-media/{filename}"


def localize_images(markdown: str) -> str:
    seen: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        alt, url = match.group(1), match.group(2)
        if url not in seen:
            try:
                seen[url] = download_image(url, len(seen) + 1)
            except Exception:
                seen[url] = url
        return f"![{alt}]({seen[url]})"

    return IMAGE_RE.sub(replace, markdown)


def split_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def join_markdown_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def filter_public_shortline_table(lines: list[str], start: int) -> tuple[list[str], int]:
    output: list[str] = []
    header = split_markdown_row(lines[start])
    drop_indexes = [idx for idx, cell in enumerate(header) if "公开短线索" in cell]
    keep_indexes = [idx for idx in range(len(header)) if idx not in drop_indexes]
    output.append(join_markdown_row([header[idx] for idx in keep_indexes]))
    output.append(join_markdown_row(["---"] * len(keep_indexes)))

    index = start + 2
    while index < len(lines) and lines[index].lstrip().startswith("|"):
        cells = split_markdown_row(lines[index])
        if len(cells) >= len(header):
            output.append(join_markdown_row([cells[idx] for idx in keep_indexes if idx < len(cells)]))
        index += 1
    return output, index


def filter_markdown(markdown: str) -> str:
    lines = markdown.splitlines()
    output: list[str] = []
    skip_level: int | None = None
    index = 0

    while index < len(lines):
        line = lines[index]
        heading = HEADING_RE.match(line)

        if skip_level is not None:
            if heading and len(heading.group(1)) <= skip_level:
                skip_level = None
            else:
                index += 1
                continue

        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            if title in SKIP_SECTION_TITLES:
                skip_level = level
                index += 1
                continue
            if title.startswith("X 单页抓取归档："):
                output.append("## 人生观：新增原文材料与可复用增长拆解")
                index += 1
                continue

        if any(line.startswith(prefix) for prefix in SKIP_PREFIXES):
            index += 1
            continue

        if re.match(r"^\s*\d+\.\s*$", line):
            index += 1
            continue

        if line.lstrip().startswith("|") and "公开短线索/评论线索" in line:
            table, index = filter_public_shortline_table(lines, index)
            output.extend(table)
            continue

        line = line.replace(
            "每篇来源都包含主贴结构、作者楼层、评论/引用洞察、可复用原则和 EzRemove 映射。",
            "每篇来源保留原文材料、评论/引用洞察、可复用原则和 EzRemove 映射；删除抓取过程表和楼层流水账。",
        )
        line = line.replace(
            "公开版不大段复制原文，但足够让团队复盘这批内容的增长方法论。",
            "网页保留必要原文材料、图片和结构化拆解，重点服务团队复盘和执行。",
        )

        output.append(line.rstrip())
        index += 1

    text = "\n".join(output)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    text = text.replace("主贴与楼层", "原文材料")
    text = text.replace("主贴结构、作者楼层", "原文材料")
    return text.strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    markdown = args.input.read_text(encoding="utf-8")
    markdown = localize_images(markdown)
    markdown = filter_markdown(markdown)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
