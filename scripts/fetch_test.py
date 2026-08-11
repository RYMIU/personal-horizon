"""Phase 3 fetch-integration test: run Horizon's own scrapers over the production
config and report per-source statistics.

Usage: uv run python scripts/fetch_test.py [config_path]
"""
import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone

import httpx

from src.extractors import ExtractorRegistry
from src.scrapers.hackernews import HackerNewsScraper
from src.scrapers.ossinsight import OSSInsightScraper
from src.scrapers.rss import RSSScraper
from src.storage.manager import StorageManager


async def main(config_path: str) -> None:
    storage = StorageManager("data", config_path)
    config = storage.load_config()
    since = datetime.now(timezone.utc) - timedelta(
        hours=config.collection.time_window_hours + 2
    )
    report = []

    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers={"User-Agent": "Horizon/1.0 (personal-horizon fetch test)"},
    ) as client:
        # RSS feeds, one at a time for per-feed stats
        registry = ExtractorRegistry(config.extractors)
        for feed in config.sources.rss:
            if not feed.enabled:
                continue
            rec = {"source": feed.name, "category": feed.category, "type": "rss"}
            try:
                items = await RSSScraper([feed], client, registry).fetch(since)
                rec["fetched"] = len(items)
                rec["valid_date"] = sum(1 for i in items if i.published_at)
                rec["dup_urls"] = len(items) - len({i.url for i in items})
                rec["error"] = None
            except Exception as ex:  # noqa: BLE001
                rec["fetched"] = 0
                rec["error"] = f"{type(ex).__name__}: {str(ex)[:120]}"
            report.append(rec)

        # Hacker News
        if config.sources.hackernews.enabled:
            rec = {"source": "Hacker News", "category": config.sources.hackernews.category, "type": "hackernews"}
            try:
                items = await HackerNewsScraper(config.sources.hackernews, client).fetch(since)
                rec["fetched"] = len(items)
                rec["valid_date"] = sum(1 for i in items if i.published_at)
                rec["dup_urls"] = len(items) - len({i.url for i in items})
                rec["error"] = None
            except Exception as ex:  # noqa: BLE001
                rec["fetched"] = 0
                rec["error"] = f"{type(ex).__name__}: {str(ex)[:120]}"
            report.append(rec)

        # OSS Insight
        if config.sources.ossinsight and config.sources.ossinsight.enabled:
            rec = {"source": "OSS Insight", "category": config.sources.ossinsight.category, "type": "ossinsight"}
            try:
                items = await OSSInsightScraper(config.sources.ossinsight, client).fetch(since)
                rec["fetched"] = len(items)
                rec["valid_date"] = sum(1 for i in items if i.published_at)
                rec["dup_urls"] = len(items) - len({i.url for i in items})
                rec["error"] = None
            except Exception as ex:  # noqa: BLE001
                rec["fetched"] = 0
                rec["error"] = f"{type(ex).__name__}: {str(ex)[:120]}"
            report.append(rec)

    by_cat = {}
    for rec in report:
        by_cat.setdefault(rec["category"], 0)
        by_cat[rec["category"]] += rec["fetched"]

    for rec in report:
        print(json.dumps(rec, ensure_ascii=False))
    print(json.dumps({"total": sum(r["fetched"] for r in report), "by_category": by_cat}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "data/config.json"))
