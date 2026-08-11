# Personal Horizon — Final Report

日期：2026-08-11 · 分支：`personal-horizon` · 基线：`80bde6db`（Thysrael/Horizon main）

## 1. 修改了什么

| 类别 | 内容 | 涉及文件 |
|---|---|---|
| 用户画像 | 长期兴趣、可靠性分级、过滤原则 | `config/user_interests.md` |
| 9 个 personal profiles | 每个含 profile.json / match.md / analysis.md / enrichment.md，内置 Personal Score 6 维评分与中文输出规则 | `profiles/china-news`, `china-tech`, `china-economy`, `world-news`, `ai-tech`, `research-general`, `research-personal`, `academic-opportunity`, `github-projects` |
| 生产配置 | 47 个 RSS 源 + HN + OSS Insight；9 个 profile 的 threshold/topic_dedup；category quota；profile_order；`languages: ["zh"]`；`top_items: 3`；`daily_overview: true` | `data/config.example.json`（`data/config.json` 为本地副本，已 gitignore） |
| Top 3 + 今日概览（最小 src 改动） | `DigestConfig` 新增 2 个可选字段；`DailySummarizer` 新增纯程序渲染（默认关闭，上游行为不变）；orchestrator 两个调用点接线 | `src/models.py`（+2 字段）、`src/ai/summarizer.py`（+约 130 行）、`src/orchestrator.py`（+4 行） |
| 测试 | Top 3 单测 8 个；生产配置校验 10 个；选择流水线集成测试 4 个 | `tests/test_top_items.py`, `test_personal_config.py`, `test_personal_integration.py` |
| 文档 | baseline、sources catalog、personalization、future | `docs/baseline.md`, `docs/sources_catalog.md`, `docs/PERSONALIZATION.md`, `docs/FUTURE.md`, `README.md`（新增 Personal Horizon 一节） |
| 工具脚本 | 源可用性测试与生产配置 fetch 集成测试 | `scripts/test_feeds*.py`, `scripts/fetch_test.py` |

## 2. 没修改什么（刻意保留）

- 抓取、去重、分析、enrichment、渲染、投递的全部核心 pipeline —— 零改动
- 内置 profiles（tech-news / tech-blog / finance-news / ai-creator）—— 原样保留
- GitHub Actions daily workflow、cron 时间 —— 未动
- Email / Webhook / MCP 能力 —— 未动
- 返回 schema（score/reason/summary/tags）—— 未动
- 上游 merge 兼容性：src 改动均为向后兼容的可选新增（默认关闭）

## 3. 为什么这样设计

- **配置与 prompt 优先**：Horizon 的 profile 体系（match/analysis/enrichment +
  运行时 threshold/quota）本身就能表达个性化评分，只有 "Top 3" 这一渲染层
  需求无法用现有机制实现，因此 src 改动仅限于 summarizer 的纯程序渲染。
- **评分在 prompt 里**：Personal Score 六维（重要性 3 / 相关度 3 / 可行动 1.5 /
  新颖 1 / 可信 1 / 时效 0.5）写进每个 profile 的 analysis.md，不同 profile
  权重不同（research-personal 相关度权重最高），不动数据结构。
- **成本两段式**：全部抓取 → 短文本评分（~1200 字符/条）→ threshold+quota →
  仅 ≤20 条做 enrichment（部分 block 允许 web_search）。不全局开全文抽取。

## 4. 使用了哪些中国源

中国官方网站均无 RSS，公共 RSSHub 实例全部不可用（详见下节），V1 采用：

- **Google News 中文查询**（4 个主题：国务院/教育部/科技部、自然科学基金/科研政策、
  大模型/AI/半导体、央行/统计局/宏观）——聚合官方与专业媒体报道，可靠性 B
- **中新网即时新闻**（官方 RSS，B）
- **量子位、InfoQ 中文、钛媒体**（官方 RSS，B）+ **Solidot**（C）
- 财新/一财/界面/36氪/机器之心因付费墙或 feed 损坏未纳入（见 catalog）

## 5. 哪些源不稳定

