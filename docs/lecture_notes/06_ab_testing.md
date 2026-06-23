# 第 6 讲 统计推断、A/B 测试与管理判断

本讲承接第5讲 dashboard 与经营波动分析，讨论如何判断观察到的指标差异是否足以支持管理行动。核心内容包括总体与样本、估计量、标准误、置信区间、p 值、随机化、A/B 测试、MDE、检验功效、护栏指标和实验决策。

正式讲义源文件与 PDF：

- `docs/lecture_notes/06_ab_testing.tex`
- `docs/lecture_notes/06_ab_testing.pdf`

配套 slides：

- `slides/06_ab_testing/week06_ab_testing_beamer.tex`
- `slides/06_ab_testing/week06_ab_testing_beamer.pdf`

配套代码与数据：

- `data/sample/ab_test_checkout.csv`
- `src/bdm_decision/causal/ab_test.py`
- `src/bdm_decision/cases/week06_ab_testing.py`

最小运行方式：

```bash
PYTHONPATH=src python3 src/bdm_decision/cases/week06_ab_testing.py
```
