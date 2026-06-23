---
title: "《大数据与管理决策基础》课程规划"
subtitle: "数智化企业运营与优化微型专业课程开发蓝图"
version: "v0.1"
language: "zh-CN"
intended_use: "供后续继续开发课程大纲、讲义、实验、项目仓库与教学材料"
---

# 《大数据与管理决策基础》课程规划

## 0. 文档用途

本文档用于支持数学与统计学院“数智化企业运营与优化”微型专业中《大数据与管理决策基础》课程的后续开发。其主要用途包括：

1. 明确课程在微型专业中的定位；
2. 给出课程知识结构、理论主线、信息技术栈和实验体系；
3. 为后续在 Codex 中开发课程讲义、PPT、实验代码、项目模板和作业系统提供蓝图；
4. 将 Palantir 等企业级数据与 AI 平台的技术实践抽象为可教学、可复现、可开源实现的课程框架。

本课程不是单纯的“Python 数据分析课”，也不是后续《企业运营数据挖掘与分析》《流程优化与数理决策》的提前重复。其核心定位是：训练学生把企业运营问题转化为数据系统、分析模型和可执行决策之间的闭环。

---

# 第一部分 课程总体定位

## 1.1 微型专业中的课程位置

微型专业“数智化企业运营与优化”包含五门课程：

1. 数智化运营概论；
2. 大数据与管理决策基础；
3. 企业运营数据挖掘与分析；
4. 流程优化与数理决策；
5. 数智化运营综合实训。

其中，《大数据与管理决策基础》应承担“方法论与技术桥梁”的角色。它位于概论课之后，专业分析课与优化课之前，既要帮助学生理解企业经营数据的基本结构，又要帮助学生掌握数据驱动决策的基本逻辑。

课程在整个微型专业中的功能可以概括为：

\[
\text{运营问题意识}
\longrightarrow
\text{数据表达}
\longrightarrow
\text{统计分析}
\longrightarrow
\text{预测建模}
\longrightarrow
\text{因果判断}
\longrightarrow
\text{优化决策}
\longrightarrow
\text{系统部署}.
\]

## 1.2 课程核心定位

课程名称：大数据与管理决策基础。

建议学时：48 学时。

建议学分：3 学分。

适用对象：数学学院本科生或具有数学、统计、计算机基础的跨学科学生。

前置课程建议：

- 高等数学或数学分析；
- 线性代数；
- 概率论与数理统计；
- Python 基础；
- 基础数据库知识可在课程中补充。

课程核心能力目标：

1. 能够理解企业运营数据的基本形态，包括订单、客户、产品、库存、供应商、流程日志等；
2. 能够使用 SQL 和 Python 完成基本的数据抽取、清洗、统计分析和特征构造；
3. 能够从管理问题出发建立 KPI、统计模型、预测模型和简单优化模型；
4. 能够区分描述分析、诊断分析、预测分析、因果分析和处方分析；
5. 能够理解企业级数据平台、语义层、模型部署、数据治理和 AI 决策系统的基本架构；
6. 能够完成一个小型“企业运营决策系统”原型。

---

# 第二部分 课程设计依据

## 2.1 学术依据

本课程的理论基础来自以下几个领域：

### 2.1.1 商业智能与数据驱动决策

商业智能与分析从传统报表系统发展到大数据、实时分析、移动分析、社交网络分析和 AI 决策系统。课程应帮助学生理解 BI、DSS、analytics、decision intelligence 之间的关系。

相关主题：

- Business Intelligence and Analytics；
- Data-driven decision making；
- Decision Support Systems；
- Management Information Systems；
- Analytics capability；
- Digital transformation。

### 2.1.2 数据挖掘与项目生命周期

CRISP-DM 仍然适合作为课程的基础项目过程模型：

1. Business Understanding；
2. Data Understanding；
3. Data Preparation；
4. Modeling；
5. Evaluation；
6. Deployment。

但在现代企业环境中，课程需要进一步补充：

- MLOps；
- CRISP-ML(Q)；
- 数据质量管理；
- 模型监控；
- 数据漂移与模型漂移；
- 模型治理；
- 反馈闭环。

### 2.1.3 统计学习与预测建模

课程应介绍经验风险最小化、训练集/测试集、交叉验证、过拟合、偏差—方差权衡、损失函数等核心概念。

统一表达为：

\[
\hat f
=
\arg\min_{f\in\mathcal F}
\frac{1}{n}
\sum_{i=1}^{n}
\ell(y_i,f(x_i))
+
\Omega(f).
\]

该表达可以涵盖线性回归、逻辑回归、树模型、随机森林、梯度提升等基础模型。

### 2.1.4 因果推断与管理干预

