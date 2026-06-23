# 第 10 章 流程数据与过程挖掘

本讲正式讲义使用 XeLaTeX 编写，源文件为：

- `docs/lecture_notes/10_process_mining.tex`
- `docs/lecture_notes/10_process_mining.pdf`

配套 slides 位于：

- `slides/10_process_mining/week10_process_mining_beamer.tex`
- `slides/10_process_mining/week10_process_mining_beamer.pdf`

本周实验围绕 order-to-cash 事件日志展开，样例数据为：

- `data/sample/order_to_cash_event_log.csv`

代码入口为：

- `src/bdm_decision/process_mining/event_log.py`
- `src/bdm_decision/ingestion/load_event_logs.py`
- `src/bdm_decision/cases/week10_process_mining.py`

最小运行方式：

```bash
PYTHONPATH=src python3 src/bdm_decision/cases/week10_process_mining.py
```

本讲重点是把业务流程转换为事件日志，并用 case、activity、timestamp、variant、directly-follows graph、throughput time、rework 和 conformance checking 形成流程改进证据。
