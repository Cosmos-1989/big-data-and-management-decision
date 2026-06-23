<div align="center">

# 大数据与管理决策基础

### Big Data and Management Decision Foundations

面向「数智化企业运营与优化」微专业的方法论与技术桥梁课程
**从运营问题到可执行决策的完整闭环**

![Python](https://img.shields.io/badge/Python-%3E%3D3.11-3776AB?logo=python&logoColor=white)
![Hours](https://img.shields.io/badge/学时-48-2E7D32)
![Credits](https://img.shields.io/badge/学分-3-2E7D32)
![Modules](https://img.shields.io/badge/教学模块-16-1565C0)
![Status](https://img.shields.io/badge/状态-建设中-orange)

</div>

---

## 目录

- [课程简介](#课程简介)
- [课程主线](#课程主线)
- [能力目标](#能力目标)
- [教学模块（48 学时）](#教学模块48-学时)
- [考核结构](#考核结构)
- [仓库结构](#仓库结构)
- [环境与安装](#环境与安装)
- [快速开始](#快速开始)
- [容器化部署](#容器化部署)
- [实验与项目](#实验与项目)
- [许可证](#许可证)

---

## 课程简介

本仓库承载《大数据与管理决策基础》的全部教学资产：课程大纲、讲义、课件、样例企业运营数据、可复用代码包、实验与作业说明、以及项目报告模板。

课程服务于「数智化企业运营与优化」微专业，承担**方法论与技术桥梁**角色，训练学生把企业运营问题转化为数据系统、分析模型与可执行决策之间的闭环。

| 项目 | 内容 |
|---|---|
| 建议学时 | 48 学时 |
| 建议学分 | 3 学分 |
| 适用对象 | 具备数学、统计、计算机基础的本科生 |
| 技术栈 | Python ≥ 3.11 · SQL（DuckDB/PostgreSQL）· scikit-learn · statsmodels · cvxpy / OR-Tools · Streamlit · FastAPI · MLflow |

---

## 课程主线

```text
运营问题意识 → 数据表达 → 统计分析 → 预测建模 → 因果判断 → 优化决策 → 系统部署与反馈治理
```

课程以企业运营中的真实问题（库存、交付、客户流失、产能瓶颈）为牵引，沿着上述主线逐章推进，最终落地为一个小型企业运营决策系统原型。

---

## 能力目标

1. 理解企业运营数据的基本形态。
2. 使用 SQL 与 Python 完成数据抽取、清洗、统计分析与特征构造。
3. 从管理问题出发建立 KPI、统计模型、预测模型与简单优化模型。
4. 区分描述分析、诊断分析、预测分析、因果分析与处方分析。
5. 理解企业级数据平台、语义层、模型部署、数据治理与 AI 决策系统的基本架构。
6. 完成一个小型企业运营决策系统原型。

---

## 教学模块（48 学时）

| 周次 | 模块 | 理论内容 | 技术内容 | 实验 / 案例 |
|:--:|---|---|---|---|
| 1 | 大数据与管理决策导论 | 数据驱动决策、BI、DSS、decision intelligence | 数据生命周期、CRISP-DM、数据角色 | 拆解库存 / 交付 / 流失 / 产能问题 |
| 2 | 企业数据与业务对象 | 实体、属性、事件、状态、KPI | ER 模型、星型模型、事实表与维度表 | 设计订单—客户—产品—库存数据模型 |
| 3 | SQL 与管理数据查询 | 连接、聚合、窗口函数；KPI 统计含义 | PostgreSQL / DuckDB / SQLite | 构造销售额、毛利率、交付延迟率 |
| 4 | 数据质量与指标治理 | 缺失、异常、口径不一致；指标可比性 | 数据剖析、校验、metadata、lineage | KPI 字典与数据质量报告 |
| 5 | 描述统计与可视化决策 | 分布、相关、分组比较、置信区间 | pandas / Polars、Streamlit | 建立运营驾驶舱 |
| 6 | 统计推断与管理判断 | 抽样、估计、假设检验、A/B 测试 | scipy、statsmodels | 促销是否提高转化率 |
| 7 | 预测模型基础 | 损失函数、偏差—方差、交叉验证 | scikit-learn：回归、树模型、随机森林 | 需求预测 / 客户流失预测 |
| 8 | 解释、预测与可解释性 | 解释模型 vs 预测模型；变量重要性 | 模型评估、特征重要性、误差分析 | 预测准确但不可行动的模型为何失败 |
| 9 | 因果推断与管理干预 | 潜在结果、处理效应、混杂、DID、IV | A/B 测试、倾向得分、简单 DID | 价格 / 优惠券 / 推荐策略的因果评估 |
| 10 | 决策理论与价值评估 | 期望效用、贝叶斯决策、信息价值 | 决策树、敏感性分析、Monte Carlo | 供应商选择、库存补货风险分析 |
| 11 | 从预测到优化 | 线性 / 整数规划、约束、对偶直觉 | scipy.optimize / cvxpy / OR-Tools | 库存补货、排班、产能分配 |
| 12 | 流程数据与过程挖掘 | event log、瓶颈、返工、合规 | process mining、吞吐时间分析 | order-to-cash / procure-to-pay 分析 |
| 13 | 大数据系统与现代数据平台 | 批 / 流处理、数据湖仓、语义层 | Spark / PySpark、dbt、semantic layer | 模拟 lakehouse：bronze/silver/gold |
| 14 | MLOps 与分析工程 | 实验追踪、模型注册、部署、监控、漂移 | Git、Docker、MLflow、FastAPI | 把预测模型封装成 API |
| 15 | Palantir 式决策系统抽象 | ontology、object、link、action、scenario | 自建简化 ontology/action/scenario 框架 | 订单风险—行动推荐—场景比较原型 |
| 16 | AI Agent 与项目答辩 | LLM 与企业数据、NL2SQL、RAG、AI 治理 | SQL agent 原型、提示词评估、日志审计 | 期末项目展示 |

> 32 学时压缩版本与各模块取舍详见 [`course_plan.md`](course_plan.md)。

---

## 考核结构

| 考核项目 | 权重 | 说明 |
|---|:--:|---|
| 平时作业 | 20% | SQL、统计推断、建模、优化的小作业 |
| 实验报告 | 25% | 6 次实验，每次提交代码、结果与业务解释 |
| 期中测验 | 15% | 概念、公式、SQL、统计与优化基础 |
| 综合项目 | 30% | 小组完成企业运营决策系统原型 |
| 项目答辩与个人贡献 | 10% | 展示、问答、代码贡献、决策 memo |

---

## 仓库结构

```text
big-data-and-management-decision/
├── docs/                     课程大纲、讲义（LaTeX + Markdown）、参考资料
│   ├── lecture_notes/        14 章讲义源文件与导出 PDF
│   ├── latex/                讲义 LaTeX 模板
│   └── syllabus.md           课程大纲
├── slides/                   各章节 Beamer 课件源码与导出文件
├── data/                     数据分层（raw/bronze/silver/gold）与样例运营数据
│   └── sample/               订单、客户、库存、事件日志等样例 CSV
├── src/bdm_decision/         可复用课程代码包
│   ├── cases/                各周案例代码（week01–week10）
│   ├── ingestion/            数据加载
│   ├── quality/              数据剖析与校验
│   ├── features/             特征工程
│   ├── models/               预测模型（流失、需求、延误风险）
│   ├── causal/               因果推断（A/B、DID、倾向得分）
│   ├── optimization/         优化（库存、排班、产能）
│   ├── process_mining/       过程挖掘
│   ├── ontology/             Palantir 式 ontology/action/scenario 原型
│   ├── warehouse/            星型模型、KPI 表、数据质量测试（SQL）
│   └── app/                  应用入口（API / dashboard / agent，建设中）
├── tests/                    数据质量、指标、模型、决策规则、ontology 测试
├── assignments/              作业与期末项目说明
├── reports/                  model card、decision memo、项目报告模板
├── notebooks/                学生实验 notebook
├── course_plan.md            课程整体规划文档
├── pyproject.toml            依赖与构建配置
└── docker-compose.yml        容器化运行配置
```

---

## 环境与安装

要求 **Python ≥ 3.11**。建议使用虚拟环境。

```bash
# 1. 克隆仓库
git clone https://github.com/Cosmos-1989/big-data-and-management-decision.git
cd big-data-and-management-decision

# 2. 创建并激活虚拟环境
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. 安装课程代码包（含全部依赖）
pip install -e ".[dev]"
```

核心依赖：`duckdb` · `pandas` · `polars` · `numpy` · `scipy` · `statsmodels` · `scikit-learn` · `matplotlib` · `plotly` · `streamlit` · `cvxpy` · `ortools` · `mlflow` · `fastapi` · `uvicorn` · `jupyterlab`。

---

## 快速开始

```bash
# 运行测试套件（数据质量、指标、模型、决策规则、ontology）
pytest

# 运行某一周的案例代码，例如第 3 周 SQL/KPI
python -m bdm_decision.cases.week03_sql_kpi

# 启动 JupyterLab 进行实验
jupyter lab
```

编译讲义 / 课件（需本地 LaTeX 环境，建议 `xelatex` + `ctex`）：

```bash
# 讲义
cd docs/lecture_notes && xelatex 01_intro.tex

# Beamer 课件
cd slides/01_intro && xelatex week01_data_driven_decision_intro_beamer.tex
```

---

## 容器化部署

仓库提供 `docker-compose.yml`，用于在统一环境中运行课程应用服务：

```bash
docker compose --profile app up
```

> **说明**：`src/bdm_decision/app/`（FastAPI 服务、AI agent）目前为骨架占位，将随第 14–16 周（MLOps、AI Agent）内容逐步完善。当前可直接运行的能力集中在 `cases/`、`models/`、`causal/`、`optimization/` 等模块及测试套件。

---

## 实验与项目

| 编号 | 实验 | 对应模块 |
|:--:|---|---|
| 实验一 | 企业数据建模 | 第 2 周 |
| 实验二 | SQL 与经营分析 | 第 3 周 |
| 实验三 | 数据质量与指标治理 | 第 4 周 |
| 实验四 | 预测模型 | 第 7 周 |
| 实验五 | 因果评估 | 第 9 周 |
| 实验六 | 优化决策 | 第 11 周 |
| 综合项目 | 企业运营决策系统原型 | 期末 |

作业说明见 [`assignments/`](assignments/)，报告模板（model card、decision memo、项目报告）见 [`reports/`](reports/)。

---

## 许可证

许可证待定（TBD）。在正式确定前，课程材料仅供教学与学习用途。

---

<div align="center">
<sub>《大数据与管理决策基础》课程仓库 · 持续建设中</sub>
</div>
