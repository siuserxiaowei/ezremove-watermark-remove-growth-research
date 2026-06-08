#!/usr/bin/env python3
"""Extract a normalized corpus from local X/Twitter browser crawl payloads."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


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
                "source_pages": sorted(source_pages[tid]),
            }
        )

    type_order = {"root": 0, "thread": 1, "comment": 2, "quote": 3, "related": 4}
    items.sort(key=lambda item: (type_order.get(item["type"], 9), item.get("created_at") or "", item["id"]))
    counts = Counter(item["type"] for item in items)
    return {
        "label": label,
        "root_id": root_id,
        "source_url": f"https://x.com/{AUTHOR}/status/{root_id}",
        "counts": dict(counts),
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

