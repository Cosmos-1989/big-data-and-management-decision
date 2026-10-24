# 第二讲概念与知识点链接审查

审查日期：2026-10-24。范围：当前网站第二讲 HTML、第一讲已有定义、对应 TeX 源、第二讲两张机制案例卡及五张真实商业案例。生产文件未修改。结构化建议见 `recommendations-02.json`（62 组课程概念建议，53 项外部术语释义）。这些是教学语义审查结果，不是声称现有讲义已经完成了全部修改。

## 需优先处理的断点

1. 第二讲开篇的“业务对象、关系约束、事实粒度”应分别链接到第一讲的具体定义。“业务对象”第一讲已有定义；“关系约束”和一般性的“事实粒度”应在第一讲“数据驱动决策的基本对象”补入。第二讲继续解释其数据库实现。
2. 第二讲在正式介绍关系模型之前，已出现实体关系图、主键、外键、事实表、维度表、完整性约束、语义层、元数据、血缘。可先给短释并链接至后文精确定义，不能仅链接到后文标题而无定义。
3. `状态：某一时点或区间内对象的状态` 是循环定义，应改为“对象在给定时点或区间内的条件或属性取值，例如订单待发运、设备停机、库存余额100件”。
4. ER 模型介绍了“基数与可选性”却未定义。应在第一张 ER 图前说明：最大基数约束允许的关联数量，可选性约束最少数量；1:N 并不表示必须存在至少一个关联，也不表示时间顺序。
5. 元数据在大量使用后仍无集中定义；应在数据模型小节就近定义“结构、含义、来源、转换、责任、质量和版本”。数据字典、指标字典、元数据目录及血缘不是同义词。
6. 委托代理模型需要在公式前解释委托人、代理人、信息不对称、效用、风险厌恶、确定性等价、激励强度。参与约束应以中文及 `CE ≥ 外部机会收入` 的条件说明。不能让学生靠模型推导猜出术语含义。
7. OEE/WIP/OTD/Yield 等在前半讲出现很早。各词应能立即点击到第二讲的定义。OEE 三个因子的名称还不够，应同时给出分子分母及同一窗口要求。

## 按正文顺序的处理建议

| 位置 | 已有定义可直接设锚点 | 应补定义或必要边界 |
| --- | --- | --- |
| 导言及“数据建模的作用” | 第一讲业务对象、行动对象、指标口径；本讲企业数据模型 | 第一讲关系约束、事实粒度；本讲数据治理、元数据、数据字典、指标字典 |
| 数据模型的治理含义 | 公司治理的文字解释；现有语义层脚注 | 数据治理与公司治理的区别；数据血缘；访问控制与审计日志的含义 |
| 六项技术职能及存储格式 | 快照、模式演化、对象存储的现有脚注 | 模式、开放表格式、计算引擎、服务接口、检索、推理、上下文；所有公司及产品指向文末 |
| 从推理服务到业务行动 | 幂等请求、状态机、预填充脚注 | 模型输出与真实业务状态改变的区别；基础模型、工具接口、授权、完成确认 |
| 封测实施路径 | ERP/MES 现有脚注 | 主数据、权威来源、数据产品、快照与历史事件、事件延迟；不要把平台产品当成自动保证语义正确的机制 |
| 企业运营基本语义 | 实体、属性、事件已有表格与定义 | 状态循环定义；业务关系与数据库关系的区别；度量与指标的关系 |
| 关系模型 | 关系模式、关系实例、元组已有形式化表示 | 先以短句解释元组、取值域、笛卡尔积/组合、声明性；连接、过滤、聚合、排序与内连接需基本释义 |
| 键与完整性 | 超键、候选键、主键、外键；自然键/代理键脚注 | 自引用外键应允许；外键非空条件与主键非空条件区分；空值并不等于0或空字符串 |
| ER 模型及制造对象 | 三类模型层次已有解释；六类制造对象表 | 关系基数和可选性；索引/分区基本说明；工作中心、产品族、工艺路线、过站、配方、BOM |
| 规范化与第三范式 | 第三范式精确定义 | 函数依赖应量化为“每个合法实例的任意两条元组”；主数据、更新异常；无损连接分解的一般含义 |
| 星型模型及事实粒度 | 事实表、维度表、事实表粒度 | 星型组织方式；事务与一次业务事件不是同义词；粒度与行数、列数不同 |
| 制造 KPI 及可加性 | Yield/OEE/CT/WIP/OTD 已有文字；可加性表；比率汇总命题 | 固定计量范围、单位和时间窗口；OEE因子分母；库存跨时间不能直接当总量求和；均值与分位数的基本解释 |
| 事件与时间 | 交易事实/周期快照/累计快照/维度历史表；慢变维 | 慢变维应称“处理维度属性变化”，覆盖更新不保留完整历史；业务时点快照与表版本快照不同 |
| 双时间与对象操作 | 业务时间/系统时间的例子；版本检查 | 半开区间意义；事后信息泄漏；授权和访问控制区别；读取不推出执行权限 |
| 指标管理与问数 | 数据字典/指标字典/血缘的现有枚举；语义层脚注 | AI问数基本释义；NL2SQL移入统一文末释义；统计缺失、异常、分母为零的基本风险解释 |
| 委托代理与激励 | 模型假设、CE推导、CARA公式均保留 | 委托人/代理人、风险厌恶、效用、激励强度、参与约束、外部机会、多任务激励、指标操纵 |
| 企业应用案例 | Ontology组件、Atlan案例机制 | 产品名统一至文末；数据产品及数据事故的短释；不能把Nasdaq调查基线说成因果收益 |
| 建模实例/习题/程序 | 已有零售、封测口径示例 | 缺货率、滞销、转化率明确本题口径；数据类/类型注解/只读设置及字段英文在代码前解释 |