管理决策不仅需要预测，还需要判断行动是否有效。例如，企业不只想知道“哪些客户可能流失”，还想知道“给哪些客户优惠券能够真正降低流失率”。

课程应引入潜在结果框架：

\[
\tau
=
\mathbb E[Y(1)-Y(0)].
\]

核心概念包括：

- 处理组与对照组；
- 随机实验；
- 混杂因素；
- 选择偏差；
- A/B 测试；
- 倾向得分；
- DID 的基本思想；
- 因果效应与预测相关性的区别。

### 2.1.5 优化与处方分析

企业管理决策通常是有约束的资源配置问题，可以统一表达为：

\[
\min_{x} c^\top x,
\qquad
Ax\le b,
\qquad
x\ge 0.
\]

课程应介绍线性规划、整数规划、约束优化和情景分析的基础概念，为后续《流程优化与数理决策》课程作铺垫。

## 2.2 企业技术实践依据

现代企业数据平台正在从“报表型 BI”转向“数据—模型—业务对象—行动—反馈”的一体化平台。课程应参考但不依赖以下技术实践：

### 2.2.1 Palantir 式企业决策系统

Palantir Foundry / AIP 的可借鉴点不在于某个单一软件功能，而在于其平台思想：

- Ontology：将组织中的订单、客户、设备、资产、交易、任务等抽象为业务对象；
- Object：业务对象；
- Link：对象之间的关系；
- Action：用户或系统可以执行的管理动作；
- Function：与对象、动作和模型相连接的业务函数；
- Scenario：不同管理行动下的情景推演；
- Security and Audit：权限、审计和行动日志；
- AI Workflow / Agent：把大模型、企业数据、业务流程和人类审批连接起来。

课程应将上述思想转化为一个开放可实现的教学框架，而不应要求学生使用闭源商业平台。

### 2.2.2 Lakehouse 与现代数据平台

课程应让学生理解：

- 数据库；
- 数据仓库；
- 数据湖；
- Lakehouse；
- 批处理；
- 流处理；
- 语义层；
- 数据血缘；
- 元数据；
- 指标治理。

可参考的产业实践包括 Databricks Lakehouse、Snowflake、Microsoft Fabric、dbt Semantic Layer 等。

### 2.2.3 MLOps 与模型生命周期

课程应介绍模型从 notebook 到生产系统的基本过程：

1. 数据版本管理；
2. 实验追踪；
3. 模型训练；
4. 模型评估；
5. 模型注册；
6. 模型部署；
7. 模型监控；
8. 漂移检测；
9. 模型更新；
10. 模型审计。

可采用 MLflow、FastAPI、Docker、Git 等工具做简化实验。

### 2.2.4 AI Agent 与企业数据

课程可引入 AI Agent 的基础实践，但应强调风险控制。企业级 AI 助手不能只是普通聊天机器人，而应具有以下约束：

- 连接受治理的数据源；
- 通过语义层解释业务指标；
- 能够生成 SQL 但必须校验；
- 能够调用工具但必须记录日志；
- 关键决策必须保留 human-in-the-loop；
- 权限、审计、安全和错误评估不可省略。

---

# 第三部分 课程主线

## 3.1 总体主线

课程主线为：

\[
\text{描述分析}
\longrightarrow
\text{诊断分析}
\longrightarrow
\text{预测分析}
\longrightarrow
\text{因果分析}
\longrightarrow
\text{处方分析}
\longrightarrow
\text{系统部署}
\longrightarrow
\text{反馈治理}.
\]

管理决策可统一表达为：

\[
a^*(x)
=
\arg\min_{a\in \mathcal A(x)}
\mathbb E[L(Y,a)\mid X=x]
+
\lambda C(a),
\]

其中：

- \(X\)：企业当前状态数据；
- \(Y\)：未来经营结果；
- \(a\)：可选管理行动；
- \(\mathcal A(x)\)：在状态 \(x\) 下可行的行动集合；
- \(L(Y,a)\)：行动造成的业务损失；
- \(C(a)\)：行动成本或约束惩罚；
- \(\lambda\)：成本权重或风险偏好参数。

该公式帮助学生理解：数据分析并不以“模型准确率”为终点，而以“可执行、可评估、可反馈的管理行动”为终点。

## 3.2 与后续课程的边界

与《企业运营数据挖掘与分析》的边界：

- 本课程讲建模基础、决策框架、工程流程；
- 后续课程可深入讲聚类、关联规则、推荐系统、深度学习、文本挖掘、图挖掘等算法。

与《流程优化与数理决策》的边界：

- 本课程讲优化思想和简单线性规划；
- 后续课程可深入讲排队论、网络流、整数规划、动态规划、鲁棒优化、随机优化、仿真优化等。

与《数智化运营综合实训》的边界：

- 本课程完成小型原型；
- 综合实训可完成更完整的行业案例、系统集成和团队项目。

