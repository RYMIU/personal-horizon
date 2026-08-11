"""Unit tests for the email brief mode (Top-N + overview + link notification)."""

from src.ai.summarizer import DailySummarizer
from src.models import EmailConfig
from tests.test_top_items import _make_item


def _brief(items, link="https://example.github.io/horizon/2026/08/11/summary-zh.html", **kwargs):
    kwargs.setdefault("top_items", 3)
    kwargs.setdefault("daily_overview", True)
    summarizer = DailySummarizer(**kwargs)
    return summarizer.generate_brief(
        items, date="2026-08-11", total_fetched=100, language="zh", link=link
    )


def test_email_config_new_fields_default_off():
    config = EmailConfig(
        imap_server="imap.example.com",
        smtp_server="smtp.example.com",
        email_address="bot@example.com",
    )
    assert config.brief is False
    assert config.recipients == []
    assert config.pages_url is None
    assert config.imap_enabled is True  # upstream default unchanged


def test_email_config_accepts_brief_mode():
    config = EmailConfig(
        imap_server="imap.qq.com",
        imap_enabled=False,
        smtp_server="smtp.qq.com",
        email_address="bot@qq.com",
        brief=True,
        recipients=["me@qq.com"],
        pages_url="https://me.github.io/horizon",
    )
    assert config.brief is True
    assert config.recipients == ["me@qq.com"]
    assert config.imap_enabled is False


def test_brief_contains_top_overview_count_and_link():
    items = [
        _make_item(1, 7.5, ["ai"], "china-news"),
        _make_item(2, 9.2, ["policy"], "world-news"),
        _make_item(3, 8.8, ["chips"], "ai-tech"),
        _make_item(4, 6.0, ["math"], "research-general"),
    ]
    result = _brief(items)

    assert "## 今天最值得关注的 3 件事" in result
    assert "## 今日概览" in result
    assert "今天共扫描 100 条信息，保留 4 条。" in result
    assert "[查看完整日报](https://example.github.io/horizon/2026/08/11/summary-zh.html)" in result


def test_brief_excludes_full_digest_body():
    items = [_make_item(1, 9.0, ["ai"], "china-news")]
    result = _brief(items)

    # Full digest renders anchor links and per-profile body sections; brief must not.
    assert "](#" not in result
    assert "为什么值得今天看" in result  # top block still present


def test_brief_without_link_omits_footer():
    items = [_make_item(1, 9.0, ["ai"], "china-news")]
    result = _brief(items, link=None)

    assert "查看完整日报" not in result


def test_brief_empty_items_still_sends_overview_and_link():
    result = _brief([])

    assert "已分析 100 条内容" in result
    assert "查看完整日报" in result


def test_brief_english_labels():
    items = [_make_item(1, 9.0, ["ai"], "china-news")]
    summarizer = DailySummarizer(top_items=3, daily_overview=True)
    result = summarizer.generate_brief(
        items, date="2026-08-11", total_fetched=50, language="en", link=None
    )

    assert "Today's Top 1" in result
    assert "Daily Overview" in result
    assert "kept 1" in result
