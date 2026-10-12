# 半导体制造 KPI 与运营要素诊断

## 1. 业务对象与分析任务

制造运营分析包括业务对象建模、SQL 指标计算和运营状态展示。批次、设备、工站及订单之间的关系决定记录粒度；指标字典规定汇总方法；看板呈现分布、时间变化及数据质量。

案例使用虚构的半导体制造日运营快照，指标包括 Yield、OEE、Cycle Time、WIP 和 OTD。M13 要素用于组织诊断；字段与要素的对应关系须按具体业务核验。

## 2. 核心 KPI

| KPI | 公式 | 管理含义 | 主要风险 |
|---|---|---|---|
| Yield | `good_units / total_units` | 衡量产出质量和工艺稳定性 | 分母口径、返工后重复计数 |
| OEE | `availability * performance * quality` | 衡量设备综合效率 | 计划时间、停机时间和速度基准不一致 |
| Cycle Time | `lot_end_time - lot_start_time` 或日均周期 | 衡量批次通过速度 | 等待时间和加工时间混淆 |
| WIP | 在制批次数或在制数量 | 衡量流程拥堵和资金占用 | 快照时点不一致 |
| OTD | `orders_on_time / orders_due` | 衡量交付承诺达成 | 订单拆分、延期原因和承诺日期变更 |

## 3. 样例数据

样例数据文件：

```text
data/sample/semiconductor_kpi_daily.csv
```

粒度为“一行一个日期、区域、工作中心、产品族”的日运营快照。主要字段：

| 字段 | 含义 |
|---|---|
| production_date | 生产日期 |
| area | 制造区域，例如 wafer_sort、assembly、final_test |
| work_center | 工作中心或设备组 |
| product_family | 产品族 |
| lots_started | 当日开始批次数 |
| lots_completed | 当日完成批次数 |
| good_units | 良品数 |
| total_units | 总产出数 |
| planned_minutes | 计划生产分钟数 |
| runtime_minutes | 实际运行分钟数 |
| downtime_minutes | 停机分钟数 |
| ideal_cycle_seconds | 单件理想加工秒数 |
| units_processed | 当日处理件数 |
| avg_cycle_time_hours | 平均周期时间 |
| wip_lots | 日末 WIP 批次数 |
| orders_due | 当日到期订单数 |
| orders_on_time | 当日准时订单数 |
| rework_lots | 返工批次数 |
| scrap_units | 报废件数 |

## 4. SQL 分析任务

1. 按 `area` 和 `work_center` 计算 Yield、OEE、Cycle Time、WIP 和 OTD；
2. 按 `product_family` 计算良率和返工率；
3. 找出 OEE 低于 0.75 且 WIP 高于中位数的工作中心；
4. 用窗口函数计算 3 日滚动 Yield 和 3 日滚动 OTD；
5. 输出一条指标字典记录，任选 Yield 或 OEE，说明分子、分母、时间窗口、维度和 owner。

## 5. Dashboard 任务

运营看板包括以下指标和视图：

1. KPI 卡片：Yield、OEE、Cycle Time、WIP、OTD；
2. 趋势图：按日期展示 Yield/OEE/OTD；
3. 瓶颈图：按工作中心展示 WIP 与 Cycle Time；
4. 质量图：按产品族展示 scrap 和 rework；
5. 管理提示：指出哪些结论只是描述性，哪些需要进一步因果或流程分析。

## 6. M13 使用方式

M13 在本案例中用于组织诊断逻辑，而不是替代 KPI。示例：

- Yield 下滑可能同时涉及 M02 Product、M03 Route、M05 Equipment、M08 Quality；
- OEE 下滑可能同时涉及 M05 Equipment、M06 Capacity、M09 Maintenance；
- Cycle Time 上升可能同时涉及 M03 Route、M06 Capacity、M07 WIP、M13 Action；
- OTD 下滑可能同时涉及 M01 Demand、M06 Capacity、M07 WIP、M11 Delivery。

诊断报告应列出指标变化、相关运营要素、待核验的数据及候选行动，并区分观察事实、机制假设和决策建议。

