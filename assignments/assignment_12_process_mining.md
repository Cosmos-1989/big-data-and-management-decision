# Assignment 12: 流程数据与过程挖掘

## 背景

本周作业围绕 `data/sample/order_to_cash_event_log.csv` 的 order-to-cash 事件日志展开。请将事件日志视为业务流程的可计算证据，而不是普通流水表。

## 任务

1. 运行 `src/bdm_decision/cases/week10_process_mining.py`，记录完整输出。
2. 解释 case id、activity、timestamp、resource、trace 和 variant 的含义。
3. 计算前两个流程变体的 case 数、占比和平均吞吐时间。
4. 找出平均耗时最长的 directly-follows edge，并解释它对应的管理问题。
5. 列出返工 case 和合规异常 case，说明它们对流程改进的意义。
6. 写一段不超过 400 字的管理建议，说明 order-to-cash 流程应优先改进哪些环节。

## 提交要求

- 一份不超过 1200 字的分析报告；
- 至少一个 variant 表和一个 directly-follows edge 表；
- 明确说明 timestamp 质量、流程例外路径和业务上下文对结论的影响；
- 不得只报告平均吞吐时间，必须同时讨论变体、瓶颈、返工和合规异常。
