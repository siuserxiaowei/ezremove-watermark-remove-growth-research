#!/usr/bin/env python3
"""Download archived X/Twitter media referenced by the processed corpus."""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "processed" / "public_legacy_content_corpus.json"
OUT_DIR = ROOT / "docs" / "assets" / "x-media"


def download(url: str, path: Path) -> tuple[bool, str | None]:
    if path.exists() and path.stat().st_size > 0:
        return True, None
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
            ),
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            path.write_bytes(resp.read())
        return True, None
    except Exception as exc:  # noqa: BLE001 - persisted in manifest.
        return False, repr(exc)


def main() -> int:
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    seen = set()
    for source in data["sources"]:
        for item in source["items"]:
            for media in item.get("media") or []:
                key = media.get("file_name") or media.get("url")
                if not key or key in seen:
                    continue
                seen.add(key)
                file_name = media["file_name"]
                output = OUT_DIR / file_name
                ok, error = download(media["url"], output)
                manifest.append(
                    {
                        "tweet_id": item["id"],
                        "source_label": source["label"],
                        "media_id": media.get("id"),
                        "type": media.get("type"),
                        "source_url": media.get("url"),
                        "file": f"assets/x-media/{file_name}",
                        "bytes": output.stat().st_size if output.exists() else 0,
                        "ok": ok,
                        "error": error,
                    }
                )
                print("ok" if ok else "fail", file_name, error or "")
                time.sleep(0.2)

    (OUT_DIR / "manifest.json").write_text(
        json.dumps(
            {
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "count": len(manifest),
                "items": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(OUT_DIR / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