---

# 第四部分 教学模块设计

## 4.1 48 学时版本

| 周次 | 模块 | 理论内容 | 技术内容 | 实验或案例 |
|---|---|---|---|---|
| 1 | 大数据与管理决策导论 | 数据驱动决策、BI、DSS、decision intelligence；企业问题如何转化为数据问题 | 数据生命周期、CRISP-DM、数据角色 | 拆解库存、交付、客户流失或产能瓶颈问题 |
| 2 | 企业数据与业务对象 | 关系、实体、属性、事件、状态、KPI；从业务流程到数据模型 | ER 模型、星型模型、宽表、事实表、维度表 | 设计订单—客户—产品—库存数据模型 |
| 3 | SQL 与管理数据查询 | 集合、连接、聚合、窗口函数；KPI 的统计含义 | PostgreSQL / DuckDB / SQLite；SQL joins、group by、window functions | 从订单表构造销售额、毛利率、交付延迟率 |
| 4 | 数据质量、数据治理与指标体系 | 缺失、异常、偏差、口径不一致；指标可比性 | 数据剖析、数据校验、metadata、lineage | 设计 KPI 字典与数据质量报告 |
| 5 | 描述统计与可视化决策 | 分布、相关、分组比较、置信区间；图形误导 | pandas / Polars、Power BI / Superset / Streamlit | 建立运营驾驶舱 |
| 6 | 统计推断与管理判断 | 抽样、估计、假设检验、置信区间、A/B 测试基础 | scipy、statsmodels | 促销活动是否提高转化率 |
| 7 | 预测模型基础 | 损失函数、偏差—方差、训练集/测试集、交叉验证 | scikit-learn：线性回归、逻辑回归、树模型、随机森林 | 需求预测或客户流失预测 |
| 8 | 解释、预测与可解释性 | 解释模型与预测模型的区别；变量重要性；模型风险 | 模型评估、特征重要性、误差分析 | 预测准确但不可行动的模型为何失败 |
| 9 | 因果推断与管理干预 | 潜在结果、处理效应、混杂、匹配、DID、工具变量直觉 | A/B 测试、倾向得分、简单 DID | 价格调整、优惠券、推荐策略的因果评估 |
| 10 | 决策理论与价值评估 | 期望效用、贝叶斯决策、信息价值、风险偏好 | 决策树、敏感性分析、Monte Carlo | 供应商选择、库存补货的风险分析 |
| 11 | 从预测到优化 | 线性规划、整数规划、约束、目标函数、对偶直觉 | scipy.optimize / cvxpy / OR-Tools | 库存补货、排班、产能分配 |
| 12 | 流程数据与过程挖掘 | event log、case id、activity、timestamp；瓶颈、返工、合规 | process mining 基础、流程图、吞吐时间分析 | order-to-cash 或 procure-to-pay 流程分析 |
| 13 | 大数据系统与现代数据平台 | 批处理、流处理、数据湖、数据仓库、lakehouse、语义层 | Spark / PySpark、dbt、semantic layer | 小规模模拟 lakehouse：bronze/silver/gold |
| 14 | MLOps 与分析工程 | 实验追踪、模型注册、版本控制、部署、监控、漂移 | Git、Docker、MLflow、FastAPI、Airflow/Prefect | 把一个预测模型封装成 API |
| 15 | Palantir 式决策系统抽象 | ontology、object、link、action、scenario、function、权限、审计 | 自建简化 ontology/action/scenario 框架 | 构建“订单风险—行动推荐—场景比较”原型 |
| 16 | AI Agent 与课程项目答辩 | LLM 与企业数据、NL2SQL、RAG、human-in-the-loop、AI 治理 | SQL agent 原型、提示词评估、日志审计 | 期末项目展示 |

## 4.2 32 学时压缩版本

若课程只有 32 学时，建议保留以下 10 个核心模块：

1. 数据驱动管理决策导论；
2. 企业数据模型与 KPI；
3. SQL 与管理数据查询；
4. 数据质量与数据治理；
5. 描述统计与可视化；
6. 统计推断与 A/B 测试；
7. 预测模型基础；
8. 因果推断基础；
9. 优化与处方分析；
10. 企业决策系统原型与项目答辩。

可压缩或作为阅读材料处理的模块：

- Spark 与大数据平台；
- MLOps；
- AI Agent；
- 流程挖掘；
- Palantir 式 ontology 深入实现。

---

# 第五部分 数学内容设计

## 5.1 数据表示

关系数据可以视为有限集合上的函数与关系。

若客户集合为 \(C\)，产品集合为 \(P\)，订单集合为 \(O\)，则订单数据可表示为：

\[
o_i = (c_i,p_i,q_i,t_i,r_i),
\]