- **CBC**（2 个 feed）：间歇性 ConnectError，标记 unstable；pipeline 容错不受影响
- **Google News**：短时间重复抓取会触发限流（SSL reset）；每日一次正常
- **SIAM**：本网络 403，未接入
- **36氪/机器之心/财新/虎嗅**：feed 损坏或反爬，未接入
- **人民网**：feed 停更（最新 2025-06），弃用
- **RSSHub（demo 及公共实例）**：403/522，V1 完全不依赖；自建实例列入 FUTURE

## 6. Scoring 如何工作

每个条目路由到源绑定的 profile → 该 profile 的 analysis.md 用 Personal Score
六维打分（0-10，含来源可信度 A/B/C/D 评级）→ `processing.profile_settings`
按 profile 应用 threshold → topic dedup → category quota → enrichment。

## 7. Thresholds 与 Quota

Thresholds：china-news 7.0 / china-tech 6.8 / china-economy 7.0 /
world-news 7.2 / ai-tech 7.0 / research-general 7.4 / research-personal 6.3 /
academic-opportunity 6.0 / github-projects 6.8。

Quota：china ≤5、world ≤3、ai ≤4、research ≤4、opportunity ≤2、github ≤2，
总量硬上限 20；quota 是上限，允许栏目为 0，绝不填满。

## 8. Top 3 如何产生

最终保留条目 → 全局分数降序 → topic diversity（与已选共享 ≥2 个分析标签者跳过，
同 URL 永不重复）→ 不足 3 条按分数补齐 → 复用 `analysis.reason` 渲染
"为什么值得今天看"。**零额外 LLM 调用**。今日概览（扫描数/保留数/重点栏目与标签）
同为纯程序计算。两处功能默认关闭，由 `digest.top_items` / `digest.daily_overview` 开启。

## 9. 每日 API 调用规模（估算）

- 抓取量：~675 条/天（生产配置实测）
- 分析调用：≈650 次（URL 去重后，analysis_concurrency=4，输入 ≤1.2k 字符/条）
- Enrichment：≤20 条 ×（1 次主调用 + 至多 2 次 web_search 辅助）≈ 20–60 次
- 合计：约 700 次小调用/天；以 DeepSeek 类廉价模型计，日成本约 1–3 元人民币量级

## 10. 已知问题

1. **Phase 4 完整 pipeline 实跑受阻**：当前环境无有效 AI API key（环境中的
   `KIMI_API_KEY` 对 Moonshot 开放平台两端点均 401），`sample_digest_v1.md`
   待用户提供 key 后生成。基线运行已验证：抓取正常、AI 全部 401 时 pipeline
   不崩溃、正常产出空日报。
2. 本机 23 个上游测试因代理 fake-IP DNS（198.18.x）与 Windows 路径断言失败，
   属环境问题（见 baseline.md），CI/正常网络下应为绿。
3. 中国官方一手源覆盖为间接方案（Google News 聚合），可靠性 B；自建 RSSHub 可升级。
4. 周刊类期刊（Science/PNAS/INFORMS 等）多数日子 0 条，属正常出版节奏。
5. Anthropic/Meta/Microsoft 无可用 feed，由科技媒体覆盖。

## 11. 后续最值得优化的 3 件事

1. **完成 Phase 4 实跑**：接入有效 API key → 跑 24h pipeline → 人工评审
   `sample_digest_v1.md` → 按评审结果调 thresholds。
2. **自建 RSSHub**：恢复中国官方一手源（gov.cn/部委/NSFC/新华社）与
   财新/一财/机器之心，把 China Tier A 来源可靠性从 B 升到 A。
3. **跨语言同事件去重验证**：用真实日报检查中英媒体同事件是否被 topic dedup
   正确合并；若不足，再做最小化跨语言语义去重（FUTURE.md 已记录，不上向量库）。

## 12. 验收状态

- Functional：除"完整 pipeline 实跑"（待 API key）外全部就绪；配置校验与
  选择流水线由 `test_personal_config.py` / `test_personal_integration.py` 覆盖
- Engineering：secrets 不入 Git ✓ / 上游可 merge（改动向后兼容）✓ /
  核心 Python 改动最小 ✓ / 新功能有测试 ✓ / pytest 无新增失败 ✓ /
  README 部署说明 ✓ / sources_catalog 完整 ✓
- Quality：待 Phase 4 实跑后人工评审