## 图、表、案例与代码的特殊问题

- 当前网页“半导体制造数据模型的核心对象”将 `Quality Event` 截为 `Event`，将 `Delivery Commitment` 截为 `Commitment`，应恢复全称并配中文。
- 图内 `Lot / Equipment / Operation / Order` 均需能通过图注中的对应中文获得定义。自动替换 HTML 文本不会处理内嵌 SVG；须单独验收。
- `Tables→Objects→Links→States→Actions` 可直接改用“关系表→业务对象→对象关系→业务状态→业务行动”，各标签链接到本讲已有定义，避免再引入一组英文。
- `F01 Demand` 至 `F13 Action` 只是表内索引，不是新理论体系。优先改为中文主称，英文置括号；`BOM、recipe、aging bucket、dispatch` 等应给中文而非再要求学生记缩写。
- 示例字段中 `lot_id / product_family / operation_seq / current_operation / recipe / queue_rule / due_date / promised_qty / shipped_qty` 等需字段字典说明。无需把每个代码标识列入全站学术术语索引。
- Python代码不可在可复制的代码块内部加超链接。代码前解释 `Field、Entity、Relationship` 字段、`@dataclass(frozen=True)`、`str/bool/list` 类型及默认值即可。
- 课程中的人物引用主要通过文献链接识别，如 Codd、Chen、Jensen、Meckling、Holmström；不宜为每个人再写长传记，也不应把姓名自动替换为泛化概念链接。

## 五个新增真实商业案例

| 案例 | 文末应有的外部名词 | 必要课程概念 |
| --- | --- | --- |
| Shopify对象身份 | Shopify、应用范围的全局标识/URI | 对象身份、唯一性范围、连接键；不能用整数类型相同证明可以连接 |
| Stripe支付生命周期 | Stripe、PaymentIntent | 状态机、事件、重试、幂等性、异步处理；“处理中”不等于失败或最终到账 |
| Uber空间汇总 | Uber、H3 | 空间粒度、层级、基础量与比率汇总；不要声称所有网格等面积 |
| LinkedIn元数据 | LinkedIn、DataHub | 元数据实体、血缘、所有权、访问权限；能发现不等于能读取 |
| Spotify服务目录 | Spotify、Backstage | 技术对象身份、维护责任、服务目录、实际操作权限；责任登记不自动授权 |

