# 第 9 讲 优化与处方分析

本讲正式讲义使用 XeLaTeX 编写，源文件为：

- `docs/lecture_notes/09_optimization.tex`
- `docs/lecture_notes/09_optimization.pdf`

配套 slides 位于：

- `slides/09_optimization/week09_optimization_beamer.tex`
- `slides/09_optimization/week09_optimization_beamer.pdf`

本周实验围绕库存补货优化展开，样例数据为：

- `data/sample/replenishment_planning.csv`

代码入口为：

- `src/bdm_decision/optimization/inventory_optimization.py`
- `src/bdm_decision/optimization/capacity_allocation.py`
- `src/bdm_decision/cases/week09_optimization.py`

最小运行方式：

```bash
PYTHONPATH=src python3 src/bdm_decision/cases/week09_optimization.py
```

本讲重点是从预测和因果证据进入处方分析：明确目标函数、决策变量、约束、情景、成本、收益和敏感性分析。