其中：

- \(c_i\in C\)：客户；
- \(p_i\in P\)：产品；
- \(q_i\)：数量；
- \(t_i\)：时间；
- \(r_i\)：地区或渠道。

流程日志可表示为：

\[
e_i = (case_i, activity_i, timestamp_i, resource_i).
\]

图数据可表示为：

\[
G=(V,E),
\]

其中 \(V\) 是业务对象，\(E\) 是对象之间的关系。例如客户—产品—订单—供应商之间可以形成异质图。

## 5.2 统计推断

课程应覆盖：

- 样本与总体；
- 均值、方差、分位数；
- 置信区间；
- 假设检验；
- \(p\)-value 的正确解释；
- 多重比较的风险；
- 抽样偏差；
- 管理报表中的统计误读。

一个基本估计问题为：

\[
\bar X = \frac{1}{n}\sum_{i=1}^{n}X_i,
\qquad
\operatorname{SE}(\bar X)=\frac{s}{\sqrt n}.
\]

## 5.3 预测建模

课程应通过统一框架讲授监督学习：

\[
Y=f(X)+\varepsilon.
\]

常用损失函数包括：

均方误差：

\[
\ell(y,\hat y)=(y-\hat y)^2.
\]

交叉熵损失：

\[
\ell(y,\hat p)
=
-y\log \hat p-(1-y)\log(1-\hat p).
\]

评价指标包括：

- RMSE；
- MAE；
- Accuracy；
- Precision；
- Recall；
- F1；
- AUC；
- calibration；
- 业务损失函数。

## 5.4 因果推断

管理决策中的因果问题可以写作：

\[
Y_i = D_iY_i(1)+(1-D_i)Y_i(0),
\]

但每个个体只能观察到一个潜在结果。因此平均处理效应为：

\[
ATE=\mathbb E[Y(1)-Y(0)].
\]

教学重点不是证明高级定理，而是帮助学生建立区分以下三者的意识：

1. 相关关系；
2. 预测关系；
3. 因果关系。

## 5.5 决策与优化

企业决策一般具有目标和约束：

\[
\min_x f(x)
\]

subject to

\[
g_i(x)\le 0,\quad i=1,\dots,m,
\]

\[
h_j(x)=0,\quad j=1,\dots,k.
\]

库存决策示例：

\[
\min_{q}
\mathbb E
\left[
c_h(q-D)^+
+
c_s(D-q)^+
\right],
\]

其中：

- \(q\)：订货量；
- \(D\)：需求；
- \(c_h\)：持有成本；
- \(c_s\)：缺货成本。

---

# 第六部分 信息技术体系

## 6.1 必修核心技术栈

| 类型 | 工具 | 教学目标 |
|---|---|---|
| 数据库 | SQLite / DuckDB / PostgreSQL | SQL、关系建模、聚合查询、窗口函数 |
| 数据分析 | Python、pandas、NumPy、Polars | 数据清洗、统计计算、特征构造 |
| 统计建模 | scipy、statsmodels | 回归、推断、假设检验 |
| 机器学习 | scikit-learn | 分类、回归、交叉验证、模型评估 |
| 优化 | scipy.optimize、cvxpy、OR-Tools | 线性规划、整数规划、资源配置 |
| 可视化 | matplotlib、Plotly、Power BI / Superset / Streamlit | 仪表盘与管理沟通 |
| 工程基础 | Git、Docker、Jupyter、VS Code | 可复现分析项目 |

## 6.2 拓展技术栈

| 类型 | 工具或平台 | 教学意义 |
|---|---|---|
| 大数据处理 | Spark / PySpark | 分布式 DataFrame、批处理、机器学习流水线 |
| Lakehouse | Delta Lake / Apache Iceberg / Databricks 思想 | 理解数据湖与数据仓库融合架构 |
| 语义层 | dbt Semantic Layer | 指标集中治理和业务口径统一 |
| MLOps | MLflow | 实验追踪、模型注册、模型部署 |
| 工作流 | Airflow / Prefect | 数据管道编排 |
| API | FastAPI | 模型和决策服务封装 |
| 容器化 | Docker | 环境复现和部署 |
| BI | Power BI / Superset / Metabase | 管理驾驶舱 |
| AI | RAG、NL2SQL、SQL Agent | 企业数据问答与行动建议 |
| 流程智能 | process mining 工具 | 从事件日志发现流程瓶颈 |

## 6.3 建议开发环境

推荐最小开发环境：

```bash
python >= 3.11
duckdb
pandas
polars
numpy
scipy
statsmodels
scikit-learn
matplotlib
plotly
streamlit
cvxpy
ortools
mlflow
fastapi
uvicorn
pytest
ruff
jupyterlab
```

