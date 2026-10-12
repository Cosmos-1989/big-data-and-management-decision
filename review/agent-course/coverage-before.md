# 企业 AI Agent 培训内容覆盖审查（更新前）

**结论：**未完整覆盖。第10章为运行环境、授权执行、混合检索和任务评测提供了扎实基础；但 Chatflow、Skills、GraphRAG、多智能体、四个端到端案例、分阶段落地方法和七工具比较尚未形成完整教学闭环。

覆盖口径：以新版 1–10 章 textbook 为准；12、13 讲补充稿是待编写占位，不计作覆盖；14 讲为提纲式补充，不等同完整章节。

等级：充分 6 项、部分 15 项、缺失 13 项；共 34 项。

## 基础框架

| 主题 | 等级 | 现有证据 | 缺口与有机整合位置 |
|---|---|---|---|
| Chatbot / Copilot / Agent 的边界 | 部分 | docs/textbook/chapters/10_process_mining.tex（333–340 行）；docs/lecture_notes/14_ai_agent.md（4–7 行） | 缺 Copilot 定义、三者在主动性/工具/状态/责任上的同任务对照。 建议：第10章“语言模型、工作流与智能体”之前；第14讲实训开场。 |
| LLM 在 Agent 系统中的职责与限制 | 部分 | docs/textbook/chapters/01_intro.tex（578–581 行）；docs/textbook/chapters/10_process_mining.tex（333–340 行） | 已有生成与候选行动的定位，但缺上下文窗口、非确定性、工具结果核验和任务级失败示例的系统讲解。 建议：第10章智能体基础。 |
| Planning：分解、更新与终止 | 部分 | docs/textbook/chapters/10_process_mining.tex（343–405 行）；website/dist/content/lecture-slides.json（10_process_mining 第29–31页） | 未明确教授计划分解、观察后重规划、计划与执行记录的区别，也无规划练习。 建议：第10章运行环境组成之后。 |
| Memory：会话、检查点与长期记忆 | 部分 | docs/textbook/chapters/10_process_mining.tex（343–389 行）；website/dist/content/lecture-slides.json（10_process_mining 第28、30页） | 缺短期工作状态、长期知识/用户偏好、写入与检索策略、过期/删除/权限的对比及失效案例。 建议：第10章运行环境组成之后。 |
| Tools：结构化调用、权限、幂等与结果验证 | 充分 | docs/textbook/chapters/10_process_mining.tex（367–445 行）；docs/textbook/chapters/03_sql_kpi.tex（542–547 行）；website/dist/content/lecture-slides.json（10_process_mining 第30–32页） | 理论和示例较完整；缺可运行的工具调用沙箱。 建议：第10章实验与网站面板。 |
| Skills：可复用任务能力的定义、版本与验收 | 缺失 | docs/textbook/chapters/10_process_mining.tex（350–363 行） | 全文未把 Skills 作为独立能力单元，也未讲其与工具、提示模板、工作流的边界。 建议：第10章基础组件；第14讲工具生态。 |
| Harness：上下文、状态、预算、恢复与监督 | 充分 | docs/textbook/chapters/10_process_mining.tex（329–445 行）；website/dist/content/lecture-slides.json（10_process_mining 第27–32页） | 概念论证与案例较足；仍需一个可交互的最小 harness 原型。 建议：第10章实验。 |

## RAG 流程

| 主题 | 等级 | 现有证据 | 缺口与有机整合位置 |
|---|---|---|---|
| 文档解析、OCR/表格、元数据保真 | 部分 | docs/textbook/chapters/10_process_mining.tex（470–474 行）；docs/textbook/chapters/04_data_quality.tex（593–600 行） | 说明了保真要求，但无解析步骤、图文表/扫描件对照样例与校验输出。 建议：第4章证据质量；第10章 RAG。 |
| 切分策略与片段定位 | 部分 | docs/textbook/chapters/10_process_mining.tex（473 行）；docs/textbook/chapters/04_data_quality.tex（593 行） | 缺标题/表格/条款边界、重叠、粒度与召回/定位关系的具体反例。 建议：第10章检索增强生成的逐步计算。 |
| 向量嵌入、相似度与混合检索 | 充分 | docs/textbook/chapters/10_process_mining.tex（475–488 行）；website/dist/content/lecture-slides.json（10_process_mining 第35–37页） | 原理与算例充分，缺可调权重或候选库面板。 建议：第10章 RAG 实验。 |
| Rerank：候选重排与证据筛选 | 部分 | docs/textbook/chapters/10_process_mining.tex（485 行） | 无重排输入输出、排序前后案例、成本/权限顺序和评估。 建议：第10章 RAG。 |
| GraphRAG：实体关系检索与文本证据结合 | 缺失 | docs/textbook/chapters/02_enterprise_data_model.tex（871–873 行） | 不存在 GraphRAG 定义、图构建、路径检索与文本证据合成的课程内容；不能把 Ontology 等同 GraphRAG。 建议：第10章 RAG 后的进阶框；第2章对象图回链。 |
| 引用、冲突、有效期与检索评测 | 部分 | docs/textbook/chapters/10_process_mining.tex（490–493 行）；docs/textbook/chapters/04_data_quality.tex（593–600 行） | 冲突处理有实例；缺检索金标准、Recall@k/引用正确率/拒答率等教学测量。 建议：第10章案例评测。 |

