# 第 8 讲 因果推断与管理干预

本讲正式讲义使用 XeLaTeX 编写，源文件为：

- `docs/lecture_notes/08_causality.tex`
- `docs/lecture_notes/08_causality.pdf`

配套 slides 位于：

- `slides/08_causality/week08_causality_beamer.tex`
- `slides/08_causality/week08_causality_beamer.pdf`

本周实验围绕优惠券干预与客户留存展开，样例数据为：

- `data/sample/coupon_retention_observational.csv`
- `data/sample/coupon_retention_panel.csv`

代码入口为：

- `src/bdm_decision/causal/propensity_score.py`
- `src/bdm_decision/causal/did.py`
- `src/bdm_decision/cases/week08_causality.py`

最小运行方式：

```bash
PYTHONPATH=src python3 src/bdm_decision/cases/week08_causality.py
```

本讲重点是区分预测、相关与因果；理解潜在结果、反事实、混杂、选择偏差、倾向得分、重叠性、SUTVA、DID 和平行趋势假设。
