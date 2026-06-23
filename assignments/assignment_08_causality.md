# Assignment 08: 因果推断与管理干预

## 背景

本周作业围绕优惠券干预是否提高客户留存展开。请注意：优惠券并非随机发放，而是更可能发给高风险客户，因此朴素比较会受到选择偏差影响。

## 任务

1. 运行 `src/bdm_decision/cases/week08_causality.py`，记录完整输出。
2. 解释为什么 `coupon_retention_observational.csv` 中 treated 和 control 的朴素留存率差异为 0，却不能说明优惠券没有效果。
3. 按 `risk_band` 手工复核分层估计，说明风险结构如何改变结论。
4. 解释倾向得分的含义，并说明 IPW 估计依赖哪些关键假设。
5. 基于 `coupon_retention_panel.csv` 计算 DID：写出 treated change、control change 和 DID estimate。
6. 写一段不超过 400 字的管理建议，说明在没有随机实验时，企业应如何谨慎评估干预效果。

## 提交要求

- 一份不超过 1200 字的分析报告；
- 至少一个表格比较 naive、risk-band stratification、IPW 和 DID；
- 明确列出本案例中的识别假设和可能失败的原因；
- 不得把预测准确率或相关关系直接写成因果结论。
