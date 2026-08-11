"""Integration tests: simulated end-to-end selection with the production config.

Simulates: 100 raw items -> threshold filter -> quota (balanced digest) ->
Top-3 selection -> digest size cap, using the real production config example.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from rich.console import Console

from src.ai.summarizer import DailySummarizer
from src.models import (
    ClassificationResult,
    Config,
    ContentAnalysis,
    ContentItem,
    ProcessingConfig,
    ProcessingResult,
    SourceType,
)
from src.orchestrator import HorizonOrchestrator

REPO_ROOT = Path(__file__).resolve().parents[1]

PROFILE_BY_CATEGORY = {
    "china-news": "china-news",
    "china-tech": "china-tech",
    "china-economy": "china-economy",
    "world-news": "world-news",
    "ai-tech": "ai-tech",
    "research-general": "research-general",
    "research-personal": "research-personal",
    "academic-opportunity": "academic-opportunity",
    "github-projects": "github-projects",
}


def _config() -> Config:
    raw = json.loads(
        (REPO_ROOT / "data" / "config.example.json").read_text(encoding="utf-8")
    )
    return Config.model_validate(raw)


def _make_item(idx: int, category: str, score: float) -> ContentItem:
    profile = PROFILE_BY_CATEGORY[category]
    return ContentItem(
        id=f"rss:{category}-{idx}",
        source_type=SourceType.RSS,
        title=f"{category} story {idx}",
        url=f"https://example.com/{category}/{idx}",
        published_at=datetime(2026, 8, 11, 8, 0, tzinfo=timezone.utc),
        metadata={"category": category},
        profile=profile,
        processing=ProcessingResult(
            classification=ClassificationResult(
                profile=profile, method="source_override"
            ),
            analysis=ContentAnalysis(
                score=score, reason=f"reason {idx}", summary=f"summary {idx}",
                tags=[category, f"topic-{idx % 7}"],
            ),
        ),
    )


def _orchestrator(config: Config) -> HorizonOrchestrator:
    orchestrator = HorizonOrchestrator.__new__(HorizonOrchestrator)
    orchestrator.config = SimpleNamespace(
        digest=config.digest,
        processing=ProcessingConfig(
            profile_settings=config.processing.profile_settings
        ),
    )
    orchestrator.console = Console(record=True)
    return orchestrator


def _hundred_items(config: Config) -> list:
    """100 raw items spread across categories, most below threshold."""
    items = []
    plan = {
        "china-news": 20,
        "china-tech": 18,
        "china-economy": 12,
        "world-news": 12,
        "ai-tech": 14,
        "research-general": 10,
        "research-personal": 8,
        "academic-opportunity": 3,
        "github-projects": 3,
    }
    idx = 0
    for category, count in plan.items():
        threshold = config.processing.profile_settings[
            PROFILE_BY_CATEGORY[category]
        ].threshold
        for i in range(count):
            # Every third item clears the threshold, the rest fall short.
            score = threshold + 0.5 if i % 3 == 0 else threshold - 1.0
            items.append(_make_item(idx, category, round(score, 2)))
            idx += 1
    return items


def test_pipeline_of_100_items_respects_cap_and_group_limits():
    config = _config()
    items = _hundred_items(config)
    assert len(items) == 100

    # Threshold filtering (emulates per-profile score filter)
    passing = [
        item
        for item in items
        if item.processing.analysis.score
        >= config.processing.profile_settings[
            item.processing.classification.profile
        ].threshold
    ]
    assert 0 < len(passing) < len(items)

    result = _orchestrator(config).apply_balanced_digest(passing)
    assert len(result.items) <= config.digest.max_items

    limits = {
        "china": 5,
        "world": 3,
        "ai": 4,
        "research": 4,
        "opportunity": 2,
        "github": 2,
    }
    for group, cap in limits.items():
        assert result.group_counts.get(group, 0) <= cap


def test_group_quota_never_force_fills_empty_categories():
    config = _config()
    items = [
        _make_item(1, "china-news", 9.0),
        _make_item(2, "china-news", 8.0),
    ]
    result = _orchestrator(config).apply_balanced_digest(items)

    assert len(result.items) == 2
    assert result.group_counts == {"china": 2}


def test_top3_after_quota_uses_global_score_and_stays_diverse():
    config = _config()
    items = _hundred_items(config)
    passing = [
        item
        for item in items
        if item.processing.analysis.score
        >= config.processing.profile_settings[
            item.processing.classification.profile
        ].threshold
    ]
    selected = _orchestrator(config).apply_balanced_digest(passing).items

    summarizer = DailySummarizer(top_items=config.digest.top_items)
    top = summarizer._select_top_items(items=selected, count=3)

    assert len(top) == 3
    assert len({str(item.url) for item in top}) == 3
    scores = [item.processing.analysis.score for item in top]
    assert scores == sorted(scores, reverse=True)
    assert min(scores) >= min(
        item.processing.analysis.score for item in selected
    )


def test_survives_items_with_missing_metadata_and_analysis():
    config = _config()
    bare = ContentItem(
        id="rss:bare-1",
        source_type=SourceType.RSS,
        title="bare item",
        url="https://example.com/bare/1",
        published_at=datetime(2026, 8, 11, 8, 0, tzinfo=timezone.utc),
        profile="china-news",
    )
    scored = _make_item(2, "china-news", 9.0)

    result = _orchestrator(config).apply_balanced_digest([bare, scored])
    assert scored in result.items

    summarizer = DailySummarizer(top_items=3, daily_overview=True)
    summary = summarizer.generate_webhook_overview(
        result.items, date="2026-08-11", total_fetched=2, language="zh"
    )
    assert "bare item" in summary
