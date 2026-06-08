#!/usr/bin/env python3
"""Extract a normalized corpus from local X/Twitter browser crawl payloads."""

from __future__ import annotations

import json
import re
import hashlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "ZaneWynn_SEO"

SOURCES = [
    ("人生观", "1857705646172631354"),
    ("SEO技巧分享第0篇", "1858800927282729363"),
    ("SEO技巧分享第1篇", "1859131744110481458"),
    ("SEO技巧分享第2篇-竞品品牌词博客", "1861359494988759374"),
    ("SEO技巧分享第2.5篇-内链外链", "1862088008939528665"),
    ("SEO技巧分享第3篇-垂直外链与停留", "1863529073924030787"),
    ("选择有上涨潜力的词", "1861705710545092642"),
    ("产品第一还是流量第一", "1859514896049897754"),
    ("小红书冷启动-1", "1859535615131517384"),
    ("小红书冷启动-2", "1859890665968251317"),
    ("小红书中产人设", "1872582875465601044"),
    ("闲鱼选词方法", "1862435142884901125"),
]

RAW_FILES = [
    "browser_conversation.json",
    "browser_search_url_latest.json",
    "browser_search_quote_latest.json",
]

FALLBACK_RAW_FILES = [
    "tweet_detail_pages.json",
    "search_quote_pages.json",
]


def source_data_root() -> Path:
    local = ROOT / "data" / "raw" / "x"
    if local.exists():
        return local
    if ".worktrees" in ROOT.parts:
        index = ROOT.parts.index(".worktrees")
        main_root = Path(*ROOT.parts[:index])
        raw = main_root / "data" / "raw" / "x"
        if raw.exists():
            return raw
    fallback = Path("/Users/siuserxiaowei/ezremove-watermark-remove-growth-research/data/raw/x")
    if fallback.exists():
        return fallback
    raise SystemExit("Cannot find local X raw data directory.")


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def unwrap_tweet(node: dict[str, Any]) -> dict[str, Any] | None:
    if node.get("__typename") == "TweetWithVisibilityResults":
        tweet = node.get("tweet")
        return tweet if isinstance(tweet, dict) else None
    if node.get("__typename") == "Tweet" and isinstance(node.get("legacy"), dict):
        return node
    if "tweet" in node and isinstance(node.get("tweet"), dict) and node.get("__typename") != "Tweet":
        return unwrap_tweet(node["tweet"])
    if "legacy" in node and "rest_id" in node and isinstance(node["legacy"], dict):
        legacy = node["legacy"]
        if legacy.get("full_text") or legacy.get("text"):
            return node
    return None


