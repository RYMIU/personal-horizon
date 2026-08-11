# Phase 0 — Baseline

Date: 2026-08-11

## Environment

- Upstream: `Thysrael/Horizon`, branch `main`
- Baseline commit SHA: `80bde6db03008678111fb627b471792c7ac05a94` (2026-08-10, "chore: keep AI creator prompt only")
- Working branch: `personal-horizon`
- OS: Windows (Git Bash)
- Python: 3.12.10 (`.venv`, created by `uv sync --extra dev`); host managed Python 3.12.13
- Package manager: uv (`uv.lock` present)

## Dependency installation

```bash
uv sync --extra dev
```

Completed without errors. `trafilatura` is a core dependency (not only an
optional extra), so the default install includes the full-text extractor.

## Test results (baseline)

Command: `uv run pytest -q`

- Total: 514 tests
- Passed: 491
- Failed: 23 — **all environmental, none caused by upstream code**

| Test file | Failures | Root cause |
|---|---|---|
| `tests/test_webhook.py` | 20 | Local DNS resolves test domains (e.g. `example.com`) to `198.18.0.215` (fake-IP range used by a local proxy/VPN TUN mode). Horizon's SSRF guard correctly rejects non-public addresses, so the tests fail. Expected to pass on a normal network / CI. |
| `tests/test_extractors_trafilatura.py` | 1 | Same fake-IP DNS issue: fetch is rejected by the SSRF guard before extraction. |
| `tests/test_setup_wizard.py` | 2 | Windows path separator: code produces `data\presets.json`, test expects `data/presets.json`. Platform-specific test expectation, not a runtime bug. |

Conclusion: the suite is green on a standard Linux/macOS CI runner with normal
DNS. On this machine, treat these 23 failures as the known-failure set; any new
failure outside this set is a regression.

## Minimal pipeline run

Config: single RSS source (Simon Willison), threshold 7.0, 48h window,
provider `openai` with `base_url=https://api.moonshot.cn/v1` and
`api_key_env=KIMI_API_KEY`.

Command: `uv run horizon --hours 48 -l INFO`

Observed:

- Fetch: RSS 200 OK, 5 items; HN topstories also fetched (see below).
- Analysis: 17 items sent to AI; all failed with `401 Unauthorized` — the
  ambient `KIMI_API_KEY` in this environment is **not** a valid Moonshot
  platform API key (verified independently against both
  `api.moonshot.cn` and `api.moonshot.ai`).
- Result: 0 items selected, pipeline still completed successfully, saved
  `data/summaries/horizon-2026-08-11-en.md` and copied a GitHub Pages post.
- **Resilience confirmed**: total AI-stage failure does not crash the run,
  which matches the project's failure-handling design.

## Key findings that shape the personalization work

1. **Sources default to enabled.** `HackerNewsConfig.enabled`,
   `RedditConfig.enabled`, `TelegramConfig.enabled` (and similar) default to
   `True`. Any source type we do not want must be explicitly set to
   `"enabled": false` in `data/config.json`, otherwise it is fetched even when
   absent from the config (observed: HN topstories fetched with only an RSS
   section present).
2. **Profile system is file-based and additive.** New profiles under
   `profiles/<id>/` (`profile.json`, `match.md`, `analysis.md`,
   `enrichment.md`) require no Python changes; thresholds and `topic_dedup`
   live in `processing.profile_settings`.
3. **Balanced digest exists natively** (`digest.max_items`,
   `digest.category_groups`, `digest.default_group(_limit)`,
   `digest.profile_order`) — quotas run after profile filtering and topic
   dedup, before enrichment.
4. **Digest structure**: H1 title, H2 = localized profile name
   (`display_names.zh`), H3 = items; section order controlled by
   `digest.profile_order`. A `primary` enrichment block renders directly under
   the item title.
5. **AI provider is OpenAI-compatible-friendly** (`ai.base_url` supported), so
   DeepSeek / DashScope / Doubao / MiniMax / Ollama etc. can be used via
   config only. No key may be committed; `api_key_env` + `.env` is the
   mechanism.
6. **Cross-source dedup exists**: same normalized URL + same profile merges
   before analysis; AI topic dedup per profile (`topic_dedup`, default true).
7. **Bilingual output is native** (`ai.languages`); `zh` artifacts are
   normalized to Simplified Chinese automatically.

## Baseline behavior notes

- Output paths: `data/summaries/horizon-<date>-<lang>.md`;
  `docs/_posts/<date>-summary-<lang>.md` for GitHub Pages.
- CLI: `horizon [--hours N] [-d data-dir] [-c config] [-l LEVEL]`.
- Scripts: `horizon`, `horizon-mcp`, `horizon-wizard`, `horizon-webhook`.

## Blocker for later phases

A valid AI API key is required for scoring/enrichment. None is currently
available (see "Minimal pipeline run"). Phases 1–3 (profiles, source catalog,
fetch integration) do not require AI; Phase 4 (full personalized digest) does.