推荐使用 `uv` 或 `poetry` 管理 Python 环境。

---

# 第七部分 课程项目仓库框架

## 7.1 仓库结构

建议在 Codex 中按照以下结构开发课程项目模板：

```text
big-data-management-decision/
  README.md
  LICENSE
  pyproject.toml
  docker-compose.yml
  .env.example
  .gitignore

  docs/
    syllabus.md
    lecture_notes/
      01_intro.md
      02_enterprise_data_model.md
      03_sql_kpi.md
      04_data_quality.md
      05_statistics_dashboard.md
      06_ab_testing.md
      07_prediction.md
      08_causality.md
      09_optimization.md
      10_process_mining.md
      11_modern_data_platform.md
      12_mlops.md
      13_ontology_action_scenario.md
      14_ai_agent.md
    references.md

  slides/
    01_intro/
    02_enterprise_data_model/
    03_sql_kpi/
    04_data_quality/
    05_statistics_dashboard/
    06_ab_testing/
    07_prediction/
    08_causality/
    09_optimization/
    10_process_mining/
    11_modern_data_platform/
    12_mlops/
    13_ontology_action_scenario/
    14_ai_agent/

  data/
    raw/
    bronze/
    silver/
    gold/
    sample/
      orders.csv
      customers.csv
      products.csv
      inventory.csv
      suppliers.csv
      logistics.csv
      event_log.csv

  notebooks/
    01_data_understanding.ipynb
    02_sql_kpi.ipynb
    03_data_quality.ipynb
    04_dashboard.ipynb
    05_ab_testing.ipynb
    06_prediction.ipynb
    07_causal_inference.ipynb
    08_optimization.ipynb
    09_process_mining.ipynb
    10_scenario_analysis.ipynb

  src/
    bdm_decision/
      __init__.py

      ingestion/
        load_orders.py
        load_inventory.py
        load_event_logs.py

      quality/
        checks.py
        data_profile.py
        validation_rules.py

      warehouse/
        build_star_schema.sql
        build_kpi_tables.sql
        metrics.yml

      features/
        build_features.py

      models/
        demand_forecast.py
        delay_risk_model.py
        churn_model.py
        evaluate.py

      causal/
        ab_test.py
        propensity_score.py
        did.py

      optimization/
        inventory_optimization.py
        workforce_scheduling.py
        capacity_allocation.py

      ontology/
        objects.py
        links.py
        actions.py
        scenarios.py
        permissions.py
        audit.py

      app/
        dashboard.py
        api.py
        agent.py

  tests/
    test_data_quality.py
    test_metrics.py
    test_models.py
    test_decision_rules.py
    test_ontology.py

  assignments/
    assignment_01_data_modeling.md
    assignment_02_sql_kpi.md
    assignment_03_data_quality.md
    assignment_04_dashboard.md
    assignment_05_prediction.md
    assignment_06_causal_inference.md
    assignment_07_optimization.md
    final_project.md

  reports/
    model_card_template.md
    decision_memo_template.md
    project_report_template.md
```

## 7.2 最小可行课程仓库

如果开发时间有限，可先完成 MVP 版本：

```text
big-data-management-decision-mvp/
  README.md
  data/
    sample/
      orders.csv
      customers.csv
      products.csv
      inventory.csv
  notebooks/
    01_sql_kpi.ipynb
    02_prediction.ipynb
    03_optimization.ipynb
  src/
    ontology/
      objects.py
      actions.py
      scenarios.py
    app/
      dashboard.py
  assignments/
    final_project.md
```

MVP 必须具备：

1. 一份课程大纲；
2. 一套样例企业运营数据；
3. 一个 SQL/KPI 实验；
4. 一个预测模型实验；
5. 一个优化决策实验；
6. 一个 ontology/action/scenario 小原型；
7. 一个期末项目说明。

---

# 第八部分 Palantir 式教学抽象

## 8.1 核心思想

Palantir 式平台思想可抽象为：

\[
\text{Tables}
\longrightarrow
\text{Objects}
\longrightarrow
\text{Links}
\longrightarrow
\text{Actions}
\longrightarrow
\text{Scenarios}
\longrightarrow
\text{Decisions}.
\]

传统数据分析关注：

\[
\text{Data}
\longrightarrow
\text{Model}
\longrightarrow
\text{Report}.
\]

而现代企业决策系统关注：

\[
\text{Data}
\longrightarrow
\text{Ontology}
\longrightarrow
\text{Model}
\longrightarrow
\text{Action}
\longrightarrow
\text{Audit}
\longrightarrow
\text{Feedback}.
\]

## 8.2 课程中的简化实现

### 8.2.1 业务对象

```python
from dataclasses import dataclass
from typing import Any


@dataclass
class BusinessObject:
    object_id: str
    object_type: str
    properties: dict[str, Any]
```

