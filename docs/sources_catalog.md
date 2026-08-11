# Personal Horizon — Sources Catalog

Phase 2 source discovery results. Every source listed here was fetch-tested on
**2026-08-11** from the project network (China ISP) using Horizon's own
fetch stack (`httpx` + `feedparser`, browser UA, redirect following).
Test harness: `scripts/test_feeds.py`, `scripts/test_feeds_r2.py`, `scripts/test_feeds_r3.py`.

Reliability tiers: **A** = primary/official/original paper ·
**B** = established professional source · **C** = community/secondary/discovery ·
**D** = unknown/weak.

Status: `working` / `unstable` / `blocked` / `deprecated` / `not-used`.

---

## 1. China — official & policy (Tier A substitutes)

Chinese government bodies (gov.cn, MOE, MOST, NBS, PBOC, NSFC, CAS, Xinhua)
publish **no official RSS**. The normal fallback would be RSSHub, but the
public demo (`rsshub.app`) returns HTTP 403 for every route and tested public
instances (`rsshub.pseudoyu.com`, `rsshub.woodland.cafe`) were down (522/503).
Chinese official coverage therefore uses **Google News Chinese queries**
(which aggregate gov.cn, Xinhua, People.cn, CCTV and professional media) plus
selected direct feeds. Self-hosting RSSHub remains a documented future option.

| Source | Region | Category | Method | Reliability | Status | Notes |
|---|---|---|---|---|---|---|
| Google News CN — 国务院/教育部/科技部 | CN | china-news | Google News RSS (`hl=zh-CN&gl=CN&ceid=CN:zh`, `when:2d`) | B | working | 91 entries/2d; aggregates official + pro media |
| Google News CN — 大模型/人工智能 | CN | china-tech | Google News RSS | B | working | 100 entries/2d |
| Google News CN — 央行/统计局/宏观经济 | CN | china-economy | Google News RSS | B | planned | same mechanism as above |
| Google News CN — 国家自然科学基金/科研政策 | CN | china-news | Google News RSS | B | planned | same mechanism |
| chinanews.com 中新网即时新闻 | CN | china-news | official RSS | B | working | 30 entries, fresh |
| people.com.cn 人民网时政 | CN | china-news | official RSS | B | deprecated | feed stale: latest entry 2025-06-05; not used |
| gov.cn / MOE / MOST / NBS / PBOC / NSFC / CAS / Xinhua via rsshub.app | CN | various | RSSHub demo | A | blocked | HTTP 403 all routes; demo instance closed |
| same via rsshub.pseudoyu.com / woodland.cafe | CN | various | RSSHub public | A | blocked | 522/503 instance down |

## 2. China — professional media (Tier B)

| Source | Region | Category | Method | Reliability | Status | Notes |
|---|---|---|---|---|---|---|
| 量子位 QbitAI | CN | china-tech | official RSS | B | working | 10 entries, fresh |
| InfoQ 中文 | CN | china-tech | official RSS | B | working | 20 entries, fresh |
| 钛媒体 TMTPost | CN | china-tech/economy | official RSS | B | working | 16 entries, fresh |
| cnBeta | CN | china-tech | official RSS | C | working | 150 entries; high volume, discovery-grade quality |
| Solidot | CN | china-tech | official RSS | C | working | 20 entries; community tone |
| 36氪 | CN | china-tech | official RSS | B | unstable | feed malformed XML (`invalid token`), 0 parseable entries |
| 机器之心 | CN | china-tech | official RSS | B | unstable | serves HTML instead of RSS (anti-bot), 0 entries |
| 财新 | CN | china-economy | official RSS | B | unstable | malformed XML; also paywalled — do not use |
| 虎嗅 | CN | china-tech | official RSS | B | unstable | read timeout |
| 36氪/机器之心/财新/一财/界面 via RSSHub | CN | various | RSSHub | B | blocked | instance 403/522 |

## 3. International media

| Source | Region | Category | Method | Reliability | Status | Notes |
|---|---|---|---|---|---|---|
| BBC World | INTL | world-news | official RSS | B | working | 21 entries, fresh |
| The Guardian World | INTL | world-news | official RSS | B | working | 45 entries |
| NYT World | INTL | world-news | official RSS | B | working | 56 entries |
| CBC Top Stories | INTL(CA) | world-news | official RSS | B | working | 20 entries; Canada focus |
| CBC World | INTL(CA) | world-news | official RSS | B | working | 20 entries |
| AP Top News via RSSHub | INTL | world-news | RSSHub | B | blocked | instance 403 |

## 4. AI / Technology

| Source | Region | Category | Method | Reliability | Status | Notes |
|---|---|---|---|---|---|---|
| OpenAI News | AI | ai-tech | official RSS | A | working | full archive feed; window filter applies |
| Google DeepMind Blog | AI | ai-tech | official RSS | A | working | 100 entries |
| Google AI Blog | AI | ai-tech | official RSS | A | working | 20 entries |
| NVIDIA Blog | AI | ai-tech | official RSS | A | working | 18 entries, fresh |
| Hugging Face Blog | AI | ai-tech | official RSS | B | working | 839 entries |
| Simon Willison | AI | ai-tech | official Atom | B | working | 30 entries |
| MIT Technology Review | AI | ai-tech | official RSS | B | working | 10 entries, fresh |
| TechCrunch AI | AI | ai-tech | official RSS | B | working | 20 entries, fresh |
| The Verge AI | AI | ai-tech | official RSS | B | working | 10 entries, fresh |
| Ars Technica AI | AI | ai-tech | official RSS | B | working | 20 entries |
| vLLM Blog | AI | ai-tech | official RSS | A | working | 50 entries |
| Anthropic | AI | ai-tech | official RSS | A | not-used | no public RSS found (`/rss.xml`, `/news/rss.xml` both 404); covered via tech media + Google News |
| Meta AI Blog | AI | ai-tech | official RSS | A | not-used | feed endpoint HTTP 400; covered via media |
| Microsoft AI Blog | AI | ai-tech | official RSS | A | blocked | HTTP 403 (bot protection); covered via media |