## 编排模式

| 主题 | 等级 | 现有证据 | 缺口与有机整合位置 |
|---|---|---|---|
| Chatflow 与 Workflow 的区别 | 缺失 | docs/textbook/chapters/10_process_mining.tex（333–340 行） | 没有会话驱动与任务流程驱动的状态、触发、人工接入和失败恢复对照。 建议：第10章智能体基础；第14讲实训。 |
| 固定工作流与自主 Agent 的边界 | 充分 | docs/textbook/chapters/10_process_mining.tex（333–340 行）；website/dist/content/lecture-slides.json（10_process_mining 第27页） | 概念清楚，但缺同任务实现对照。 建议：第10章基础。 |
| 多智能体分工、调度、共享状态与冲突 | 缺失 | docs/textbook/chapters/10_process_mining.tex（343–345 行） | 缺调度器、角色边界、交接契约、并发/循环控制、冲突仲裁和成本评价。 建议：第10章运行环境后设置进阶小节。 |

## 部署与治理

| 主题 | 等级 | 现有证据 | 缺口与有机整合位置 |
|---|---|---|---|
| 私有部署架构、数据流和容量 | 部分 | docs/textbook/chapters/10_process_mining.tex（447–519 行）；docs/textbook/chapters/09_optimization.tex（340–368 行）；website/dist/content/lecture-slides.json（10_process_mining 第33–34、39页） | 架构与成本已有；缺可复现部署规格、网络边界图、模型/索引更新与容量压测。 建议：第9章容量；第10章部署。 |
| 权限、安全、提示注入、审计和人工批准 | 充分 | docs/textbook/chapters/10_process_mining.tex（367–445 行）；docs/textbook/chapters/02_enterprise_data_model.tex（663–690 行）；docs/textbook/chapters/04_data_quality.tex（581–600 行） | 原则与案例充分；缺统一威胁模型表和网站交互演练。 建议：第10章治理实验。 |
| 完整任务可靠性、成本与经营效果 | 充分 | docs/textbook/chapters/10_process_mining.tex（521–561 行）；docs/textbook/chapters/06_ab_testing.tex（359–387 行）；website/dist/content/lecture-slides.json（10_process_mining 第40–43页） | 理论完整；需把成本、质量和业务指标汇成推广门禁。 建议：第10章落地路线。 |

## 四类案例

| 主题 | 等级 | 现有证据 | 缺口与有机整合位置 |
|---|---|---|---|
| 企业制度问答 | 部分 | docs/textbook/chapters/10_process_mining.tex（490–493 行）；docs/lecture_notes/14_ai_agent.md（18–19 行） | 有制度冲突片段但无完整问答任务、用户角色、金标准答案与引用评价。 建议：第10章 RAG 案例；第14讲案例一。 |
| 办公数字员工 | 缺失 | docs/textbook/chapters/10_process_mining.tex（381–405 行） | 缺邮件/表单/日程等办公任务的边界、审批、重复提交与交付物核查。 建议：第14讲案例二。 |
| 客户分流 | 缺失 | docs/textbook/chapters/07_prediction.tex（31–35、507 行） | 缺意图/紧急度识别、路由规则、人工兜底、服务公平与误分流评价。 建议：第7章预测到行动过渡；第14讲案例三。 |
| 产线异常诊断与处置 | 部分 | docs/textbook/chapters/02_enterprise_data_model.tex（871–873 行）；docs/textbook/chapters/10_process_mining.tex（566–629 行）；website/dist/content/ai_question_to_data_case.json（示例问题） | 有制造 KPI、对象图和行动案例，但无从异常告警到证据检索、原因假设、审批、反馈的完整 Agent 轨迹。 建议：第10章综合案例；第14讲案例四。 |

## 落地路径