示例：

```python
order = BusinessObject(
    object_id="ORD-001",
    object_type="Order",
    properties={
        "customer_id": "CUS-032",
        "product_id": "PRD-008",
        "quantity": 120,
        "status": "delayed",
        "delay_risk": 0.82,
    },
)
```

### 8.2.2 业务关系

```python
@dataclass
class BusinessLink:
    source_id: str
    target_id: str
    link_type: str
    properties: dict[str, Any]
```

示例：

```python
link = BusinessLink(
    source_id="CUS-032",
    target_id="ORD-001",
    link_type="PLACED",
    properties={"channel": "online"},
)
```

### 8.2.3 管理行动

```python
@dataclass
class BusinessAction:
    action_id: str
    name: str
    target_object_id: str
    parameters: dict[str, Any]
    expected_effect: dict[str, Any]
    cost: float
```

示例：

```python
action = BusinessAction(
    action_id="ACT-001",
    name="expedite_delivery",
    target_object_id="ORD-001",
    parameters={"extra_cost": 300, "supplier": "SUP-002"},
    expected_effect={"delay_probability_reduction": 0.35},
    cost=300,
)
```

### 8.2.4 情景推演

```python
@dataclass
class Scenario:
    scenario_id: str
    base_state_id: str
    actions: list[BusinessAction]
    predicted_kpis: dict[str, float]
```

示例：

```python
scenario = Scenario(
    scenario_id="SCN-001",
    base_state_id="STATE-2026-01",
    actions=[action],
    predicted_kpis={
        "on_time_delivery_rate": 0.94,
        "total_cost": 125000.0,
        "customer_satisfaction": 0.88,
    },
)
```

## 8.3 教学目标

学生应理解以下问题：

1. 为什么企业数据不能只停留在表格层面；
2. 为什么需要把数据映射为业务对象；
3. 为什么模型输出必须连接到行动；
4. 为什么行动必须有权限、成本、预期效果和审计日志；
5. 为什么情景推演比单一预测值更适合管理决策；
6. 为什么 AI Agent 必须受到数据、权限、工具和流程约束。

---

# 第九部分 实验体系

## 9.1 实验一：企业数据建模

目标：

- 理解企业运营数据的基本结构；
- 设计 ER 图、星型模型和 KPI 字典。

任务：

1. 给定客户、订单、产品、库存、供应商数据；
2. 识别实体、属性和关系；
3. 设计事实表和维度表；
4. 定义至少 10 个运营 KPI；
5. 写出每个 KPI 的计算口径。

提交物：

- ER 图；
- 星型模型图；
- KPI 字典；
- SQL 建表脚本。

## 9.2 实验二：SQL 与经营分析

目标：

- 掌握 SQL 在管理分析中的基本用法；
- 理解 KPI 的计算逻辑。

任务：

1. 计算销售额、订单量、客单价；
2. 计算毛利率；
3. 计算库存周转率；
4. 计算延期交付率；
5. 使用窗口函数计算滚动销售额；
6. 识别高风险订单。

提交物：

- SQL 脚本；
- 结果表；
- 简短业务解释。

## 9.3 实验三：数据质量与指标治理

目标：

- 识别企业数据中的质量问题；
- 建立基本数据校验规则。

任务：

1. 检查缺失值；
2. 检查重复记录；
3. 检查异常值；
4. 检查主外键一致性；
5. 生成数据质量报告；
6. 设计数据修复策略。

提交物：

- 数据剖析报告；
- 数据校验代码；
- 修复前后对比结果。

## 9.4 实验四：预测模型

目标：

- 掌握从业务问题到预测模型的基本流程。

可选题目：

- 需求预测；
- 客户流失预测；
- 订单延期预测。

任务：

1. 定义预测目标；
2. 构造特征；
3. 划分训练集和测试集；
4. 训练至少两个模型；
5. 比较模型表现；
6. 解释模型结果；
7. 讨论业务行动含义。

提交物：

- notebook；
- 模型评估表；
- 误差分析；
- model card。

## 9.5 实验五：因果评估

目标：

- 理解相关、预测与因果的区别；
- 学会基本干预效果评估。

可选题目：

- 促销是否提高转化率；
- 优惠券是否降低流失率；
- 物流加急是否提高满意度；
- 推荐系统是否提高复购率。

任务：

1. 构造处理组和对照组；
2. 比较 naïve difference；
3. 控制基本混杂变量；
4. 估计处理效应；
5. 讨论识别假设；
6. 给出管理建议。

提交物：

- 因果分析报告；
- 代码；
- 决策建议。

## 9.6 实验六：优化决策

目标：

- 把预测结果转化为行动方案；
- 使用优化模型处理资源约束。

可选题目：

