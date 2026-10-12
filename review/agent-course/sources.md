# 企业 AI Agent 教学扩展：官方资料核查

核查日期：2026-10-12。已查阅官方文档、官方工程文章、规范及原始论文；本文件不构成平台实测排名。

## 证据规则

产品能力部分列可核验事实；“教学选型”均为基于事实的课程设计判断。云产品、开源部署、不同区域和不同版本分别识别。模型、Harness、工具、业务权限及人工决策责任分别讨论。

OpenAI 部分先读本地安装 README，再查官方网页。本地 `codex --help` 因包内二进制缺失报 ENOENT，未操作安装。官方当前文档将部分 developers.openai.com/codex 链接重定向至 learn.chatgpt.com。

## 七个平台

### OpenClaw｜消息入口与自部署Agent运行时

可核验事实：

- 自部署Gateway统一渠道连接、会话及路由；可从聊天渠道或控制界面与Agent交互。 [OC1：OpenClaw Docs](https://docs.openclaw.ai/)
- 工具执行可以进入沙箱；Gateway仍运行在宿主机。沙箱默认关闭，工具拒绝策略仍独立生效。 [OC3：OpenClaw Sandboxing](https://docs.openclaw.ai/gateway/sandboxing)
- 官方信任模型是每Gateway一个可信操作者或相互信任团队；相互敌对用户应拆分Gateway/凭证/主机边界。 [OC2：OpenClaw Security](https://docs.openclaw.ai/gateway/security)
- 消息工具可能跨渠道发送，工具策略与接入身份策略分别约束相关动作。 [OC4：OpenClaw Tool and Agent Permissions](https://docs.openclaw.ai/gateway/security/tool-permissions)

教学选型（推论）：

- 用于讲解“消息→任务→工具执行→结果”的持续服务链；课堂先用脱敏事件和只读工具。
- 若任务需要固定可审计节点路径，可在运行时之外显式设计Workflow；不把聊天入口视为既有业务流程。

边界：

- 自部署Gateway不意味着模型推理或插件也都在内网；需单独审查提供商和工具数据流。
- 不能称为企业敌对多租户隔离平台；不把能调用工具视为已经授予业务操作权限。

### Hermes Agent｜通用Agent运行时与跨会话记忆

可核验事实：

- 官方文档提供CLI/桌面与消息网关，持续记忆、技能复用、子代理以及本地/容器/SSH等执行后端。 [HE1：Hermes Agent Documentation](https://hermes-agent.nousresearch.com/docs)
- 安全控制分别处理发送者授权、危险命令审批、文件写入和容器隔离。 [HE2：Hermes Security](https://hermes-agent.nousresearch.com/docs/user-guide/security)
- Skills可被保存和复用，第三方安装有扫描机制。 [HE3：Hermes Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)

教学选型（推论）：

- 适合比较程序化记忆、任务经历形成的操作知识与知识库证据，观察跨会话任务是否可恢复。
- 课堂比较应固定任务、工具、模型、预算与测试集，评价完成率和可追踪性。

边界：

- “自我改进”是文档中的设计定位，不是已证明所有任务性能单调提升。
- 本地运行与容器运行的权限差异需按后端配置核验；本次未安装或实测。

### Claude Code｜代码与文件任务的工程Agent

可核验事实：

- 读取代码库、编辑文件、执行命令，提供终端/IDE/桌面/Web等入口。 [CC1：Claude Code Overview](https://code.claude.com/docs/en/overview)
- 权限由Claude Code运行时规则执行；prompt或CLAUDE.md不会直接变更允许的系统访问。 [CC2：Claude Code Configure Permissions](https://code.claude.com/docs/en/permissions)
- 内置shell沙箱限制命令的文件和网络访问；其文件工具、MCP服务器和hooks不在这个shell沙箱中。 [CC3：Claude Code Sandboxed Bash Tool](https://code.claude.com/docs/en/sandboxing)

教学选型（推论）：

- 用于把分析脚本、测试、代码差异与文档产物置于一个可审查的工程任务中。
- 用仓库约定或Skills表达方法规范，用运行时规则及环境隔离落实执行权限。

边界：

- 不能把模型行为提示写成强制访问控制。
- 仅shell沙箱不等于全进程、MCP及外部系统的统一隔离；平台和云会话边界各有文档。

### Codex｜开放Harness及工程Agent入口

可核验事实：

- Codex提供CLI、桌面及IDE等入口，底层的开放Harness也可用于应用集成。 [CX2：Codex as a Platform: Open Agent Harness](https://developers.openai.com/blog/codex-as-a-platform)
- sandbox_mode决定技术边界，approval_policy决定越界时如何审批；自动审批不改变沙箱边界。 [CX1：Codex Sandbox](https://learn.chatgpt.com/docs/sandboxing)
- 官方开放Harness管理会话状态、工具使用、执行与审批，可经CLI、SDK、app-server集成。 [CX2：Codex as a Platform: Open Agent Harness](https://developers.openai.com/blog/codex-as-a-platform)
- Skills使用SKILL.md和可选脚本/资料，先读取描述，选用时载入完整指令。 [CX3：Build Skills](https://learn.chatgpt.com/docs/build-skills)

教学选型（推论）：

- 适合讲授“模型决策—Harness控制—隔离执行—测试验收”的分层，并产出可审查文件。
- 在任务契约、目录范围与验收规则明确的场景比较自动化收益。

边界：

- 开放Harness不表示模型权重或托管服务也开源。
- 本地执行不意味着无需模型服务；计划、账号和功能访问不做跨用户保证。
- 本地CLI帮助因二进制缺失无法执行；本次事实来自已读README和官方网页，不是运行测试。

### TRAE｜IDE工程Agent与通用工作助手产品族

可核验事实：

- 2026-06-09官方产品说明将独立SOLO产品称为TRAE Work，覆盖Desktop/Web/Mobile；TRAE IDE仍有IDE Mode与SOLO Mode。 [TR1：Introducing TRAE Work](https://www.trae.ai/blog/trae_work_0609)
- 2026-01-08工程文章说明文件系统沙箱、shell拦截以及手动/自动执行配置。 [TR2：Making AI Coding Safer](https://www.trae.ai/blog/engineering_thought_0108)

教学选型（推论）：

- 代码任务可比较TRAE IDE的编辑器、终端和代码审查组织方式；文档/数据任务应明确当前产品是TRAE Work。
- 按任务完成证据、权限设置与数据流评价，保留试验环境和版本记录。

边界：

- 工程文章所述平台范围是发布日期快照，不能据此宣布当前所有OS具备同等沙箱或网络隔离。
- 未核验私有化部署能力；不把下载桌面客户端等同模型完全本地推理。
- 不引用营销中的无人干预、最高效率或模型排名作为教材结论。

### Dify｜可视化AI应用与知识库编排平台

可核验事实：

- Workflow用于单次或批处理任务，可经用户/API或Trigger触发；Chatflow每轮对话触发，提供会话变量、LLM记忆及流式输出。 [DI1：Dify Key Concepts](https://docs.dify.ai/en/learn/key-concepts)
- 官方提供Docker Compose自部署指南。 [DI2：Deploy Dify with Docker Compose](https://docs.dify.ai/en/self-host/deploy/quick-start/docker-compose)
- 云版工作区具有Owner、Admin、Editor、Normal角色，知识库可见/使用权限在其自身设置管理。 [DI3：Dify Manage Members](https://docs.dify.ai/en/cloud/use-dify/workspace/team-members-management)
- 知识库支持一般/父子块及向量、全文、混合检索，候选可再由Rerank模型排序。 [DI4：Dify Configure Chunk Settings](https://docs.dify.ai/en/cloud/use-dify/knowledge/create-knowledge/chunking-and-cleaning-text)；[DI5：Dify Index Method and Retrieval Settings](https://docs.dify.ai/en/cloud/use-dify/knowledge/create-knowledge/setting-indexing-methods)

教学选型（推论）：

- 固定输入输出、校验、分支、报告等单次业务用Workflow；需要澄清需求并保存对话状态时用Chatflow。
- 用可视化节点显式表现检索、校验、审批、外部API和错误分支；可对比固定流程与Agent节点的动态选择。

边界：

- 云版资源权限不能直接套在所有开源自部署版本；编排角色与后端ERP/数据库API权限是不同层。
- 自部署Dify不意味着接入的模型、插件与Rerank服务不会处理出网数据。
- 无普遍最优块长、TopK、阈值；需任务级检索测试。

### Coze｜智能体与低代码应用编排平台

可核验事实：

- 中国官方文档以可视化节点实现Workflow与Chatflow：前者功能请求，后者多轮对话请求。 [CZ1：Coze 低代码工作流介绍](https://docs.coze.cn/guides_workflow)
- API执行Chatflow要求已发布的对话流、令牌run权限，相关会话创建者需一致。 [CZ2：Coze 执行对话流](https://docs.coze.cn/developer_guides_workflow_chat)
- Coze Studio官方开源仓库提供Docker部署；与云端Coze平台应分开识别。 [CZ3：Coze Studio Official Repository](https://github.com/coze-dev/coze-studio)

教学选型（推论）：

- 课堂可从接待澄清的Chatflow开始，再把固定报告、查询或审批处理组织为Workflow。
- 分别展示编辑/发布权限、API调用身份和后端业务权限，避免把流程可见等同于可执行所有动作。

边界：

- 本次云资料来自coze.cn；不推论国际站、Studio及所有商业版本能力或费用一致。
- 开源Studio自部署需要自行管理运行、网络与鉴权；部署成功不等于获得业务操作授权。

## 技术基础与课堂表达

### RAG：证据获取与回答生成

- 原始RAG将检索到的文档视为潜在变量，用检索分布与条件生成分布构造输出；RAG-Sequence对同一文档条件下的整段输出进行top-k近似边缘化。 [RA1：Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/html/2005.11401v4)

$$p(y\mid x)\approx\sum_{z\in\mathcal Z_k(x)}p_\eta(z\mid x)p_\theta(y\mid x,z)$$

RAG-Sequence原论文的top-k近似；不是所有RAG系统的必需计算步骤。 [RA1：Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/html/2005.11401v4)

教学设计（推论）：

- 教材须区分原论文的联合训练模型与现代应用中“检索证据后加入上下文”的RAG实现。
- 案例应先定义可回答范围、来源与版本，再检查候选证据、引用位置及拒答条件。

边界：

- 检索增强不保证证据真实、覆盖完整或生成无误。
- 检索器概率、向量相似度、Rerank分数不可无条件互换；流程是否更新模型参数取决于具体实现。

### 文档解析：保持可溯源的结构

- 解析工具按格式输出结构元素；PDF/图像可以配置OCR或布局处理，表格与文本具有不同结构表示。 [RA3：Unstructured Partitioning](https://docs.unstructured.io/open-source/core-functionality/partitioning)

教学设计（推论）：

- 把段落、标题、表格、文档版本、页码与来源ID一起保存；对扫描件和复杂表格用样本核查解析结果。

边界：

- 能输出文本不证明版面顺序、公式、单位或表格结构已准确恢复；OCR结果须作为解析产物而非原文。

### 切分：匹配精度与上下文完整性

- Unstructured可按标题保留节边界，并对表格单独处理；原元素元数据有助恢复来源。 [RA4：Unstructured Chunking](https://docs.unstructured.io/open-source/core-functionality/chunking)
- Dify父子模式以较小子块匹配，返回较大父块提供上下文；一般模式直接返回匹配块。 [DI4：Dify Configure Chunk Settings](https://docs.dify.ai/en/cloud/use-dify/knowledge/create-knowledge/chunking-and-cleaning-text)

教学设计（推论）：

- 以合同条款、SOP步骤、完整表格或定义条件为切分单位；比较短块、重叠、父子块对证据召回的影响。

边界：

- 重叠可保留局部连续性，也会引入重复；固定长度不是唯一策略。
- 不要混淆字符数与token数；产品的上限与默认值应随实验环境记录。

### 向量检索与混合检索

- DPR通过双编码器表示问题与段落，再从密集表示中选择相关候选；原RAG使用内积检索。 [RA2：Dense Passage Retrieval for Open-Domain Question Answering](https://arxiv.org/abs/2004.04906)；[RA1：Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/html/2005.11401v4)
- Dify支持语义向量、全文和混合检索。 [DI5：Dify Index Method and Retrieval Settings](https://docs.dify.ai/en/cloud/use-dify/knowledge/create-knowledge/setting-indexing-methods)

教学设计（推论）：

- 语义近似问题可用向量检索；物料号、订单号、精确术语需比较关键词/过滤或混合检索；结构化数值查询可交给受限SQL工具。

边界：

- 向量相近只表示该表示与度量下的候选关系，不能当作事实蕴含或业务权限证明。
- 更换编码模型可能影响索引兼容；实验需保持编码、过滤和语料版本一致。

### Rerank：候选集内部的二次排序

- 官方Rerank接口接受query及候选文档，并按与查询的语义相关性重排。 [RA5：Cohere Rerank Overview](https://docs.cohere.com/docs/rerank-overview)
- Dify检索设置允许对向量、全文或混合召回结果调用Rerank。 [DI5：Dify Index Method and Retrieval Settings](https://docs.dify.ai/en/cloud/use-dify/knowledge/create-knowledge/setting-indexing-methods)

教学设计（推论）：

- 先评估首阶段是否召回正确证据，再评估重排是否把它移到有限上下文预算内；同时记录延迟和成本。

边界：

- 重排不能挽回未进入候选集的证据；分数不是校准后的答案正确概率。

### GraphRAG：关系与全局主题摘要

- 原论文从文档抽取实体图并预生成社区摘要，再为全局主题类问题组合回答。 [GR1：From Local to Global: A Graph RAG Approach to Query-Focused Summarization](https://arxiv.org/abs/2404.16130v2)
- 官方项目包含TextUnits、实体/关系/声明、社区层次；Global与Local等查询各用不同证据结构。 [GR2：Microsoft GraphRAG Documentation](https://microsoft.github.io/graphrag/)

教学设计（推论）：

- 当任务需要跨文档实体关系、主题汇总或关联链时，将图索引与向量基线进行同题比较。
- 将每条关系与社区摘要链接回来源，区分提取事实、综合摘要与推断。

边界：

- 并非所有RAG都必须图化，简单局部事实查询可能更适合基线检索。
- 抽取关系和摘要仍可能出错，建图与维护也增加成本；论文结果不能外推所有企业任务。

### Harness：模型外围的运行与控制系统

- 官方将Harness描述为Agent循环外围的执行系统，管理状态、工具、进展、失败处理及审批。 [CX2：Codex as a Platform: Open Agent Harness](https://developers.openai.com/blog/codex-as-a-platform)
- 长任务案例通过初始环境、进度工件、版本记录、逐项推进及端到端测试衔接多个上下文。 [HA2：Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

教学设计（推论）：

- 企业任务可明确状态机、工具契约、预算、终止条件、恢复点、审批与验收记录；把“答案”与“已验证完成的动作”分别记录。

边界：

- Harness不是单一模型名称，也不是一个提示词文件；长期任务工件不能自动证明任务正确。
- 原始长任务案例不证明多Agent必然优于单Agent。

### Skills：可复用操作知识的按需加载

- 官方规范以SKILL.md的YAML元数据和Markdown说明组织Skill，可配脚本、参考资料和资源。 [SK1：Agent Skills Specification](https://agentskills.io/specification)
- 按需加载先暴露描述，再在选择后加载操作指令；allowed-tools为实验字段，不同宿主支持不同。 [SK1：Agent Skills Specification](https://agentskills.io/specification)；[CX3：Build Skills](https://learn.chatgpt.com/docs/build-skills)

教学设计（推论）：

- 用Skill封装指标口径检查、报表生成、实验复核等稳定方法，并明确输入、步骤、产物和适用条件。

边界：

- Skill是操作知识与资源包，不等于RAG证据库；也不意味着执行内容天然可信。
- Skill的工具列表或自然语言约束不替代宿主、沙箱、身份及后端授权。

### 多智能体：分工契约与控制权

- Workflow遵循预定义路径；Agent由模型动态安排步骤和工具，适用复杂度应随任务需求增加。 [HA1：Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- manager-as-tools让管理者保留最终答复，handoff将下一分支控制权交给专家Agent。 [MA1：Orchestration and Handoffs](https://developers.openai.com/api/docs/guides/agents/orchestration)

教学设计（推论）：

- 当子任务存在独立工具、专业指令、输出契约或并行价值时再分工；为归并、冲突与独立复核指定责任。

边界：

- 多个Agent使用相同错误证据时可能相关地出错；交叉复核不自动等于独立证据。
- 增加Agent数会增加协调、状态和权限表面；未核验任何通用性能排名。

### MCP：工具与上下文连接契约

- 官方架构由Host管理Clients及连接生命周期，Servers暴露资源、工具、提示；各连接按能力协商。 [MC1：MCP Architecture (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25/architecture)

教学设计（推论）：

- 将企业查询和有限动作包装为输入输出明确的工具，分别标注身份、读写范围和可审计的结果。

边界：

- 能力协商说明双方支持哪些协议特性，不等于完成企业业务授权；具体ACL与副作用政策仍由宿主和服务落实。

## 可用于教材的选型问句

1. 任务能否明确列出输入、输出、校验与异常分支？可以时先比较固定 Workflow。
2. 是否需要逐轮澄清并保存会话状态？需要时比较 Chatflow；不能据此自动推论需要开放式 Agent。
3. 是否需要模型动态选择路径、工具或子任务？在固定流程不足时比较 Agent，并定义终止与验收条件。
4. 主要产物是代码、文档还是企业系统动作？工程任务、应用编排和持续消息服务的评价对象应分开。
5. 执行在哪里，数据会经过哪些模型或插件，谁拥有工具身份？自部署服务不自动等于完全本地推理。
6. 成功如何验证？保持固定测试任务、证据集、权限和预算，分别记录准确性、完成率、引用、延迟与代价。

上述问句是课程设计建议，不是任何厂商宣称的产品排名。

## 来源索引

- **OC1** [OpenClaw Docs](https://docs.openclaw.ai/) — OpenClaw 官方文档。
- **OC2** [OpenClaw Security](https://docs.openclaw.ai/gateway/security) — OpenClaw 官方文档。
- **OC3** [OpenClaw Sandboxing](https://docs.openclaw.ai/gateway/sandboxing) — OpenClaw 官方文档。
- **OC4** [OpenClaw Tool and Agent Permissions](https://docs.openclaw.ai/gateway/security/tool-permissions) — OpenClaw 官方文档。
- **HE1** [Hermes Agent Documentation](https://hermes-agent.nousresearch.com/docs) — Nous Research 官方文档。
- **HE2** [Hermes Security](https://hermes-agent.nousresearch.com/docs/user-guide/security) — Nous Research 官方文档。
- **HE3** [Hermes Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) — Nous Research 官方文档。
- **CC1** [Claude Code Overview](https://code.claude.com/docs/en/overview) — Anthropic 官方文档。
- **CC2** [Claude Code Configure Permissions](https://code.claude.com/docs/en/permissions) — Anthropic 官方文档。
- **CC3** [Claude Code Sandboxed Bash Tool](https://code.claude.com/docs/en/sandboxing) — Anthropic 官方文档。
- **CX1** [Codex Sandbox](https://learn.chatgpt.com/docs/sandboxing) — OpenAI 官方文档。
- **CX2** [Codex as a Platform: Open Agent Harness](https://developers.openai.com/blog/codex-as-a-platform) — OpenAI 官方工程文章。
- **CX3** [Build Skills](https://learn.chatgpt.com/docs/build-skills) — OpenAI 官方文档。
- **TR1** [Introducing TRAE Work](https://www.trae.ai/blog/trae_work_0609) — TRAE 官方产品文章。
  适用范围：产品定位资料，不提供能力效果或价格比较依据。
- **TR2** [Making AI Coding Safer](https://www.trae.ai/blog/engineering_thought_0108) — TRAE 官方工程文章。
  适用范围：2026-01-08 发布时的实施快照；不能证明2026-10所有平台的相同支持状态。
- **DI1** [Dify Key Concepts](https://docs.dify.ai/en/learn/key-concepts) — Dify 官方文档。
- **DI2** [Deploy Dify with Docker Compose](https://docs.dify.ai/en/self-host/deploy/quick-start/docker-compose) — Dify 官方文档。
- **DI3** [Dify Manage Members](https://docs.dify.ai/en/cloud/use-dify/workspace/team-members-management) — Dify 官方文档。
  适用范围：该页面属于Cloud产品，不能直接当作每个自部署版本的权限矩阵。
- **DI4** [Dify Configure Chunk Settings](https://docs.dify.ai/en/cloud/use-dify/knowledge/create-knowledge/chunking-and-cleaning-text) — Dify 官方文档。
- **DI5** [Dify Index Method and Retrieval Settings](https://docs.dify.ai/en/cloud/use-dify/knowledge/create-knowledge/setting-indexing-methods) — Dify 官方文档。
  适用范围：页面中的默认值与收费随版本变化，本教材不固定这些数值。
- **CZ1** [Coze 低代码工作流介绍](https://docs.coze.cn/guides_workflow) — Coze 中国官方文档。
- **CZ2** [Coze 执行对话流](https://docs.coze.cn/developer_guides_workflow_chat) — Coze 中国官方API文档。
- **CZ3** [Coze Studio Official Repository](https://github.com/coze-dev/coze-studio) — Coze 官方开源仓库。
  适用范围：开源版本不等于coze.cn/国际版商业服务；不保证能力、许可、鉴权一致。
- **RA1** [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/html/2005.11401v4) — Lewis et al. 原始论文。
  适用范围：原论文含训练方案；常见企业检索后提示生成的系统不必采用其联合微调。
- **RA2** [Dense Passage Retrieval for Open-Domain Question Answering](https://arxiv.org/abs/2004.04906) — Karpukhin et al. 原始论文。
  适用范围：原论文测试集成绩不能推论当前企业私有语料收益。
- **RA3** [Unstructured Partitioning](https://docs.unstructured.io/open-source/core-functionality/partitioning) — Unstructured 官方文档。
- **RA4** [Unstructured Chunking](https://docs.unstructured.io/open-source/core-functionality/chunking) — Unstructured 官方文档。
- **RA5** [Cohere Rerank Overview](https://docs.cohere.com/docs/rerank-overview) — Cohere 官方文档。
  适用范围：不以产品营销词或特定模型性能作为本课程比较结论。
- **GR1** [From Local to Global: A Graph RAG Approach to Query-Focused Summarization](https://arxiv.org/abs/2404.16130v2) — Edge et al. 原始论文。
  适用范围：论文结果限于所研究任务与数据，不能推论所有检索问题均优于向量RAG。
- **GR2** [Microsoft GraphRAG Documentation](https://microsoft.github.io/graphrag/) — Microsoft 官方项目文档。
- **HA1** [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — Anthropic 官方工程文章。
  适用范围：2024-12原文的架构原则仍可教学；不把其旧工具列表当最新产品目录。
- **HA2** [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — Anthropic 官方工程文章。
  适用范围：案例主要是Web开发；不是多Agent普遍占优的证明。
- **SK1** [Agent Skills Specification](https://agentskills.io/specification) — Agent Skills 官方规范。
- **MA1** [Orchestration and Handoffs](https://developers.openai.com/api/docs/guides/agents/orchestration) — OpenAI 官方文档。
- **MC1** [MCP Architecture (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25/architecture) — MCP 官方版本化规范。