| 主题 | 等级 | 现有证据 | 缺口与有机整合位置 |
|---|---|---|---|
| 场景筛选与优先级 | 部分 | docs/textbook/chapters/01_intro.tex（478–485 行）；docs/textbook/chapters/10_process_mining.tex（521–561 行） | 缺价值、可用数据、流程标准化、失败损失、授权难度的统一筛选矩阵。 建议：第10章新“从筛选到扩展”小节。 |
| MVP 与试点验收 | 部分 | docs/textbook/chapters/06_ab_testing.tex（359–376 行）；docs/textbook/chapters/10_process_mining.tex（367–405 行） | 缺可交付的最小原型结构、基线、样本任务集和故障注入验收单。 建议：第10章实验；第14讲项目任务。 |
| 评测、灰度与回滚 | 部分 | docs/textbook/chapters/10_process_mining.tex（529–561 行）；docs/textbook/chapters/06_ab_testing.tex（378–398 行） | 未形成 Agent 特有的离线→影子→小流量→扩展门禁，也无故障回滚演练。 建议：第10章落地路径。 |
| 规模化运维与持续治理 | 部分 | docs/textbook/chapters/10_process_mining.tex（494–519 行）；docs/textbook/chapters/10_process_mining.tex（529–561 行） | 缺模型/工具/知识版本更新、责任分工、监控告警和定期复评的运行清单。 建议：第10章落地路径。 |

## 工具生态

| 主题 | 等级 | 现有证据 | 缺口与有机整合位置 |
|---|---|---|---|
| OpenClaw | 缺失 | 未检出 | 核心讲义、11–14 补充稿、网站幻灯片及实验均未出现 OpenClaw；现有平台比较涉及其他产品，不能替代该工具。 建议：第14讲“工具生态与选型”中性比较页。 |
| Hermes Agent | 缺失 | 未检出 | 核心讲义、11–14 补充稿、网站幻灯片及实验均未出现 Hermes Agent；现有平台比较涉及其他产品，不能替代该工具。 建议：第14讲“工具生态与选型”中性比较页。 |
| Claude Code | 缺失 | 未检出 | 核心讲义、11–14 补充稿、网站幻灯片及实验均未出现 Claude Code；现有平台比较涉及其他产品，不能替代该工具。 建议：第14讲“工具生态与选型”中性比较页。 |
| Codex | 缺失 | 未检出 | 核心讲义、11–14 补充稿、网站幻灯片及实验均未出现 Codex；现有平台比较涉及其他产品，不能替代该工具。 建议：第14讲“工具生态与选型”中性比较页。 |
| Trae | 缺失 | 未检出 | 核心讲义、11–14 补充稿、网站幻灯片及实验均未出现 Trae；现有平台比较涉及其他产品，不能替代该工具。 建议：第14讲“工具生态与选型”中性比较页。 |
| Dify | 缺失 | 未检出 | 核心讲义、11–14 补充稿、网站幻灯片及实验均未出现 Dify；现有平台比较涉及其他产品，不能替代该工具。 建议：第14讲“工具生态与选型”中性比较页。 |
| Coze | 缺失 | 未检出 | 核心讲义、11–14 补充稿、网站幻灯片及实验均未出现 Coze；现有平台比较涉及其他产品，不能替代该工具。 建议：第14讲“工具生态与选型”中性比较页。 |

## 整合顺序

1. **第1、2、3、4、6、7、9章的既有桥接段落：**各增加最少必要的 Agent 语境：决策任务、语义/权限、受限问数、文档质量、试点评价、客户路由的预测与行动区别、容量成本。避免重写原有统计和管理主线。
2. **第10章“智能体及其运行环境”：**在现有工作流/Agent与 harness 之间补三者边界、Planning/Memory/Skills 和 Chatflow/Workflow；以单 Agent 基线引出多智能体调度与交接。
3. **第10章“本地部署与检索增强生成”：**在现有向量/RRF推导前后加解析、结构化切分、权限过滤、重排、GraphRAG 和检索评测，保留原有公式及 E7 冲突材料案例。
4. **第10章“智能体的可靠性与经济评价”及综合案例：**加入筛选→最小原型→离线评测→影子运行→受控试点→灰度扩展→复评/回滚的门禁，并把四案例贯穿对应步骤。
5. **第14讲补充页与网站实验区：**把现有提纲升级为可选实践单元：四个完整案例、七工具中性对照、无需外部账号的本地模拟 Agent/RAG 面板；每个案例定义背景、输入、权限、预期输出、异常与评分。

## 判定说明

- **充分：**现有核心讲义有系统定义/机制、具体算例或案例，且网页幻灯片可独立讲授；若缺实验，在 gap 中另列。
- **部分：**已有相关概念或案例，但缺关键环节、完整讲授或实践。
- **缺失：**未见该主题的实质性课程内容；相邻概念不推定等价。

- 网站主课目前只有第1–10章 HTML 幻灯片；第11–14讲位于 extras，均无对应 lecture-slides deck。
- 第12、13讲 MD 与网页正文仍写“待编写”，不能计算为已有覆盖。
- 实验面板中有流程挖掘、SQL 审计、对象/行动数据类演示，却没有 Agent 的工具循环或 RAG 检索评测任务。
- 七工具只是用户要求覆盖的生态条目；本报告仅判现有课程是否涉及，不对截至审查日的产品能力、价格、排名作未经官网核验的断言。
