"""Validation tests for the Personal Horizon production config example."""

import json
from pathlib import Path

from src.models import Config
from src.processing import ProfileRegistry

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "data" / "config.example.json"

PERSONAL_PROFILES = {
    "china-news",
    "china-tech",
    "china-economy",
    "world-news",
    "ai-tech",
    "research-general",
    "research-personal",
    "academic-opportunity",
    "github-projects",
}

EXPECTED_THRESHOLDS = {
    "china-news": 7.0,
    "china-tech": 6.8,
    "china-economy": 7.0,
    "world-news": 7.2,
    "ai-tech": 7.0,
    "research-general": 7.4,
    "research-personal": 6.3,
    "academic-opportunity": 6.0,
    "github-projects": 6.8,
}


def _load() -> Config:
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return Config.model_validate(raw)


def test_example_config_validates_against_schema():
    config = _load()
    assert config.processing.profiles_dir == "profiles"


def test_default_profile_is_a_personal_profile():
    config = _load()
    assert config.processing.default_profile in PERSONAL_PROFILES


def test_every_enabled_rss_source_has_category_and_personal_profile():
    config = _load()
    for feed in config.sources.rss:
        if not feed.enabled:
            continue
        assert feed.category, f"{feed.name} missing category"
        assert feed.profile in PERSONAL_PROFILES, (
            f"{feed.name} routes to unexpected profile {feed.profile}"
        )


def test_every_source_category_is_covered_by_a_digest_group():
    config = _load()
    grouped = {
        category
        for group in config.digest.category_groups.values()
        for category in group.categories
    }
    for feed in config.sources.rss:
        if feed.enabled:
            assert feed.category in grouped, f"{feed.category} not in any group"
    if config.sources.hackernews.enabled:
        assert config.sources.hackernews.category in grouped
    if config.sources.ossinsight.enabled:
        assert config.sources.ossinsight.category in grouped


def test_thresholds_match_personalization_spec():
    config = _load()
    for profile_id, expected in EXPECTED_THRESHOLDS.items():
        settings = config.processing.profile_settings.get(profile_id)
        assert settings is not None, f"{profile_id} missing profile_settings"
        assert settings.threshold == expected
        assert 0 <= settings.threshold <= 10


def test_profile_order_lists_every_loaded_profile_exactly_once():
    config = _load()
    registry = ProfileRegistry.load(REPO_ROOT / "profiles", "china-news")
    assert sorted(config.digest.profile_order) == sorted(registry.ids)


def test_digest_limits_are_consistent_with_daily_cap():
    config = _load()
    assert config.digest.max_items == 20
    group_total = sum(
        group.limit for group in config.digest.category_groups.values()
    )
    assert group_total == 20


def test_no_duplicate_feed_urls():
    config = _load()
    urls = [str(feed.url) for feed in config.sources.rss if feed.enabled]
    assert len(urls) == len(set(urls))


def test_no_secrets_in_example_config():
    raw = CONFIG_PATH.read_text(encoding="utf-8")
    config = json.loads(raw)
    assert config["ai"]["api_key_env"].endswith("_API_KEY")
    for marker in ("sk-", "ghp_", "apify_api_"):
        assert marker not in raw
