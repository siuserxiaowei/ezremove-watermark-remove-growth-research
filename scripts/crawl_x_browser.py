#!/usr/bin/env python3
"""Crawl X conversation/search pages with local Chrome login cookies.

This complements crawl_x_threads.py. It saves raw browser network payloads under
data/raw and writes a sanitized manifest suitable for public docs.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import browser_cookie3
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from crawl_x_threads import (
    AUTHOR,
    PROCESSED_DIR,
    RAW_DIR,
    TWEETS,
    collect_tweets,
    safe_excerpt,
    save_json,
    summarize_tweet,
)


CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def chrome_cookies_for_playwright(domain_name: str) -> list[dict[str, Any]]:
    jar = browser_cookie3.chrome(domain_name=domain_name)
    cookies: list[dict[str, Any]] = []
    for cookie in jar:
        same_site = "Lax"
        if getattr(cookie, "_rest", None):
            raw_same_site = cookie._rest.get("SameSite") or cookie._rest.get("samesite")
            if raw_same_site in {"Strict", "Lax", "None"}:
                same_site = raw_same_site
        cookies.append(
            {
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path or "/",
                "expires": int(cookie.expires) if cookie.expires else -1,
                "httpOnly": bool(getattr(cookie, "_rest", {}).get("HttpOnly")),
                "secure": bool(cookie.secure),
                "sameSite": same_site,
            }
        )
    return cookies


def sanitize_dom_text(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if clean in {"登录", "注册", "关注", "更多", "回复", "转帖", "喜欢"}:
            continue
        lines.append(safe_excerpt(clean, max_words=22, max_chars=120))
    return lines[:80]


def sanitize_article_text(text: str) -> str:
    lines = sanitize_dom_text(text)
    if not lines:
        return ""
    # X repeats action labels and sidebar text frequently; keep the compact
    # article block so later extraction can dedupe visible scroll snapshots.
    return "\n".join(lines[:36])


def collect_visible_snapshot(page, step: int, phase: str) -> dict[str, Any]:
    try:
        scroll_y = page.evaluate("() => Math.round(window.scrollY)")
    except Exception:
        scroll_y = None
    try:
        article_texts = page.locator("article").evaluate_all(
            """els => els.map((el, index) => ({
                index,
                text: el.innerText || "",
                top: Math.round(el.getBoundingClientRect().top),
                height: Math.round(el.getBoundingClientRect().height)
            }))"""
        )
    except Exception:
        article_texts = []

    articles = []
    seen = set()
    for article in article_texts:
        text = sanitize_article_text(article.get("text") or "")
        if not text or text in seen:
            continue
        seen.add(text)
        articles.append(
            {
                "index": article.get("index"),
                "top": article.get("top"),
                "height": article.get("height"),
                "text": text,
            }
        )
    try:
        body_text = page.locator("body").inner_text(timeout=5000)
    except Exception:
        body_text = ""

    return {
        "step": step,
        "phase": phase,
        "scroll_y": scroll_y,
        "article_count": len(articles),
        "articles": articles[:20],
        "body_lines_sample": sanitize_dom_text(body_text)[:40],
    }


def collect_page(
    page,
    url: str,
    raw_out: Path,
    *,
    scrolls: int = 3,
    wait_ms: int = 1500,
    goto_timeout_ms: int = 20_000,
) -> dict[str, Any]:
    responses: list[dict[str, Any]] = []
    scroll_snapshots: list[dict[str, Any]] = []
    error = None

    def on_response(response):
        response_url = response.url
        if "/graphql/" not in response_url and "/i/api/graphql/" not in response_url:
            return
        try:
            payload = response.json()
        except Exception:
            payload = None
        responses.append(
            {
                "url": response_url,
                "status": response.status,
                "payload": payload,
            }
        )

    page.on("response", on_response)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=goto_timeout_ms)
    except Exception as exc:  # noqa: BLE001 - X often keeps loading; still capture visible DOM.
        error = repr(exc)

    try:
        page.wait_for_timeout(wait_ms)
        scroll_snapshots.append(collect_visible_snapshot(page, 0, "initial"))
        for idx in range(1, scrolls + 1):
            page.mouse.wheel(0, 1400)
            page.wait_for_timeout(900)
            scroll_snapshots.append(collect_visible_snapshot(page, idx, "after_wheel"))
    except Exception as exc:  # noqa: BLE001 - persisted for crawl diagnostics.
        error = f"{error} | {repr(exc)}" if error else repr(exc)
    try:
        body_text = page.locator("body").inner_text(timeout=10_000)
    except PlaywrightTimeoutError:
        body_text = ""
    page.remove_listener("response", on_response)

    raw = {
        "url": url,
        "final_url": page.url,
        "title": page.title(),
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "error": error,
        "response_count": len(responses),
        "responses": responses,
        "scroll_snapshots": scroll_snapshots,
        "dom_text": body_text,
    }
    save_json(raw_out, raw)
    return raw


def main() -> int:
    scrolls = int(os.environ.get("X_BROWSER_SCROLLS", "3"))
    wait_ms = int(os.environ.get("X_BROWSER_WAIT_MS", "1500"))
    goto_timeout_ms = int(os.environ.get("X_BROWSER_GOTO_TIMEOUT_MS", "20000"))
    only_ids = {
        item.strip()
        for item in os.environ.get("X_TWEET_IDS", "").split(",")
        if item.strip()
    }
    x_cookies = chrome_cookies_for_playwright("x.com")
    twitter_cookies = chrome_cookies_for_playwright("twitter.com")
    all_cookies = x_cookies + twitter_cookies
    if not any(cookie["name"] == "auth_token" for cookie in all_cookies):
        raise SystemExit("Chrome Default profile does not expose an X auth_token cookie.")

    manifest: dict[str, Any] = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_account": f"https://x.com/{AUTHOR}",
        "cookie_source": "Chrome Default profile via browser_cookie3",
        "raw_storage": "data/raw/x/<tweet_id>/browser_*.json",
        "items": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 1800},
            locale="zh-CN",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
            ),
        )
        context.add_cookies(all_cookies)
        page = context.new_page()

        for label, tweet_id in TWEETS:
            if only_ids and tweet_id not in only_ids:
                continue
            print(f"browser crawl {tweet_id} {label}", flush=True)
            item_dir = RAW_DIR / tweet_id
            item_dir.mkdir(parents=True, exist_ok=True)
            tweet_url = f"https://x.com/{AUTHOR}/status/{tweet_id}"
            pages = [
                ("conversation", tweet_url),
                ("search_url_latest", f"https://x.com/search?q=url%3A{tweet_id}&src=typed_query&f=live"),
                (
                    "search_quote_latest",
                    f"https://x.com/search?q=quoted_tweet_id%3A{tweet_id}&src=typed_query&f=live",
                ),
            ]

            page_payloads = []
            for name, url in pages:
                raw = collect_page(
                    page,
                    url,
                    item_dir / f"browser_{name}.json",
                    scrolls=scrolls,
                    wait_ms=wait_ms,
                    goto_timeout_ms=goto_timeout_ms,
                )
                page_payloads.append((name, raw))
                time.sleep(1)

            all_tweets: dict[str, dict[str, Any]] = {}
            network_statuses: list[dict[str, Any]] = []
            for name, raw in page_payloads:
                network_statuses.extend(
                    {"page": name, "status": r["status"], "url": r["url"]}
                    for r in raw.get("responses", [])
                )
                for response in raw.get("responses", []):
                    for tweet in collect_tweets(response.get("payload")):
                        tid = str(tweet.get("rest_id") or "")
                        if tid:
                            all_tweets[tid] = tweet

            summaries = [summarize_tweet(tweet, tweet_id) for tweet in all_tweets.values()]
            replies = [
                t
                for t in summaries
                if t["id"] != tweet_id
                and (t.get("in_reply_to_status_id") == tweet_id or t.get("conversation_id") == tweet_id)
            ]
            quotes = [
                t for t in summaries if t["id"] != tweet_id and t.get("quoted_status_id") == tweet_id
            ]
            dom_lines = sanitize_dom_text(page_payloads[0][1].get("dom_text", ""))
            scroll_snapshot_count = sum(
                len(raw.get("scroll_snapshots") or [])
                for _, raw in page_payloads
            )
            visible_article_count = sum(
                snapshot.get("article_count", 0)
                for _, raw in page_payloads
                for snapshot in raw.get("scroll_snapshots") or []
            )

            manifest["items"].append(
                {
                    "label": label,
                    "tweet_id": tweet_id,
                    "source_url": tweet_url,
                    "network_response_count": len(network_statuses),
                    "network_statuses": network_statuses[:20],
                    "conversation_candidates_fetched": len(summaries),
                    "reply_candidates_fetched": len(replies),
                    "quote_candidates_fetched": len(quotes),
                    "reply_samples": replies[:8],
                    "quote_samples": quotes[:8],
                    "dom_lines_sample": dom_lines[:40],
                    "scroll_snapshot_count": scroll_snapshot_count,
                    "visible_article_count": visible_article_count,
                    "raw_local_dir": str(item_dir.relative_to(RAW_DIR.parents[1])),
                }
            )
            save_json(PROCESSED_DIR / "x_browser_crawl_manifest.partial.json", manifest)

        context.close()
        browser.close()

    save_json(PROCESSED_DIR / "x_browser_crawl_manifest.json", manifest)
    print(f"saved {PROCESSED_DIR / 'x_browser_crawl_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