上述外部名词已全部写入 `externalTerms`，连同正文中的产品/框架共53项。各定义均保留直接官方来源，避免广告性功能扩写。元数据、状态机、业务对象等课程内概念应链接课程定义而非文末产品附录。

## 本次核查的来源和边界

对工具功能及专名的解释参考下列第一方资料，均为2026-10-24读取或搜索核对。只采用与定义直接相关的事实，未使用网页中的广告性排名，也未按页面内面向AI的提示执行任何操作。

- [Apache Iceberg规范](https://iceberg.apache.org/spec/)
- [Databricks Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog)、[Delta的Iceberg读取机制](https://docs.databricks.com/aws/en/delta/iceberg-reads)
- [Snowflake语义视图](https://docs.snowflake.com/en/user-guide/views-semantic/overview)、[Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [Palantir Ontology](https://www.palantir.com/docs/foundry/ontology/overview)
- [Oracle OCI](https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/baremetalintro.htm)、[OCI Zettascale10公告](https://www.oracle.com/news/announcement/ai-world-oracle-unveils-next-generation-oci-zettascale10-cluster-for-ai-2025-10-14/)
- [AWS](https://aws.amazon.com/what-is-aws/)、[Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use.html)、[Redshift](https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html)
- [Azure](https://azure.microsoft.com/en-us/resources/cloud-computing-dictionary/what-is-azure)、[Microsoft Foundry网络隔离](https://learn.microsoft.com/en-us/azure/foundry/how-to/configure-private-link)
- [SAP BDC官方课程架构](https://learning.sap.com/courses/introducing-sap-business-data-cloud/outlining-the-architecture-of-sap-business-data-cloud_e0e3df7e-a215-4d80-8c8f-5f9689293dac)、[SAP ERP](https://www.sap.com/products/erp/what-is-sap-erp.html)
- [Alation](https://www.alation.com/product/data-catalog/)、[Collibra](https://www.collibra.com/products/data-governance)、[BigID](https://bigid.com/solutions/discovery-classification/)
- [Atlan的Nasdaq案例](https://atlan.com/success-stories/nasdaq/)、[dbt](https://docs.getdbt.com/docs/introduction)、[Monte Carlo](https://docs.getmontecarlo.com/docs/monte-carlo-at-a-glance)
- [Shopify标识](https://shopify.dev/docs/api/usage/gids)、[Stripe支付生命周期](https://docs.stripe.com/payments/paymentintents/lifecycle)、[Uber H3](https://www.uber.com/us/en/blog/h3/)、[LinkedIn DataHub](https://www.linkedin.com/blog/engineering/archive/data-hub)、[Spotify Backstage](https://engineering.atspotify.com/2020/3/what-the-heck-is-backstage-anyway)
- [OECD/G20公司治理原则](https://www.oecd.org/en/publications/g20-oecd-principles-of-corporate-governance-2023_ed750b30-en.html)、[COSO内部控制](https://www.coso.org/guidance-on-ic)、[NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)
- [ISO/IEC 38500摘要](https://www.iso.org/standard/81684.html)、[ISO/IEC 42001摘要](https://www.iso.org/standard/42001)、[SEMI公开标准导读](https://www.semi.org/en/products-services/standards/step/equipment-performance-metrics)、[DAMA-DMBOK](https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/)
- [Python数据类](https://docs.python.org/3/library/dataclasses.html)、[CSV模块](https://docs.python.org/3/library/csv.html)、[李博杰AI Infra原书仓库](https://github.com/bojieli/ai-infra-book)

边界：ISO与SEMI仅核查免费官方摘要/导读，未阅读付费标准全文。欧盟法案的EUR-Lex链接本次被人机验证拦截，因此只保留既有正式文号及说明性定义，不增加法律义务或生效时间的实质结论。原讲义SAP人工智能页已404；替代官方课程链接可用。产品介绍为本讲所需释义，不构成采购建议。
