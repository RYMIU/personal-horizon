# Personal Horizon — 个性化设计说明

本文件说明 Personal Horizon 如何在**不修改 Horizon 核心架构**的前提下实现个性化每日情报。

## 总览

```text
47 个 RSS/Atom 源 + Hacker News + OSS Insight
        ↓ fetch（单源失败不拖垮 pipeline）
   URL 去重（跨源同链接同 profile 合并）
        ↓
   Profile 路由（每个源显式绑定 9 个 personal profile 之一）
        ↓
   Personal Score（analysis.md 内置 6 维评分，0-10）
        ↓
   Threshold（processing.profile_settings，按 profile）
        ↓
   Topic Dedup（AI 主题去重，跨语言同事件合并）
        ↓
   Category Quota（digest.category_groups，宁缺毋滥）+ max_items=20
        ↓
   Enrichment（仅对最终保留的 ≤20 条：发生了什么/为什么重要/为什么值得我关注）
        ↓
   Top 3（全局分数排序 + 主题多样性，纯程序计算，无额外 LLM 调用）
        ↓
   简体中文日报 → data/summaries/ + GitHub Pages
```

## 用户画像

`config/user_interests.md` 是所有评分的依据。九个 profile 的
`analysis.md` 把画像转化为各自的 Personal Score 细则：

```text
Importance         0-3    事件本身的重要性
Personal relevance 0-3    与用户画像的相关度（research-personal 权重最高）
Actionability      0-1.5  是否需要/可以采取行动
Novelty            0-1    新颖性
Credibility        0-1    来源可信度（A 官方/原始论文 → D 未知弱源）
Timeliness         0-0.5  时效性
                   -----
Total              0-10
```

输出 schema 完全沿用 Horizon 原生 `score / reason / summary / tags`。

## Thresholds（初值，后续按日报质量调参）

| Profile | Threshold | 说明 |
|---|---|---|
| china-news | 7.0 | |
| china-tech | 6.8 | |
| china-economy | 7.0 | |
| world-news | 7.2 | 最严格的国际过滤 |
| ai-tech | 7.0 | |
| research-general | 7.4 | 最高阈值，只要真正重要的成果 |
| research-personal | 6.3 | 最低阈值：niche but highly relevant |
| academic-opportunity | 6.0 | 机会类宁多勿漏 |
| github-projects | 6.8 | |

## Category Quota（digest.category_groups）

| Group | Limit | Categories |
|---|---|---|
| china | 5 | china-news, china-tech, china-economy |
| world | 3 | world-news |
| ai | 4 | ai-tech |
| research | 4 | research-general, research-personal |
| opportunity | 2 | academic-opportunity |
| github | 2 | github-projects |

`max_items = 20`。quota 是上限不是目标：某栏目当天可以为 0，绝不强制填满。

## Top 3 与今日概览

`digest.top_items: 3`、`digest.daily_overview: true` 启用（默认关闭，上游行为不变）。

- **Top 3**：从最终保留条目中按全局分数排序选取；候选与已选条目共享 ≥2 个
  分析标签时视为同一事件跳过（topic diversity）；同一 URL 最多出现一次；
  不足 3 条时按分数补齐。复用 `analysis.reason`（无则 `summary`），无额外 LLM 调用。
- **今日概览**：扫描数/保留数 + 条目最多的 3 个栏目与 3 个高频标签，纯程序计算。

## 中文输出

`ai.languages: ["zh"]` —— 只生成简体中文日报（需要英文时改为 `["en", "zh"]`）。
栏目名来自各 profile 的 `display_names.zh`，顺序由 `digest.profile_order` 固定。
enrichment prompt 内置规则：论文标题/模型名/软件名保留英文，专业术语首次出现保留中英，
不编造事实、deadline 或论文内容。`zh` 产物自动做繁简归一。

## 部署

1. 复制配置：`cp data/config.example.json data/config.json`
2. 配置密钥（任选一家 OpenAI 兼容 provider，推荐便宜快速的模型）：

   ```bash
   cp .env.example .env
   # .env 中填入 DEEPSEEK_API_KEY / DASHSCOPE_API_KEY / OPENAI_API_KEY 等
   ```

   修改 `data/config.json` 的 `ai.provider`、`ai.model`、`ai.api_key_env`
   （`deepseek` / `ali`(通义) / `doubao` / `minimax` / `gemini` / `openai` 均已内置，
   前四类对国内网络友好）。`data/config.example.json` 保持上游默认 openai 以兼容上游测试。
3. 本地运行：`uv run horizon --hours 24`
4. GitHub Actions：复用上游 `.github/workflows/daily-summary.yml`，
   在仓库 Secrets 中配置同名密钥；`workflow_dispatch` 可手动触发。
   cron 时间保持项目默认，不擅自绑定个人时区。

## 调参指引

- 某栏目垃圾太多 → 提高对应 profile threshold（每次 +0.2）
- 漏掉重要新闻 → 降低 threshold 或检查来源可靠性评级
- 某栏目长期为 0 → 正常（宁缺毋滥）；若长期想要更多，先加源再降阈值
- 源失效 → 在 `docs/sources_catalog.md` 更新 status，换同类源

## 测试

```bash
uv run pytest tests/test_profiles.py tests/test_prompting.py \
  tests/test_top_items.py tests/test_personal_config.py \
  tests/test_personal_integration.py -q
```