- 库存补货；
- 人员排班；
- 产能分配；
- 供应商选择。

任务：

1. 定义决策变量；
2. 定义目标函数；
3. 定义约束条件；
4. 求解优化问题；
5. 做敏感性分析；
6. 比较不同情景下的结果。

提交物：

- 数学模型；
- 求解代码；
- 情景比较；
- 管理解释。

## 9.7 综合项目：企业运营决策系统原型

最低要求：

1. 一个规范化数据库或 lakehouse 分层数据集；
2. 一个 KPI dashboard；
3. 一个预测模型；
4. 一个因果评估或策略评估模块；
5. 一个优化或行动推荐模块；
6. 一个 ontology/action/scenario 原型；
7. 一份面向管理者的 decision memo；
8. 一份技术说明文档；
9. 可复现实验环境。

---

# 第十部分 期末项目题目

## 10.1 零售企业库存与补货决策

核心问题：

- 如何预测需求；
- 如何识别缺货风险；
- 如何平衡库存成本与服务水平；
- 如何制定补货方案。

技术要点：

- 时间序列特征；
- 需求预测；
- 安全库存；
- Newsvendor model；
- 线性规划；
- 情景分析。

## 10.2 制造企业交付延期风险预警

核心问题：

- 哪些订单存在延期风险；
- 影响延期的关键因素是什么；
- 是否需要加急处理；
- 如何分配有限产能。

技术要点：

- 分类模型；
- 特征重要性；
- 产能约束；
- 行动成本；
- scenario analysis。

## 10.3 客户流失与干预策略

核心问题：

- 哪些客户可能流失；
- 干预是否真的有效；
- 应该干预哪些客户；
- 如何控制优惠成本。

技术要点：

- 流失预测；
- 倾向得分；
- uplift 思想；
- 客户终身价值；
- 优惠券分配优化。

## 10.4 采购到付款流程优化

核心问题：

- 流程实际运行路径是什么；
- 哪些环节造成瓶颈；
- 是否存在返工；
- 如何缩短流程周期。

技术要点：

- event log；
- process mining；
- 吞吐时间；
- 流程变体；
- 合规检查。

## 10.5 企业经营 AI 助手

核心问题：

- 如何让管理者用自然语言查询经营数据；
- 如何防止错误 SQL；
- 如何解释指标口径；
- 如何控制权限和审计。

技术要点：

- semantic layer；
- NL2SQL；
- RAG；
- tool calling；
- human-in-the-loop；
- 日志审计。

---

# 第十一部分 考核方案

## 11.1 总体考核结构

| 考核项目 | 权重 | 说明 |
|---|---:|---|
| 平时作业 | 20% | SQL、统计推断、建模、优化的小作业 |
| 实验报告 | 25% | 6 次实验，每次提交代码、结果和业务解释 |
| 期中测验 | 15% | 概念、公式、SQL、统计与优化基础 |
| 综合项目 | 30% | 小组完成企业运营决策系统原型 |
| 项目答辩与个人贡献 | 10% | 展示、问答、代码贡献、决策 memo |

## 11.2 综合项目评分细则

| 维度 | 权重 |
|---|---:|
| 业务问题定义清楚 | 15% |
| 数据模型与数据质量处理规范 | 15% |
| 统计/机器学习模型合理 | 15% |
| 决策模型或优化模型有数学表达 | 15% |
| Dashboard 与管理解释有效 | 10% |
| ontology/action/scenario 设计 | 15% |
| 工程规范、复现性、文档 | 10% |
| 风险、伦理、治理意识 | 5% |

## 11.3 个人贡献评价

建议要求每组提交：

1. Git commit 记录；
2. 分工说明；
3. 个人反思；
4. 互评表；
5. 项目答辩个人问答。

---

# 第十二部分 Codex 开发任务清单

## 12.1 第一阶段：课程基础材料

目标：形成可以开课的最小材料包。

任务：

- [ ] 编写 `syllabus.md`；
- [ ] 编写 16 周教学计划；
- [ ] 编写课程目标与毕业要求对应表；
- [ ] 编写课程考核方案；
- [ ] 编写期末项目说明；
- [ ] 建立样例数据集；
- [ ] 建立课程仓库结构。

## 12.2 第二阶段：实验体系开发

目标：形成可运行的实验代码。

任务：

- [ ] 开发企业运营样例数据库；
- [ ] 开发 SQL/KPI 实验；
- [ ] 开发数据质量实验；
- [ ] 开发 dashboard 实验；
- [ ] 开发预测模型实验；
- [ ] 开发因果评估实验；
- [ ] 开发优化决策实验；
- [ ] 编写每个实验的教师版答案。

## 12.3 第三阶段：讲义与课件开发

目标：形成完整教学内容。

任务：

