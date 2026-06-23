# Assignment 04: 数据质量与指标治理

## 任务背景

本作业对应第 4 周课程。你需要对 `data/sample/orders_quality_issues.csv` 进行数据剖析和质量校验，并说明质量问题会如何影响第 3 周构造的销售额、毛利率、准时交付率等 KPI。

## 提交内容

1. 一份数据剖析报告：
   - 行数和字段数；
   - 每列缺失数、缺失率和不同值数量；
   - 关键字段的最小值、最大值或取值集合。
2. 一份质量规则结果表，至少包含：
   - `order_id` 非空且唯一；
   - `customer_id` 和 `product_id` 外键能匹配主数据；
   - `quantity` 为正；
   - `channel` 属于 `Direct`、`Partner`、`Online`；
   - `priority` 属于 `High`、`Normal`；
   - `promised_date` 不早于 `order_date`；
   - `actual_date` 不早于 `order_date`，且在本实验中不能为空。
3. 一页业务解释：
   - 每类失败记录会影响哪些 KPI；
   - 哪些失败应设为 error，哪些可以设为 warning；
   - 你建议如何修复或治理这些问题。

## 评分标准

| 项目 | 权重 | 说明 |
|---|---:|---|
| 剖析完整性 | 25% | 能系统展示缺失、唯一性、取值范围和异常模式。 |
| 规则正确性 | 35% | 能准确返回失败记录，而不是只给出抽象结论。 |
| 指标影响解释 | 25% | 能说明质量问题如何扭曲 KPI 或管理行动。 |
| 治理建议 | 15% | 能提出 owner、steward、门禁和修复流程。 |

## 可选加分

- 将质量规则改写为 SQL 失败记录查询；
- 为 `on_time_delivery_rate` 补充一条指标级质量门禁；
- 比较 clean dataset 与 dirty dataset 的质量报告差异。

