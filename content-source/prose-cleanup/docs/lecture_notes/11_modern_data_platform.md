# 第 11 章 现代数据平台与语义层

## 1. 学习目标

1. 区分数据库、数据仓库、数据湖和 lakehouse 的管理含义；
2. 解释 bronze/silver/gold 分层如何支撑可复现分析；
3. 理解语义层在 KPI 统一口径、AI 问数和权限治理中的作用；
4. 将半导体制造 KPI 映射为可治理的数据产品；
5. 说明 SiFactory-like 制造决策系统需要哪些数据对象、指标层和审计机制。

## 2. 管理问题导入

当管理者问“为什么某条线 OEE 下降、WIP 上升、OTD 变差”时，系统不能只返回一张临时 SQL 表。它需要知道设备、批次、工站、订单、质量事件、维护事件和指标口径之间的关系。现代数据平台的任务，是把这些数据组织为可查询、可治理、可审计的事实基础。

## 3. 理论基础

- 数据仓库：面向主题、集成、稳定、可分析；
- 数据湖：保留多源异构数据和原始明细；
- lakehouse：在开放存储上结合湖的灵活性与仓库的治理能力；
- 语义层：将表字段、指标公式、业务对象和权限规则统一表达；
- 数据产品：有 owner、SLA、质量规则和消费接口的数据资产。

## 4. 数据与技术方法

制造数据从原始事件到指标服务的处理链为：

```text
raw events -> bronze tables -> silver conformed objects
-> gold KPI marts -> semantic layer -> dashboard / AI question-to-data
```

半导体制造场景的 gold 层至少包含：

- lot KPI mart；
- equipment KPI mart；
- work-center daily KPI mart；
- order delivery KPI mart；
- M13 element mapping table。

## 5. 案例分析

样本 `data/sample/semiconductor_kpi_daily.csv` 的分析包括：

1. 如何从日运营快照构造 Yield、OEE、Cycle Time、WIP、OTD；
2. 为什么 KPI 层必须保留分子和分母；
3. 为什么 AI 问数必须先经过语义层，而不能直接让模型猜表结构；
4. 如何把 M13 要素作为诊断导航，而不是零散指标列表。

## 6. 实验任务

1. 设计 bronze/silver/gold 三层表；
2. 为 Yield 或 OEE 编写语义层指标定义；
3. 写出 AI 问数可访问和不可访问的数据范围；
4. 设计一条审计日志记录，包含用户问题、候选 SQL、最终 SQL、结果摘要和人工校验。

## 7. 结果解释与管理含义

现代数据平台为指标计算、模型服务、AI 回答和行动建议提供共同的事实基础。缺少语义定义与审计记录时，临时查询的口径和解释难以复核，AI 问数结果可能增加管理风险。

## 8. 常见错误

1. 把数据湖仓理解为存储系统升级，而不是治理机制升级；
2. 只建设宽表，不定义指标 owner 和质量规则；
3. 让 AI 直接查询底层表，绕过语义层；
4. 不保留分子、分母和时间窗口，导致 KPI 无法复核；
5. 只看 dashboard，不保留行动和反馈日志。

## 9. 课后作业

围绕半导体制造 KPI 设计一个最小语义层，至少包含 3 个业务对象、5 个指标和 3 条权限或审计规则。

## 10. 延伸阅读

- DAMA-DMBOK 数据治理相关章节；
- dbt Semantic Layer 官方文档；
- NIST AI Risk Management Framework；
- Lakehouse 与现代数据平台相关白皮书。

