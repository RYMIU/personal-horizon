# Personal Horizon — 用户兴趣画像

本文件是 Personal Horizon 所有 profile 的评分与筛选依据。
核心判断标准始终是：

> 这件事是否值得用户今天花几分钟注意？

如果答案是否定的，即使内容很热门，也应该被过滤掉。

---

## 一、中国（china-news / china-tech / china-economy）

关注：

- 中国重大政治/政策、国务院及重要部委政策
- 中国宏观经济、就业、房地产重大变化、金融政策
- 科技产业政策、AI 产业、半导体、大模型、中国互联网公司
- 高校与科研政策、国家自然科学基金、留学/人才政策

降低优先级：

- 普通明星新闻、娱乐八卦、网红新闻
- 普通体育比赛、无实际意义的热搜、单纯情绪性社会话题

## 二、国际（world-news）

重点：中国、加拿大、美国、英国、欧盟；全球重大地缘政治；
战争与安全重大变化；国际科技政策；AI 监管；科研政策；
移民/留学政策；全球经济重大事件。

只有真正重要的国际事件才进入日报。普通美国国内政治争论不自动进入。
判断标准：这件事是否可能影响全球、中国、加拿大、科研、经济或未来几年的政策环境？

## 三、AI / Technology（ai-tech）

最高关注公司：

- OpenAI、Anthropic、Google DeepMind、Google、Meta AI、Microsoft、NVIDIA、xAI
- DeepSeek、Alibaba/Qwen、ByteDance、Tencent、Baidu、Zhipu、Moonshot、MiniMax
- 其他真正有技术影响力的新模型

技术方向：

- LLM、reasoning、coding agent、autonomous agent、MCP、RAG、model memory
- inference、context engineering、multimodal、AI for Science、AI coding、agentic workflow

过滤：单纯营销软文；没有新技术内容的融资新闻；小模型简单套壳；
无实际价值的“AI 创业公司发布 XX”。

## 四、科研（research-general / research-personal）

### Mathematical Biology（最高优先级）

mathematical biology、epidemic modelling、infectious disease modelling、
opinion dynamics、behavioural epidemiology、social dynamics、tipping points、
bifurcation、dynamical systems、network epidemiology、computational biology

### Statistics / ML

graphical models、Gaussian graphical models、Lasso、statistical learning、
causal inference、network science

### Operations Research / Optimization

MILP、integer programming、combinatorial optimization、routing、scheduling、
LNS、ALNS、branch-and-price、column generation、decomposition、
ML for optimization、learning to optimize

来源重点：Nature、Science、Cell、PNAS、Nature Communications、arXiv、
bioRxiv、medRxiv、SIAM、INFORMS、Operations Research、
Mathematical Biosciences、Journal of Mathematical Biology。

`research-personal` 是最重要的 personal profile：只要与上述方向强相关，
即使不热门也可以高分；niche but highly relevant 的价值远高于热门综合科研新闻。

## 五、学术机会（academic-opportunity）

监控：PhD funding、MSc funding、research assistantship、scholarship、
fellowship、summer school、workshop、conference、travel award、research internship。

重点机构：UBC、UBC Okanagan、NSERC、Mitacs、CIHR、SSHRC、
Government of Canada、CSC、NIH、NSF、Wellcome、Simons Foundation。

方向优先：Mathematical Biology、Computational Biology、Epidemiology、
Applied Mathematics、Statistics、Operations Research、AI for Science。

必须判断：是否可以申请、deadline、eligibility、funding amount、institution、
research area、对国际学生是否开放。能提取到 deadline 必须显示；deadline 近则提高优先级。

## 六、GitHub（github-projects）

每天最多 2–3 个项目。重点方向：AI Agent、Coding Agent、MCP、LLM tooling、
RAG、Memory、Optimization、Operations Research、Scientific Computing、
Data Science、Research automation、Productivity / knowledge management。

评分不能只看 Stars，需考虑：最近增长、技术新颖性、实际可用性、是否开源、
文档质量、活跃程度、与用户兴趣的关系。

避免：README 漂亮但没有实际代码、单纯套 API、bot-generated repo、
复制项目、无维护项目。

## 七、来源可信度（Source Reliability）

- **A** = primary / official / original paper：可直接作为主要事实来源
- **B** = established professional source：正常使用
- **C** = community / secondary / discovery：可发现新闻，重大事实需进一步证据
- **D** = unknown / weak source：无法验证时降低评分或删除
