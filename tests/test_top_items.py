"""Unit tests for the Top-N picks and daily overview rendering."""

import asyncio
from datetime import datetime, timezone

from src.ai.summarizer import DailySummarizer
from src.models import (
    ClassificationResult,
    ContentAnalysis,
    ContentItem,
    DigestConfig,
    ProcessingResult,
    SourceType,
)


def _run_async(coro):
    return asyncio.run(coro)


def _make_item(idx: int, score, tags, profile: str = "china-news") -> ContentItem:
    return ContentItem(
        id=f"rss:item-{idx}",
        source_type=SourceType.RSS,
        title=f"Item {idx}",
        url=f"https://example.com/items/{idx}",
        content="content",
        author="tester",
        published_at=datetime(2026, 8, 11, 8, 0, tzinfo=timezone.utc),
        profile=profile,
        processing=ProcessingResult(
            classification=ClassificationResult(
                profile=profile, method="source_override"
            ),
            analysis=ContentAnalysis(
                score=score,
                reason=f"reason {idx}",
                summary=f"summary {idx}",
                tags=tags,
            ),
        ),
    )


def _summary(items, **kwargs):
    summarizer = DailySummarizer(**kwargs)
    return _run_async(
        summarizer.generate_summary(
            items, date="2026-08-11", total_fetched=100, language="zh"
        )
    )


def test_top_items_disabled_by_default():
    items = [_make_item(1, 9.0, ["ai"]), _make_item(2, 8.0, ["policy"])]
    result = _summary(items)

    assert "今天最值得关注" not in result
    assert "今日概览" not in result


def test_top_items_rendered_in_global_score_order_before_sections():
    items = [
        _make_item(1, 7.5, ["ai"], "china-news"),
        _make_item(2, 9.2, ["policy"], "world-news"),
        _make_item(3, 8.8, ["chips"], "ai-tech"),
        _make_item(4, 6.0, ["math"], "research-general"),
    ]
    result = _summary(items, top_items=3)

    assert "## 今天最值得关注的 3 件事" in result
    top_index = result.index("今天最值得关注")
    top_block = result[top_index : result.index("\n---", top_index)]

    order = [
        top_block.index("Item 2"),
        top_block.index("Item 3"),
        top_block.index("Item 1"),
    ]
    assert order == sorted(order)
    assert "Item 4" not in top_block
    assert "⭐️ 9.2/10" in top_block
    assert "为什么值得今天看: reason 2" in top_block


def test_top_items_topic_diversity_skips_same_event():
    items = [
        _make_item(1, 9.5, ["deepseek", "llm", "release"], "china-tech"),
        _make_item(2, 9.4, ["deepseek", "llm", "benchmark"], "ai-tech"),  # same event
        _make_item(3, 8.0, ["monetary", "pboc"], "china-economy"),
        _make_item(4, 7.0, ["nature", "protein"], "research-general"),
    ]
    result = _summary(items, top_items=3)
    top_index = result.index("今天最值得关注")
    top_block = result[top_index : result.index("\n---", top_index)]

    assert "Item 1" in top_block
    assert "Item 2" not in top_block
    assert "Item 3" in top_block
    assert "Item 4" in top_block


def test_top_items_never_repeats_same_url():
    items = [
        _make_item(1, 9.5, ["a", "b"], "china-news"),
        _make_item(2, 9.4, ["c", "d"], "china-news"),
        _make_item(3, 9.3, ["e", "f"], "china-news"),
    ]
    items[1].url = items[0].url  # duplicate URL entry
    items.append(_make_item(4, 6.0, ["g"], "china-news"))
    result = _summary(items, top_items=3)
    top_index = result.index("今天最值得关注")
    top_block = result[top_index : result.index("\n---", top_index)]

    assert top_block.count("example.com/items/1") == 1
    assert "Item 4" in top_block  # fill pass keeps the block at 3 entries


def test_top_items_falls_back_to_summary_and_handles_missing_score():
    item = _make_item(1, None, ["x"])
    item.processing.analysis.reason = ""
    result = _summary([item], top_items=1)

    assert "今天最值得关注的 1 件事" in result
    assert "为什么值得今天看: summary 1" in result
    assert "?/10" in result


def test_daily_overview_counts_and_focus():
    items = [
        _make_item(1, 8.0, ["ai", "llm"], "china-news"),
        _make_item(2, 7.5, ["ai"], "china-news"),
        _make_item(3, 7.0, ["policy"], "ai-tech"),
    ]
    result = _summary(items, daily_overview=True)

    assert "## 今日概览" in result
    assert "今天共扫描 100 条信息，保留 3 条。" in result
    assert "重点集中于" in result
    assert "`#ai`" in result


def test_overview_position_after_top_items():
    items = [_make_item(1, 8.0, ["ai"], "china-news")]
    result = _summary(items, top_items=1, daily_overview=True)

    assert result.index("今天最值得关注") < result.index("今日概览")


def test_digest_config_accepts_new_fields():
    config = DigestConfig(top_items=3, daily_overview=True)
    assert config.top_items == 3
    assert config.daily_overview is True
    default = DigestConfig()
    assert default.top_items == 0
    assert default.daily_overview is False