def clean_text(text: str) -> str:
    text = re.sub(r"https://t.co/\S+", "", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tweet_text(tweet: dict[str, Any]) -> str:
    legacy = tweet.get("legacy") or {}
    return clean_text(legacy.get("full_text") or legacy.get("text") or "")


def media_file_name(tweet_id: str, media_id: str, url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4"}:
        suffix = ".jpg"
    return f"{tweet_id}_{media_id}{suffix}"


def media_from_graphql_tweet(tweet: dict[str, Any]) -> list[dict[str, Any]]:
    legacy = tweet.get("legacy") or {}
    tweet_id = str(tweet.get("rest_id") or "")
    raw_media = []
    for container in (legacy.get("extended_entities") or {}, legacy.get("entities") or {}):
        if isinstance(container.get("media"), list):
            raw_media.extend(container["media"])

    media: dict[str, dict[str, Any]] = {}
    for idx, item in enumerate(raw_media, 1):
        if not isinstance(item, dict):
            continue
        media_id = str(item.get("id_str") or item.get("id") or f"{tweet_id}_{idx}")
        media_url = item.get("media_url_https") or item.get("media_url")
        media_type = item.get("type") or "media"
        if media_type in {"animated_gif", "video"}:
            variants = (((item.get("video_info") or {}).get("variants")) or [])
            mp4_variants = [v for v in variants if v.get("content_type") == "video/mp4" and v.get("url")]
            if mp4_variants:
                media_url = sorted(mp4_variants, key=lambda v: v.get("bitrate") or 0)[-1]["url"]
        if not media_url:
            continue
        sizes = item.get("original_info") or {}
        url = media_url
        if "pbs.twimg.com/media/" in url and "?" not in url:
            url = f"{url}?name=orig"
        media[media_id] = {
            "id": media_id,
            "type": media_type,
            "url": url,
            "expanded_url": item.get("expanded_url") or "",
            "width": sizes.get("width") or item.get("sizes", {}).get("large", {}).get("w"),
            "height": sizes.get("height") or item.get("sizes", {}).get("large", {}).get("h"),
            "file_name": media_file_name(tweet_id, media_id, url),
        }
    return list(media.values())


def media_from_fxtwitter(path: Path, tweet_id: str) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    tweet = (((payload.get("data") or {}).get("tweet")) or {})
    raw_media = ((tweet.get("media") or {}).get("all")) or []
    media = []
    for idx, item in enumerate(raw_media, 1):
        if not isinstance(item, dict):
            continue
        url = item.get("url")
        if not url:
            continue
        media_id = str(item.get("id") or f"{tweet_id}_{idx}")
        media.append(
            {
                "id": media_id,
                "type": item.get("type") or "media",
                "url": url,
                "expanded_url": f"https://x.com/{AUTHOR}/status/{tweet_id}/photo/{idx}",
                "width": item.get("width"),
                "height": item.get("height"),
                "file_name": media_file_name(tweet_id, media_id, url),
            }
        )
    return media


def visible_page_name(file_name: str) -> str:
    return {
        "browser_conversation.json": "主贴页",
        "browser_search_url_latest.json": "评论/链接搜索页",
        "browser_search_quote_latest.json": "引用搜索页",
    }.get(file_name, file_name)


def normalize_for_match(text: str) -> str:
    return re.sub(r"\s+", "", text or "").lower()


def visible_excerpt(text: str, max_chars: int = 96) -> str:
    lines = []
    for line in (text or "").splitlines():
        clean = line.strip()
        if not clean:
            continue
        if clean in {"Post", "关注", "回复", "转帖", "喜欢", "书签", "分享"}:
            continue
        if clean.startswith("http://") or clean.startswith("https://"):
            continue
        lines.append(clean)
    compact = clean_text(" ".join(lines))
    if len(compact) <= max_chars:
        return compact
    return compact[:max_chars].rstrip() + "..."


def visible_insight(text: str, matched_item: dict[str, Any] | None) -> str:
    if matched_item:
        kind = matched_item.get("type")
        if kind == "root":
            return "可见主贴入口：负责定义主题和读者预期。"
        if kind == "thread":
            return "可见作者补充楼层：把主贴观点继续展开成论证链。"
        if kind == "comment":
            return "可见评论：提供读者疑问、反驳、补充或内容需求信号。"
        if kind == "quote":
            return "可见引用：说明该主题被外部传播或被作者接到下一篇。"
        return "可见关联内容：补足上下游语境。"
    if "Relevant people" in text or "What’s happening" in text or "Search" in text:
        return "侧栏/导航信息，不作为正文拆解对象。"
    if "Show translation" in text or "显示翻译" in text:
        return "正文区可见内容，包含 X 的翻译/交互控件。"
    if "likes" in text or "views" in text or "Bookmarks" in text:
        return "可见互动指标，可辅助判断传播强弱。"
    return "滚动过程中可见的正文块，已作为浏览器可见归档保留。"


def build_visible_archive(raw_root: Path, root_id: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    item_matchers = []
    for item in items:
        normalized = normalize_for_match(item.get("text") or "")
        if not normalized:
            continue
        item_matchers.append((item, normalized[:48], normalized))

    records = []
    seen_hashes: set[str] = set()
    snapshot_count = 0
    article_block_count = 0
    for file_name in RAW_FILES:
        path = raw_root / root_id / file_name
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for snapshot in payload.get("scroll_snapshots") or []:
            snapshot_count += 1
            articles = snapshot.get("articles") or []
            article_block_count += len(articles)
            for article in articles:
                text = article.get("text") or ""
                normalized_text = normalize_for_match(text)
                if not normalized_text:
                    continue
                digest = hashlib.sha1(normalized_text.encode("utf-8")).hexdigest()[:12]
                if digest in seen_hashes:
                    continue
                seen_hashes.add(digest)
                matched = None
                for item, short_key, full_key in item_matchers:
                    if (short_key and short_key in normalized_text) or normalized_text[:48] in full_key:
                        matched = item
                        break
                records.append(
                    {
                        "page": visible_page_name(file_name),
                        "raw_file": file_name,
                        "step": snapshot.get("step"),
                        "scroll_y": snapshot.get("scroll_y"),
                        "article_index": article.get("index"),
                        "matched_id": matched.get("id") if matched else "",
                        "matched_type": matched.get("type") if matched else "",
                        "matched_url": matched.get("url") if matched else "",
                        "excerpt": visible_excerpt(text),
                        "insight": visible_insight(text, matched),
                    }
                )

    return {
        "snapshot_count": snapshot_count,
        "article_block_count": article_block_count,
        "unique_block_count": len(records),
        "records": records,
    }


def author_screen_name(tweet: dict[str, Any]) -> str:
    user = (((tweet.get("core") or {}).get("user_results") or {}).get("result") or {})
    return (
        (user.get("legacy") or {}).get("screen_name")
        or (user.get("core") or {}).get("screen_name")
        or ""
    )


def metrics(tweet: dict[str, Any]) -> dict[str, Any]:
    legacy = tweet.get("legacy") or {}
    views = tweet.get("views") or {}
    return {
        "views": views.get("count"),
        "likes": legacy.get("favorite_count"),
        "bookmarks": legacy.get("bookmark_count"),
        "replies": legacy.get("reply_count"),
        "retweets": legacy.get("retweet_count"),
        "quotes": legacy.get("quote_count"),
    }


def classify(root_id: str, tweet: dict[str, Any]) -> str:
    tid = str(tweet.get("rest_id") or "")
    legacy = tweet.get("legacy") or {}
    author = author_screen_name(tweet)
    conversation_id = str(legacy.get("conversation_id_str") or "")
    quote_of = str(legacy.get("quoted_status_id_str") or "")
    if tid == root_id:
        return "root"
    if quote_of == root_id:
        return "quote"
    if conversation_id == root_id and author == AUTHOR:
        return "thread"
    if conversation_id == root_id:
        return "comment"
    return "related"


def extract_source(raw_root: Path, label: str, root_id: str) -> dict[str, Any]:
    by_id: dict[str, dict[str, Any]] = {}
    source_pages: dict[str, set[str]] = defaultdict(set)
    for file_name in RAW_FILES:
        path = raw_root / root_id / file_name
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for response in payload.get("responses", []):
            for node in walk(response.get("payload")):
                tweet = unwrap_tweet(node)
                if not tweet:
                    continue
                legacy = tweet.get("legacy") or {}
                tid = str(tweet.get("rest_id") or "")
                if not tid or not tweet_text(tweet) or not legacy.get("created_at"):
                    continue
                by_id[tid] = tweet
                source_pages[tid].add(file_name)

    for file_name in FALLBACK_RAW_FILES:
        path = raw_root / root_id / file_name
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        page_payloads = payload if isinstance(payload, list) else [payload]
        for page in page_payloads:
            data = page.get("data") if isinstance(page, dict) else page
            for node in walk(data):
                tweet = unwrap_tweet(node)
                if not tweet:
                    continue
                legacy = tweet.get("legacy") or {}
                tid = str(tweet.get("rest_id") or "")
                if not tid or not tweet_text(tweet) or not legacy.get("created_at"):
                    continue
                by_id[tid] = tweet
                source_pages[tid].add(file_name)

    fx_media = media_from_fxtwitter(raw_root / root_id / "fxtwitter.json", root_id)

    items = []
    for tid, tweet in by_id.items():
        legacy = tweet.get("legacy") or {}
        kind = classify(root_id, tweet)
        items.append(
            {
                "id": tid,
                "type": kind,
                "author": author_screen_name(tweet),
                "created_at": legacy.get("created_at"),
                "reply_to": legacy.get("in_reply_to_status_id_str"),
                "conversation_id": legacy.get("conversation_id_str"),
                "quote_of": legacy.get("quoted_status_id_str"),
                "url": f"https://x.com/{author_screen_name(tweet) or AUTHOR}/status/{tid}",
                "text": tweet_text(tweet),
                "metrics": metrics(tweet),
                "media": media_from_graphql_tweet(tweet),
                "source_pages": sorted(source_pages[tid]),
            }
        )
    for item in items:
        if item["id"] == root_id and fx_media and not item.get("media"):
            item["media"] = fx_media

    type_order = {"root": 0, "thread": 1, "comment": 2, "quote": 3, "related": 4}
    items.sort(key=lambda item: (type_order.get(item["type"], 9), item.get("created_at") or "", item["id"]))
    counts = Counter(item["type"] for item in items)
    media_count = sum(len(item.get("media") or []) for item in items)
    visible_archive = build_visible_archive(raw_root, root_id, items)
    return {
        "label": label,
        "root_id": root_id,
        "source_url": f"https://x.com/{AUTHOR}/status/{root_id}",
        "counts": dict(counts),
        "media_count": media_count,
        "visible_archive": visible_archive,
        "items": items,
    }


def main() -> int:
    raw_root = source_data_root()
    processed = ROOT / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    sources = [extract_source(raw_root, label, root_id) for label, root_id in SOURCES]
    stats = {
        source["root_id"]: source["counts"]
        for source in sources
    }
    corpus = {
        "generated_at": "2026-06-08",
        "raw_root": str(raw_root),
        "author": AUTHOR,
        "sources": sources,
        "stats": stats,
    }
    out = processed / "public_legacy_content_corpus.json"
    out.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    for source in sources:
        print(source["root_id"], source["label"], source["counts"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
