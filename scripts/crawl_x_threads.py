#!/usr/bin/env python3
"""Crawl public X/Twitter materials for the EzRemove SEO research pack.

The script stores full raw responses locally under data/raw, then emits a
sanitized manifest for public documents. Do not commit data/raw.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "x"
PROCESSED_DIR = ROOT / "data" / "processed"

AUTHOR = "ZaneWynn_SEO"

TWEETS = [
    ("人生观", "1857705646172631354"),
    ("SEO技巧分享第0篇", "1858800927282729363"),
    ("SEO技巧分享第1篇", "1859131744110481458"),
    ("SEO技巧分享第2篇-竞品品牌词博客", "1861359494988759374"),
    ("SEO技巧分享第2.5篇", "1862088008939528665"),
    ("SEO技巧分享第3篇-垂直外链与停留", "1863529073924030787"),
    ("选择有上涨潜力的词", "1861705710545092642"),
    ("产品第一还是流量第一", "1859514896049897754"),
    ("小红书冷启动-1", "1859535615131517384"),
    ("小红书冷启动-2", "1859890665968251317"),
    ("小红书冷启动-3", "1872582875465601044"),
    ("闲鱼选词方法", "1862435142884901125"),
]

TWEET_DETAIL_OP = ("RguQ9yvaXf-EETmDagsLzg", "TweetDetail")
SEARCH_OP = ("dsWn-Op2S0SmJjgY6Yvckg", "SearchTimeline")

COMMON_FEATURES = [
    "rweb_video_screen_enabled",
    "rweb_cashtags_enabled",
    "profile_label_improvements_pcf_label_in_post_enabled",
    "responsive_web_profile_redirect_enabled",
    "rweb_tipjar_consumption_enabled",
    "verified_phone_label_enabled",
    "creator_subscriptions_tweet_preview_api_enabled",
    "responsive_web_graphql_timeline_navigation_enabled",
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled",
    "premium_content_api_read_enabled",
    "communities_web_enable_tweet_community_results_fetch",
    "c9s_tweet_anatomy_moderator_badge_enabled",
    "responsive_web_grok_analyze_button_fetch_trends_enabled",
    "responsive_web_grok_analyze_post_followups_enabled",
    "rweb_cashtags_composer_attachment_enabled",
    "responsive_web_jetfuel_frame",
    "responsive_web_grok_share_attachment_enabled",
    "responsive_web_grok_annotations_enabled",
    "articles_preview_enabled",
    "responsive_web_edit_tweet_api_enabled",
    "rweb_conversational_replies_downvote_enabled",
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled",
    "view_counts_everywhere_api_enabled",
    "longform_notetweets_consumption_enabled",
    "responsive_web_twitter_article_tweet_consumption_enabled",
    "content_disclosure_indicator_enabled",
    "content_disclosure_ai_generated_indicator_enabled",
    "responsive_web_grok_show_grok_translated_post",
    "responsive_web_grok_analysis_button_from_backend",
    "post_ctas_fetch_enabled",
    "freedom_of_speech_not_reach_fetch_enabled",
    "standardized_nudges_misinfo",
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled",
    "longform_notetweets_rich_text_read_enabled",
    "longform_notetweets_inline_media_enabled",
    "responsive_web_grok_image_annotation_enabled",
    "responsive_web_grok_imagine_annotation_enabled",
    "responsive_web_grok_community_note_auto_translation_is_enabled",
    "responsive_web_enhance_cards_enabled",
]

FIELD_TOGGLES = [
    "withPayments",
    "withAuxiliaryUserLabels",
    "withArticleRichContentState",
    "withArticlePlainText",
    "withArticleSummaryText",
    "withArticleVoiceOver",
    "withGrokAnalyze",
    "withDisallowedReplyControls",
]


@dataclass
class FetchResult:
    ok: bool
    status: int
    data: Any | None = None
    error: str | None = None


def request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    data: bytes | None = None,
    timeout: int = 30,
) -> FetchResult:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            text = raw.decode("utf-8", errors="replace")
            try:
                return FetchResult(True, resp.status, json.loads(text))
            except json.JSONDecodeError:
                return FetchResult(False, resp.status, {"text": text}, "invalid json")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"text": body[:1000]}
        return FetchResult(False, exc.code, payload, f"http {exc.code}")
    except Exception as exc:  # noqa: BLE001 - persisted for crawl diagnostics.
        return FetchResult(False, 0, None, repr(exc))


def load_bearer_token() -> str | None:
    token = os.environ.get("X_BEARER_TOKEN")
    if token:
        return token
    try:
        from twitter_downloader.scraper import BEARER_TOKEN  # type: ignore

        return BEARER_TOKEN
    except Exception:
        pass

    local_scraper = (
        Path.home()
        / "Desktop"
        / "日常交流"
        / "06-开源项目"
        / "twitter-media-downloader"
        / "twitter_downloader"
        / "scraper.py"
    )
    if local_scraper.exists():
        match = re.search(
            r'BEARER_TOKEN\s*=\s*"([^"]+)"',
            local_scraper.read_text(encoding="utf-8", errors="ignore"),
        )
        if match:
            return match.group(1)
    return None


def get_guest_token(bearer: str) -> str | None:
    result = request_json(
        "POST",
        "https://api.x.com/1.1/guest/activate.json",
        headers={
            "Authorization": f"Bearer {bearer}",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    if result.ok and isinstance(result.data, dict):
        guest = result.data.get("guest_token")
        return guest if isinstance(guest, str) else None
    return None


def feature_map() -> dict[str, bool]:
    disabled = {
        "verified_phone_label_enabled",
        "premium_content_api_read_enabled",
    }
    return {name: name not in disabled for name in COMMON_FEATURES}


def field_toggle_map() -> dict[str, bool]:
    enabled = {
        "withArticleRichContentState",
        "withArticlePlainText",
        "withArticleSummaryText",
        "withGrokAnalyze",
        "withDisallowedReplyControls",
    }
    return {name: name in enabled for name in FIELD_TOGGLES}


def graphql_headers(bearer: str, guest: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {bearer}",
        "X-Guest-Token": guest,
        "Content-Type": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Referer": "https://x.com/",
        "Origin": "https://x.com",
    }


def call_graphql(
    bearer: str,
    guest: str,
    op: tuple[str, str],
    variables: dict[str, Any],
    *,
    field_toggles: dict[str, bool] | None = None,
) -> FetchResult:
    query_id, op_name = op
    url = f"https://api.x.com/graphql/{query_id}/{op_name}"
    params = {
        "variables": json.dumps(variables, separators=(",", ":")),
        "features": json.dumps(feature_map(), separators=(",", ":")),
        "fieldToggles": json.dumps(field_toggles or field_toggle_map(), separators=(",", ":")),
    }
    return request_json("GET", url, headers=graphql_headers(bearer, guest), params=params)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_excerpt(text: str, max_words: int = 22, max_chars: int = 96) -> str:
    clean = re.sub(r"\s+", " ", text or "").strip()
    if not clean:
        return ""
    parts = clean.split(" ")
    excerpt = clean if len(parts) <= max_words else " ".join(parts[:max_words]) + "..."
    if len(excerpt) > max_chars:
        return excerpt[:max_chars].rstrip() + "..."
    return excerpt


def walk(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk(item)


def unwrap_tweet_result(node: dict[str, Any]) -> dict[str, Any] | None:
    if "tweet" in node and isinstance(node["tweet"], dict):
        return unwrap_tweet_result(node["tweet"])
    if node.get("__typename") == "TweetWithVisibilityResults":
        tweet = node.get("tweet")
        return tweet if isinstance(tweet, dict) else None
    if "legacy" in node and "rest_id" in node:
        return node
    return None


def collect_tweets(payload: Any) -> list[dict[str, Any]]:
    seen: set[str] = set()
    tweets: list[dict[str, Any]] = []
    for node in walk(payload):
        tweet = unwrap_tweet_result(node)
        if not tweet:
            continue
        tweet_id = str(tweet.get("rest_id") or "")
        if not tweet_id or tweet_id in seen:
            continue
        seen.add(tweet_id)
        tweets.append(tweet)
    return tweets


def extract_cursor(payload: Any, cursor_type: str = "Bottom") -> str | None:
    for node in walk(payload):
        if not isinstance(node, dict):
            continue
        content = node.get("content")
        if isinstance(content, dict) and content.get("cursorType") == cursor_type:
            value = content.get("value")
            if isinstance(value, str):
                return value
        if node.get("cursorType") == cursor_type and isinstance(node.get("value"), str):
            return node["value"]
    return None


def summarize_tweet(tweet: dict[str, Any], root_id: str) -> dict[str, Any]:
    legacy = tweet.get("legacy") or {}
    user = (((tweet.get("core") or {}).get("user_results") or {}).get("result") or {})
    user_legacy = user.get("legacy") or {}
    views = tweet.get("views") or {}
    tweet_id = str(tweet.get("rest_id") or "")
    text = legacy.get("full_text") or legacy.get("text") or ""
    return {
        "id": tweet_id,
        "url": f"https://x.com/{user_legacy.get('screen_name') or AUTHOR}/status/{tweet_id}",
        "is_root": tweet_id == root_id,
        "author": user_legacy.get("screen_name") or "",
        "created_at": legacy.get("created_at") or "",
        "conversation_id": legacy.get("conversation_id_str") or "",
        "in_reply_to_status_id": legacy.get("in_reply_to_status_id_str") or "",
        "quoted_status_id": legacy.get("quoted_status_id_str") or "",
        "metrics": {
            "reply_count": legacy.get("reply_count"),
            "retweet_count": legacy.get("retweet_count"),
            "quote_count": legacy.get("quote_count"),
            "favorite_count": legacy.get("favorite_count"),
            "bookmark_count": legacy.get("bookmark_count"),
            "view_count": views.get("count"),
        },
        "excerpt": safe_excerpt(text),
    }


def fetch_fx_twitter(tweet_id: str) -> FetchResult:
    return request_json("GET", f"https://api.fxtwitter.com/{AUTHOR}/status/{tweet_id}")


def crawl_tweet_detail(bearer: str, guest: str, tweet_id: str, max_pages: int) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    cursor: str | None = None
    for page in range(max_pages):
        variables = {
            "focalTweetId": tweet_id,
            "with_rux_injections": False,
            "rankingMode": "Relevance",
            "includePromotedContent": True,
            "withCommunity": False,
            "withQuickPromoteEligibilityTweetFields": True,
            "withBirdwatchNotes": False,
            "withVoice": False,
            "isReaderMode": False,
        }
        if cursor:
            variables["cursor"] = cursor
        result = call_graphql(bearer, guest, TWEET_DETAIL_OP, variables)
        page_payload = {
            "ok": result.ok,
            "status": result.status,
            "error": result.error,
            "data": result.data,
        }
        pages.append(page_payload)
        if not result.ok:
            break
        next_cursor = extract_cursor(result.data)
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        time.sleep(1)
    return pages


def crawl_search_quotes(bearer: str, guest: str, tweet_id: str) -> list[dict[str, Any]]:
    queries = [
        f"url:{tweet_id}",
        f"quoted_tweet_id:{tweet_id}",
        f"https://x.com/{AUTHOR}/status/{tweet_id}",
    ]
    pages: list[dict[str, Any]] = []
    for raw_query in queries:
        variables = {
            "rawQuery": raw_query,
            "count": 20,
            "querySource": "typed_query",
            "product": "Latest",
        }
        result = call_graphql(bearer, guest, SEARCH_OP, variables)
        pages.append(
            {
                "raw_query": raw_query,
                "ok": result.ok,
                "status": result.status,
                "error": result.error,
                "data": result.data,
            }
        )
        time.sleep(1)
    return pages


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    max_pages = int(os.environ.get("X_TWEET_DETAIL_PAGES", "4"))
    bearer = load_bearer_token()
    guest = get_guest_token(bearer) if bearer else None

    manifest: dict[str, Any] = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_account": f"https://x.com/{AUTHOR}",
        "graphql_guest_mode": bool(bearer and guest),
        "notes": [
            "Raw X/FxTwitter responses are kept locally under data/raw and excluded from Git.",
            "Public artifacts use links, metrics, counts, summaries, and short excerpts only.",
        ],
        "items": [],
        "crawl_errors": [],
    }
    internal: dict[str, Any] = {"items": []}

    for label, tweet_id in TWEETS:
        print(f"crawl {tweet_id} {label}")
        item_dir = RAW_DIR / tweet_id
        item_dir.mkdir(parents=True, exist_ok=True)
        source_url = f"https://x.com/{AUTHOR}/status/{tweet_id}"

        fx = fetch_fx_twitter(tweet_id)
        save_json(item_dir / "fxtwitter.json", fx.__dict__)

        detail_pages: list[dict[str, Any]] = []
        search_pages: list[dict[str, Any]] = []
        if bearer and guest:
            detail_pages = crawl_tweet_detail(bearer, guest, tweet_id, max_pages)
            save_json(item_dir / "tweet_detail_pages.json", detail_pages)
            search_pages = crawl_search_quotes(bearer, guest, tweet_id)
            save_json(item_dir / "search_quote_pages.json", search_pages)
        else:
            manifest["crawl_errors"].append(
                {"tweet_id": tweet_id, "stage": "graphql", "error": "missing bearer or guest token"}
            )

        all_payloads = [fx.data] + [p.get("data") for p in detail_pages] + [p.get("data") for p in search_pages]
        all_tweets: list[dict[str, Any]] = []
        for payload in all_payloads:
            all_tweets.extend(collect_tweets(payload))

        dedup: dict[str, dict[str, Any]] = {}
        for tweet in all_tweets:
            tid = str(tweet.get("rest_id") or "")
            if tid:
                dedup[tid] = tweet

        summaries = [summarize_tweet(tweet, tweet_id) for tweet in dedup.values()]
        replies = [
            t
            for t in summaries
            if t["id"] != tweet_id
            and (
                t.get("in_reply_to_status_id") == tweet_id
                or t.get("conversation_id") == tweet_id
            )
        ]
        quotes = [
            t
            for t in summaries
            if t["id"] != tweet_id and t.get("quoted_status_id") == tweet_id
        ]

        fx_tweet = fx.data.get("tweet", {}) if isinstance(fx.data, dict) else {}
        fx_author = fx_tweet.get("author", {}) if isinstance(fx_tweet, dict) else {}
        public_item = {
            "label": label,
            "tweet_id": tweet_id,
            "source_url": source_url,
            "fx_status": fx.status,
            "fx_ok": fx.ok,
            "main_metrics": {
                "likes": fx_tweet.get("likes"),
                "replies": fx_tweet.get("replies"),
                "retweets": fx_tweet.get("retweets"),
                "quotes": fx_tweet.get("quotes"),
                "bookmarks": fx_tweet.get("bookmarks"),
                "views": fx_tweet.get("views"),
                "created_at": fx_tweet.get("created_at"),
            },
            "author_snapshot": {
                "screen_name": fx_author.get("screen_name"),
                "followers": fx_author.get("followers"),
                "following": fx_author.get("following"),
                "verified": fx_author.get("verified"),
            },
            "graphql_detail_pages": len(detail_pages),
            "graphql_detail_ok_pages": sum(1 for p in detail_pages if p.get("ok")),
            "reply_candidates_fetched": len(replies),
            "quote_candidates_fetched": len(quotes),
            "conversation_candidates_fetched": len(summaries),
            "reply_samples": replies[:5],
            "quote_samples": quotes[:5],
            "main_excerpt": safe_excerpt(fx_tweet.get("text") or fx_tweet.get("raw_text") or ""),
            "raw_local_dir": str(item_dir.relative_to(ROOT)),
        }
        manifest["items"].append(public_item)
        internal["items"].append(
            {
                "label": label,
                "tweet_id": tweet_id,
                "source_url": source_url,
                "fxtwitter": fx.data,
                "summaries": summaries,
            }
        )

        if not fx.ok:
            manifest["crawl_errors"].append(
                {"tweet_id": tweet_id, "stage": "fxtwitter", "status": fx.status, "error": fx.error}
            )
        for page_idx, page in enumerate(detail_pages):
            if not page.get("ok"):
                manifest["crawl_errors"].append(
                    {
                        "tweet_id": tweet_id,
                        "stage": f"tweet_detail_page_{page_idx}",
                        "status": page.get("status"),
                        "error": page.get("error"),
                    }
                )
        for page_idx, page in enumerate(search_pages):
            if not page.get("ok"):
                manifest["crawl_errors"].append(
                    {
                        "tweet_id": tweet_id,
                        "stage": f"search_quote_page_{page_idx}",
                        "query": page.get("raw_query"),
                        "status": page.get("status"),
                        "error": page.get("error"),
                    }
                )

        time.sleep(1)

    save_json(PROCESSED_DIR / "x_crawl_manifest.json", manifest)
    save_json(PROCESSED_DIR / "x_internal_corpus.json", internal)
    print(f"saved {PROCESSED_DIR / 'x_crawl_manifest.json'}")
    if manifest["crawl_errors"]:
        print(f"errors: {len(manifest['crawl_errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