## 5. Research

| Source | Region | Category | Method | Reliability | Status | Notes |
|---|---|---|---|---|---|---|
| Nature | RES | research-general | official RSS | A | working | 75 entries, fresh |
| Nature Communications | RES | research-general | official RSS | A | working | 8 entries |
| Nature Machine Intelligence | RES | research-general | official RSS | A | working | 8 entries |
| Nature Computational Science | RES | research-general | official RSS | A | working | 8 entries |
| Science | RES | research-general | Atypon showFeed RSS | A | working | 36 entries |
| PNAS | RES | research-general | Atypon showFeed RSS | A | working | 84 entries |
| Cell | RES | research-general | official RSS | A | working | 20 entries |
| arXiv q-bio.PE | RES | research-personal | official RSS | A | working | 4 entries; epidemiology core |
| arXiv stat.ML | RES | research-personal | official RSS | A | working | 76 entries |
| arXiv math.OC | RES | research-personal | official RSS | A | working | 111 entries; optimization core |
| arXiv cs.LG | RES | research-general | official RSS | A | working | 570 entries; high volume |
| bioRxiv (all) | RES | research-general | official RSS | A | working | 30 entries |
| medRxiv (all) | RES | research-general | official RSS | A | working | 30 entries |
| INFORMS Operations Research | RES | research-personal | Atypon showFeed RSS | A | working | 75 entries |
| INFORMS J. on Computing | RES | research-personal | Atypon showFeed RSS | A | working | 138 entries |
| Mathematical Biosciences (Elsevier) | RES | research-personal | ScienceDirect journal RSS | A | working | 43 entries |
| Journal of Mathematical Biology (Springer) | RES | research-personal | Springer search RSS | A | working | 20 entries |
| SIAM J. Applied Math | RES | research-personal | Atypon showFeed | A | blocked | HTTP 403; SIAM blocks feed fetch from this network |
| PLOS Computational Biology | RES | research-general | official RSS | A | blocked | HTTP 404 on `/feed`; needs re-investigation |
| eLife | RES | research-general | official RSS | A | blocked | HTTP 406 |

## 6. Academic opportunities

| Source | Region | Category | Method | Reliability | Status | Notes |
|---|---|---|---|---|---|---|
| NIH Funding Opportunities | ACA | academic-opportunity | official RSS (`grants.nih.gov/grants/guide/newsfeed/fundingopps.xml`) | A | working | 2 entries; low volume is normal |
| Mitacs | ACA | academic-opportunity | official RSS | A | working | 12 entries |
| Simons Foundation | ACA | academic-opportunity | official RSS | A | working | 10 entries |
| Google News CA — NSERC/Mitacs/CIHR funding | ACA | academic-opportunity | Google News RSS (`hl=en-CA&gl=CA&ceid=CA:en`, `when:14d`) | C | working | 14 entries/14d; discovery channel |
| NSF funding RSS | ACA | academic-opportunity | official RSS | A | blocked | legacy URLs 404 after site redesign; needs new endpoint |
| Wellcome | ACA | academic-opportunity | official RSS | A | blocked | 404 on tested endpoints |
| UBC Grad School | ACA | academic-opportunity | official RSS | A | blocked | 404/SSL errors on tested endpoints |
| canada.ca (NSERC/CIHR/SSHRC) Atom | ACA | academic-opportunity | official Atom | A | unstable | endpoint returns HTML (bot protection), 0 entries |
| CSC (国家留学基金委) | ACA | academic-opportunity | — | A | not-used | no feed; check site manually or via Google News |

## 7. GitHub projects

| Source | Region | Category | Method | Reliability | Status | Notes |
|---|---|---|---|---|---|---|
| OSS Insight trending | OSS | github-projects | Horizon native `ossinsight` source (API) | B | planned | config: period `past_24_hours`, languages All/Python/TypeScript/Jupyter Notebook, `max_items` 30 → quota 2 |

---

## Decisions for Phase 3 integration

1. **No RSSHub dependency in production V1.** All Chinese coverage via
   Google News RSS (Horizon's native `google_news` source) + direct feeds.
   Self-hosted RSSHub documented in `docs/FUTURE.md` only.
2. **Google News as Tier A substitute, marked B reliability.** Analysis prompts
   already downgrade unverifiable claims; Google News items carry publisher
   names in titles, and topic dedup merges duplicates across outlets.
3. **Broken Chinese media feeds (36kr, 机器之心, 财新, 虎嗅) excluded from V1.**
4. **Anthropic / Meta AI / Microsoft AI** have no fetchable feed from this
   network; they are covered through tech-media sources and receive no special
   treatment.
5. **Blocked academic feeds** (NSF, Wellcome, UBC, canada.ca) are replaced by
   the working set (NIH, Mitacs, Simons) + Google News CA funding discovery.
6. **SIAM blocked (403)** from this network; INFORMS + Elsevier + Springer
   cover OR/math-bio journals instead.