- [ ] 编写每章讲义；
- [ ] 为每章生成 PPT；
- [ ] 为每章配置课堂案例；
- [ ] 为每章设计课后作业；
- [ ] 为关键章节补充数学推导；
- [ ] 为实践章节补充代码说明。

## 12.4 第四阶段：Palantir 式系统原型

目标：形成课程特色项目。

任务：

- [ ] 设计 ontology schema；
- [ ] 实现 BusinessObject；
- [ ] 实现 BusinessLink；
- [ ] 实现 BusinessAction；
- [ ] 实现 Scenario；
- [ ] 实现简单权限控制；
- [ ] 实现行动日志；
- [ ] 将预测模型接入 action recommendation；
- [ ] 将优化模型接入 scenario comparison；
- [ ] 实现 Streamlit dashboard；
- [ ] 编写项目说明文档。

## 12.5 第五阶段：AI Agent 拓展

目标：形成前沿拓展模块。

任务：

- [ ] 实现基于语义层的指标问答；
- [ ] 实现简单 NL2SQL；
- [ ] 增加 SQL 校验；
- [ ] 增加执行权限控制；
- [ ] 增加工具调用日志；
- [ ] 增加错误案例库；
- [ ] 编写 AI 治理说明；
- [ ] 编写 human-in-the-loop 流程说明。

---

# 第十三部分 每章开发模板

后续在 Codex 中开发每一章时，建议统一使用以下模板。

```markdown
# 第 X 章 章节标题

## 1. 学习目标

学生完成本章后应能够：

1. ...
2. ...
3. ...

## 2. 管理问题导入

给出一个企业运营场景，引导学生理解本章问题。

## 3. 理论基础

包括概念、定义、公式、命题或基本推导。

## 4. 数据与技术方法

说明本章使用的数据、工具和代码框架。

## 5. 案例分析

完整展示一个从问题到结果的分析案例。

## 6. 实验任务

给出学生需要完成的实验步骤。

## 7. 结果解释与管理含义

强调分析结果如何转化为管理判断。

## 8. 常见错误

列出学生容易犯的概念错误、统计错误、代码错误和业务解释错误。

## 9. 课后作业

包括概念题、计算题、代码题和开放讨论题。

## 10. 延伸阅读
```

---

# 第十四部分 参考资料

## 14.1 商业智能与数据驱动决策

1. Chen, H., Chiang, R. H. L., & Storey, V. C. Business Intelligence and Analytics: From Big Data to Big Impact.
2. Davenport, T. H. Competing on Analytics.
3. Brynjolfsson, E., Hitt, L. M., & Kim, H. H. Strength in Numbers: How Does Data-Driven Decisionmaking Affect Firm Performance?
4. Wamba, S. F. et al. Big data analytics and firm performance.

## 14.2 数据挖掘与机器学习项目方法论

1. CRISP-DM 1.0.
2. CRISP-ML(Q).
3. MLflow Documentation.
4. scikit-learn Documentation.

## 14.3 统计学习、因果推断与优化

1. James, G., Witten, D., Hastie, T., & Tibshirani, R. An Introduction to Statistical Learning.
2. Hastie, T., Tibshirani, R., & Friedman, J. The Elements of Statistical Learning.
3. Shmueli, G. To Explain or to Predict?
4. Hernán, M. A., & Robins, J. M. Causal Inference: What If.
5. Boyd, S., & Vandenberghe, L. Convex Optimization.

## 14.4 企业平台与产业实践

1. Palantir Foundry Documentation.
2. Palantir Ontology Documentation.
3. Palantir AIP Documentation.
4. Databricks Lakehouse Documentation.
5. Snowflake Cortex Documentation.
6. dbt Semantic Layer Documentation.
7. Power BI Documentation.
8. Celonis Process Mining Documentation.
9. NIST AI Risk Management Framework.
10. DAMA-DMBOK.

---

# 第十五部分 课程特色总结

本课程应形成三个核心特色。

## 15.1 数学性

课程以概率统计、统计学习、因果推断、优化和流程建模为基础，使学生理解管理决策背后的数学结构。

## 15.2 工程性

课程要求学生掌握数据库、SQL、Python、数据质量、MLOps、API、dashboard 和可复现实验环境，使学生理解数据分析如何进入企业系统。

## 15.3 前沿性

课程吸收 Palantir、Databricks、Snowflake、dbt、Celonis 等平台所代表的产业趋势，强调 ontology 化、scenario 化、agent 化、权限化、审计化和行动闭环。

最终，学生不只是会做一次性分析，而应能够理解并初步构建：

\[
\text{数据系统}
+
\text{分析模型}
+
\text{业务对象}
+
\text{管理行动}
+
\text{反馈治理}
=
\text{数智化企业运营决策系统}.
\]
