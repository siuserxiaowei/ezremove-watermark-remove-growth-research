# X Legacy Content Breakdown Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the EzRemove research deliverable so it decomposes the actual X/Twitter legacy content, including thread posts, comments, and quote posts, then publishes the full analysis to GitHub Pages and Feishu.

**Architecture:** Parse raw X browser GraphQL payloads from the ignored local `data/raw/x` directory into a normalized corpus, classify each item as root/thread/comment/quote/related, and generate public-safe long-form analysis from that corpus. The online page must render the full document inline, not a link-only placeholder.

**Tech Stack:** Python 3 stdlib, existing raw X JSON files, Pandoc for Markdown-to-HTML, GitHub Pages from `/docs`, `lark-cli docs +update/+create` for Feishu.

---

### Task 1: Corpus Parser

**Files:**
- Create: `scripts/extract_x_legacy_corpus.py`
- Create: `data/processed/public_legacy_content_corpus.json`

- [ ] **Step 1: Implement strict tweet extraction**

Create `scripts/extract_x_legacy_corpus.py` that:
- Finds the source root: current repo if `data/raw/x` exists, otherwise parent repo when running inside `.worktrees/content-breakdown`.
- Reads `browser_conversation.json`, `browser_search_url_latest.json`, and `browser_search_quote_latest.json` for each source tweet.
- Walks each GraphQL payload recursively.
- Keeps only tweet objects with `legacy.full_text` or `legacy.text`, `legacy.created_at`, and `rest_id`.
- Extracts author from `core.user_results.result.legacy.screen_name` or `core.user_results.result.core.screen_name`.
- Classifies as:
  - `root`: tweet id equals the source tweet id.
  - `thread`: author is `ZaneWynn_SEO`, `conversation_id_str` equals root, and tweet id is not root.
  - `comment`: non-author tweet in the root conversation.
  - `quote`: `quoted_status_id_str` equals root.
  - `related`: any other tweet captured from the page/search context.

- [ ] **Step 2: Emit public-safe corpus**

Write `data/processed/public_legacy_content_corpus.json` with:
- `sources[]`: source label, tweet id, URL.
- `items[]`: id, type, author, created_at, reply_to, quote_of, full_text, metrics, source_page.
- `stats`: counts per source and type.

This file is allowed to contain full local text for internal processing, but must stay ignored unless explicitly reviewed.

### Task 2: Deep Breakdown Generator

**Files:**
- Create: `scripts/build_legacy_breakdown.py`
- Create/Modify: `docs/ezremove-watermark-remove-growth-research.md`
- Modify: `docs/index.html`
- Modify: `site/index.html`
- Create: `data/processed/public_breakdown_metrics.json`

- [ ] **Step 1: Create analysis model**

Implement `scripts/build_legacy_breakdown.py` to load `public_legacy_content_corpus.json` and generate a long-form Markdown report with:
- Overview of all 12 source threads.
- Per-thread sections containing:
  - source URL and counts,
  - one-sentence theme,
  - argument structure,
  - thread post breakdown,
  - comment/quote insights,
  - reusable principle,
  - concrete EzRemove action mapping.
- A final “术法道器势” synthesis.
- A 30/60/90 day execution plan.

- [ ] **Step 2: Preserve copyright-safe public presentation**

The report must not dump all tweet text verbatim. It may include short excerpts, links, and detailed paraphrase. Full text remains in local ignored corpus.

- [ ] **Step 3: Render full report inline**

Reuse Pandoc conversion so `docs/index.html` and `site/index.html` render the complete report inline.

### Task 3: Parallel Review Fragments

**Files:**
- Create: `notes/comment-insights.md`
- Create: `notes/ezremove-action-map.md`

- [ ] **Step 1: Comment insights fragment**

Summarize what the comments and quotes reveal: unanswered questions, reader demand, objections, and follow-up opportunities.

- [ ] **Step 2: EzRemove action map fragment**

Map the legacy content to EzRemove’s `watermark remove` growth system: page types, PR hooks, KOL content angles, internal links, external links, and GEO pages.

### Task 4: Publish and Verify

**Files:**
- Modify: Feishu document `THSzdhk8vo7ycIxCXebcvpwdn9g`
- Push branch `content-breakdown`, then merge/push to main after verification.

- [ ] **Step 1: Run generators**

Run:
```bash
python3 scripts/extract_x_legacy_corpus.py
python3 scripts/build_legacy_breakdown.py
```

- [ ] **Step 2: Local verify**

Run a Playwright smoke test against `docs/index.html`; expect:
- `article.doc` exists.
- At least 12 per-thread sections exist.
- Page contains comment/quote insights.
- No “完整文档见 .md” placeholder remains.

- [ ] **Step 3: Publish**

Commit, merge to main, push, wait for GitHub Pages `built`, verify live URL.

- [ ] **Step 4: Feishu**

Update or recreate the Feishu doc with the full Markdown, then fetch it to verify content.

