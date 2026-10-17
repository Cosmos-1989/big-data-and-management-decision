# 第 11 章 现代数据平台与语义层

## 1. 学习目标

1. 区分数据库、数据仓库、数据湖和湖仓一体（lakehouse）的用途；
2. 解释 bronze/silver/gold 分层[^medallion]如何支持可复现分析；
3. 理解语义层在 KPI 统一口径、AI 问数和权限治理中的作用；
4. 将半导体制造关键绩效指标（KPI）组织为具有明确责任和使用规则的数据产品；
5. 说明制造决策系统原型（SiFactory-like）所需的数据对象、指标层和审计机制。

## 2. 管理问题导入

当管理者问“为什么某条产线的 OEE 下降、WIP 上升、OTD 下降”[^manufacturing-kpi]时，仅返回临时查询结果不足以解释这些变化。分析还需要关联设备、批次、工站、订单、质量事件和维护事件，并确认各项指标的计算口径。现代数据平台的任务，是把这些数据组织为可查询、可治理、可审计的事实基础。

## 3. 理论基础

- 数据仓库：围绕业务主题整合多源数据，保存支持历史分析的统一记录；
- 数据湖：集中保存不同来源和格式的数据，包括供后续处理的原始明细；
- 湖仓一体：在数据湖存储基础上提供表管理、事务与分析能力，结合多格式数据存储和仓库式管理；
- 语义层：将表字段、指标公式、业务对象和权限规则统一表达；
- 数据产品：具有明确责任人、服务水平协议（SLA）[^sla]、质量规则和访问接口的数据资产。

## 4. 数据与技术方法

制造数据从原始事件到指标服务的处理链为：

```text
raw events -> bronze tables -> silver conformed objects
-> gold KPI marts -> semantic layer -> dashboard / AI question-to-data
```

在本案例设计中，gold 层以面向特定分析任务的数据集市[^mart]组织制造指标：

- 批次 KPI 数据集市（lot KPI mart）；
- 设备 KPI 数据集市（equipment KPI mart）；
- 工作中心日 KPI 数据集市（work-center daily KPI mart）；
- 订单交付 KPI 数据集市（order delivery KPI mart）；
- 运营要素映射表（M13 element mapping table）。

## 5. 案例分析

样本 `data/sample/semiconductor_kpi_daily.csv` 的分析包括：

1. 如何从日运营快照构造 Yield、OEE、Cycle Time、WIP、OTD；
2. 为什么 KPI 层必须保留分子和分母；
3. 为什么 AI 问数必须先经过语义层，而不能直接让模型猜表结构；
4. 如何依据 M13 运营要素分类组织诊断，将指标变化关联到待核查的业务环节。

## 6. 实验任务

1. 设计 bronze/silver/gold 三层表；
2. 为 Yield 或 OEE 编写语义层指标定义；
3. 写出 AI 问数可访问和不可访问的数据范围；
4. 设计一条审计日志记录，包含用户问题、候选 SQL、最终 SQL、结果摘要和人工校验。

## 7. 结果解释与管理含义

现代数据平台为指标计算、模型服务、AI 回答和行动建议提供共同的事实基础。缺少语义定义与审计记录时，临时查询的口径和解释难以复核，AI 问数结果可能增加管理风险。

## 8. 常见错误

1. 仅更换存储系统，未同步建立质量、权限、版本和责任规则；
2. 只建设宽表，不明确指标责任人和质量规则；
3. 让 AI 直接查询底层表，绕过语义层；
4. 不保留分子、分母和时间窗口，导致 KPI 无法复核；
5. 只查看运营看板，不保留行动与结果反馈日志。

## 9. 课后作业

围绕半导体制造 KPI 设计一个最小语义层，至少包含 3 个业务对象、5 个指标和 3 条权限或审计规则。

## 10. 延伸阅读

- DAMA-DMBOK 数据治理相关章节；
- dbt Semantic Layer 官方文档；
- NIST AI Risk Management Framework；
- Lakehouse 与现代数据平台相关白皮书。

[^medallion]: bronze、silver、gold 是常见的数据分层命名：bronze 保留原始数据，silver 对数据进行清洗和标准化，gold 组织供业务分析使用的结果。分层名称本身不保证质量；各层仍须有可检验的处理与发布规则。参见 [Microsoft 分层架构文档](https://learn.microsoft.com/en-us/fabric/onelake/onelake-medallion-lakehouse-architecture)。

[^manufacturing-kpi]: OEE（Overall Equipment Effectiveness）为设备综合效率，WIP（Work in Process）为在制品存量，OTD（On-time Delivery）为准时交付率。下文的 Yield 为良率，Cycle Time 为生产周期。各指标的对象、时间与分子分母必须分别定义；计算基础见第 3 章。

[^sla]: 服务水平协议（Service Level Agreement）规定供给方与使用方的责任、服务质量及响应要求。在数据服务中，可约定刷新频率、可用性、质量门槛和故障处置期限。参见 [NIST 术语定义](https://csrc.nist.gov/glossary/term/service_level_agreement)。

[^mart]: 数据集市（data mart）面向特定业务领域或分析任务组织数据，例如设备效率或订单交付分析。数据集市须明确覆盖范围、基础事实及指标口径，支持汇总结果的追溯。
