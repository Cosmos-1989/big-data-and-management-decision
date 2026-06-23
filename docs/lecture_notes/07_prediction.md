# 第 7 讲 预测模型基础

本讲正式讲义使用 XeLaTeX 编写，源文件为：

- `docs/lecture_notes/07_prediction.tex`
- `docs/lecture_notes/07_prediction.pdf`

配套 slides 位于：

- `slides/07_prediction/week07_prediction_beamer.tex`
- `slides/07_prediction/week07_prediction_beamer.pdf`

本周实验围绕客户流失预测展开，样例数据为：

- `data/sample/customer_churn.csv`

代码入口为：

- `src/bdm_decision/models/churn_model.py`
- `src/bdm_decision/models/evaluate.py`
- `src/bdm_decision/cases/week07_prediction.py`

最小运行方式：

```bash
PYTHONPATH=src python3 src/bdm_decision/cases/week07_prediction.py
```

本讲重点不是追求复杂算法，而是建立监督学习的基本语言：特征、标签、训练集、测试集、损失函数、交叉验证、过拟合、概率校准、阈值选择和业务损失函数。
