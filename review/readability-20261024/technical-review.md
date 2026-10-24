# 前两讲重写版技术复核

本报告区分源稿一致性、资料保留、导航有效性、修改范围与有限模型计算。自动验收可发现结构和算例错误，不能证明讲义论证充分、语言自然或模型适用于真实企业。

基线：`4836fc871718e417b2176f76080645a652bc928e`。本次自动验收：**通过**。

## 自动验收结果

### 01_intro

作者源一致：True；原正文锚点 214 个，丢失 0 个；失效或歧义链接 0 处。闭合 details 中的定义照常作为真实目标检查。

- pre：基线 1，当前 1；保留检查 True。
- math：基线 95，当前 100；保留检查 True。
- images：基线 1，当前 1；保留检查 True。
- citations：基线 15，当前 15；保留检查 True。

正文段落可见中文字符数（不计公式、代码、引用标记和来源标题）：{"count": 129, "min": 0, "median": 79, "p90": 120, "max": 191, "bins": {"0-30": 16, "31-60": 20, "61-120": 80, "121-180": 12, "181-220": 1, "221+": 0}}。

二、三级标题次序：

- 从经营变化到决策问题（`管理决策的研究对象`）
-   经营症状与管理选择（`数据分析与管理决策`）
-   怎样规定一次分析任务（`经营问题的定义`）
-   数据、统计与方案选择（`相关学科与研究对象`）
- 业务对象与评价指标（`决策系统的对象与层次`）
-   记录对象、行动对象与指标口径（`数据驱动决策的基本对象`）
- 订单交付任务的完整定义（`制造企业的交付延期风险分析`）
- 按期望损失比较行动（`管理决策问题的形式化表达`）
-   明确比较条件与基准（`行动方案的比较`）
-   状态、行动与条件期望损失（`状态行动与条件损失`）
- 检测信息的决策价值（`sec:information-value`）
-   检测之前怎样选择（`先验概率下的行动选择`）
-   根据检测结果调整行动（`贝叶斯更新与条件行动`）
-   计算检测的期望价值（`样本信息的期望价值`）
-   行动阈值与检测采购（`行动阈值与信息采购`）
- 多期决策与分析方法（`多期决策与分析任务`）
-   把未来成本计入当前选择（`多期决策的递推关系`）
-   区分描述、预测与干预评价（`五类分析任务的研究问题`）
-   经营信息系统支持哪些任务（`商业智能决策支持与决策智能`）
- 从分析任务到实际应用（`数据分析项目的组织`）
-   任务规定与实施检验（`从经营意图到可检验的实现`）
- 企业应用中的决策问题（`企业数据平台的应用`）
-   Airbus与Palantir：维护分析的数据整合（`airbus-与-palantir-的数据整合`）
-   Oracle与Red Bull Racing：比较比赛策略（`oracle-与-red-bull-racing-的赛事仿真`）
-   怎样计算人工智能应用的生产率（`人工智能应用的生产率测量`）
-   语言模型和智能体参与哪些工作（`人工智能工具与智能体`）
- 用程序保存问题定义（`问题定义的结构化表示`）
- 本章小结（`本章小结`）
-   文献导读（`文献导读`）
- 思考与习题（`思考与习题`）
- 注释（`01_intro-notes`）

词法强禁匹配与未覆盖资料：

```json
{
  "forbiddenPatterns": [],
  "longParagraphCandidates": [],
  "unresolvedMath": [],
  "lostAnchors": [],
  "linkErrors": []
}
```

### 02_enterprise_data_model

作者源一致：True；原正文锚点 315 个，丢失 0 个；失效或歧义链接 0 处。闭合 details 中的定义照常作为真实目标检查。

- pre：基线 1，当前 1；保留检查 True。
- math：基线 139，当前 152；保留检查 True。
- images：基线 5，当前 5；保留检查 True。
- citations：基线 45，当前 45；保留检查 True。

正文段落可见中文字符数（不计公式、代码、引用标记和来源标题）：{"count": 187, "min": 0, "median": 83, "p90": 127, "max": 188, "bins": {"0-30": 36, "31-60": 24, "61-120": 101, "121-180": 24, "181-220": 2, "221+": 0}}。

二、三级标题次序：

- 从订单问题到数据模型（`数据模型与组织管理`）
-   订单记录与共同定义（`数据建模的作用`）
- 业务对象与关系表达（`sec:objects-relations`）
-   完成事件、记录规则与测量（`从业务概念到可观察记录`）
-   实体、事件、状态与指标（`企业运营数据的基本语义`）
-   关系模型的基本语言（`关系模型的基本语言`）
-   键、外键与完整性约束（`键外键与完整性约束`）
-   订单、客户、产品与库存的 ER 模型（`订单客户产品与库存的-er-模型`）
-   半导体制造业务对象（`半导体制造业务对象`）
- 规范化、事实粒度与分析模型（`规范化与分析型数据模型`）
-   规范化与函数依赖（`规范化与函数依赖`）
-   关系分解与准确重建（`无损连接分解`）
-   事务型建模与分析型建模（`事务型建模与分析型建模`）
-   事实表粒度（`事实表粒度`）
-   制造指标的记录基础（`制造-kpi-的事实粒度`）
-   度量的可加性（`度量的可加性`）
- 历史记录与受控操作（`时间语义与对象操作`）
-   事件、状态与时间（`事件状态与时间`）
-   双时间与可追溯决策（`双时间与可追溯决策`）
-   从关联记录到行动对象（`从关系表到业务对象`）
-   对象操作与状态转换（`对象操作与状态转换`）
- 指标定义与查询语义（`指标定义与语义管理`）
-   指标字典与来源记录（`指标字典元数据与治理`）
-   从运营指标追踪相关对象（`制造运营的分析要素`）
-   自然语言问数的查询条件（`语义层与-ai-问数`）
- 数据治理与职责配置（`数据治理与职责配置`）
-   数据定义与监督责任（`数据模型的治理含义`）
-   定义、批准、执行与复核（`治理职责在数据模型中的表达`）
- 委托代理与绩效激励（`委托代理与绩效激励`）
-   绩效信号与风险承担（`指标测量与激励目标`）
-   合同如何影响努力（`代理人的努力选择`）
-   参与约束与企业的合同选择（`参与约束与最优激励强度`）
-   多任务配置与指标操纵（`多任务配置与指标操纵`）
- 对象和元数据的企业应用（`业务对象与元数据管理的企业应用`）
-   沿对象关系追踪停机影响（`palantir-ontology-的技术含义`）
-   Nasdaq的数据发现与分析时间（`atlan-与-nasdaq-的元数据管理`）
- 企业AI系统的实现与平台选择（`sec:enterprise-ai-stack`）
-   共享表数据与保持业务含义（`从存储格式到业务含义`）
-   模型调用与业务执行（`从推理服务到业务行动`）
-   按技术职责比较平台（`平台组合与采购对象`）
-   订单加急应用的两种实施路径（`封测企业的两种实施路径`）
- 零售与封测模型的综合复核（`建模实例与复核`）
-   零售订单数据模型（`零售订单数据模型`）
-   封测工厂的运营指标（`封测工厂的运营指标`）
-   用数据类表达逻辑模型（`配套程序`）
- 本章小结（`本章小结`）
-   文献导读（`文献导读`）
- 思考与习题（`思考与习题`）
- 注释（`02_enterprise_data_model-notes`）

词法强禁匹配与未覆盖资料：

```json
{
  "forbiddenPatterns": [],
  "longParagraphCandidates": [],
  "unresolvedMath": [],
  "lostAnchors": [],
  "linkErrors": []
}
```

修改范围：
```json
{
  "otherContentFilesUnchanged": 39,
  "changedBusinessCases": [
    "b01-01",
    "b01-02",
    "b01-03",
    "b01-04",
    "b01-05",
    "b02-01",
    "b02-02",
    "b02-03",
    "b02-04",
    "b02-05"
  ],
  "unchangedBusinessCases": 70,
  "changedCaseCards": [
    "airbus-skywise-maintenance",
    "oracle-red-bull-simulation",
    "palantir-ontology-lot",
    "atlan-nasdaq-catalog"
  ],
  "unchangedCaseCards": 11,
  "otherSlideDecksUnchanged": [
    "03_sql_kpi",
    "04_data_quality",
    "05_statistics_dashboard",
    "06_ab_testing",
    "07_prediction",
    "08_causality",
    "09_optimization",
    "10_process_mining",
    "11_modern_data_platform",
    "12_mlops",
    "13_ontology_action_scenario",
    "14_ai_agent",
    "final_project",
    "final_project_defense"
  ],
  "casebookUnrelatedArticleChanges": [],
  "caseProseForbiddenPatterns": []
}
```

源哈希核验：
```json
{
  "requiredSources": [
    "content-source/concept-links/knowledge.json",
    "content-source/readability-20261024/business-cases.json",
    "content-source/readability-20261024/case-cards.json",
    "content-source/readability-20261024/chapters/01_intro.json",
    "content-source/readability-20261024/chapters/02_enterprise_data_model.json",
    "content-source/readability-20261024/config.json"
  ],
  "mismatches": []
}
```

重复长句候选（仅提示人工检查，不以重复本身判错）：
```json
[]
```

## 有限决策算例与激励模型的独立核验

信息算例按四个“状态—信号”单元直接枚举联合概率，不复写讲义的后验概率公式。每个信号下，分别计算维持与转移的联合加权损失并取较小者。阳性列的最优贡献为 (26/5)，阴性列为 (4)，合计 (46/5=9.2)。事前最小损失为 (17)，故信息价值为 (39/5=7.8)。令两项行动损失相等，有 (100p=15+10p)，从而阈值为 (1/6)。

激励模型采用 (c,r,v>0)、(sigma^2ge0)、(e,etage0)，正态加性扰动与无额外固定工资下界。令 (Z=alpha+eta e-ce^2/2+etaarepsilon)。正态密度指数中的配方为

[
-retaarepsilon-rac{arepsilon^2}{2sigma^2}
=-rac{(arepsilon+retasigma^2)^2}{2sigma^2}
+rac{r^2eta^2sigma^2}{2}.
]

当 (sigma^2>0) 时，将平移后的正态密度积分为1，得到指数效用的期望；再按确定性等价的定义解出
[
operatorname{CE}=alpha+eta e-rac c2e^2-rac r2eta^2sigma^2.
]

零方差时随机项为零，得到同一公式。关于努力配方：
[
operatorname{CE}=alpha+rac{eta^2}{2c}-rac r2eta^2sigma^2
-rac c2left(e-rac{eta}{c}
ight)^2.
]

因为 (c>0)，经理的最优努力为 (e^*=eta/c)。参与约束取等号时，
[
alpha=ar u-rac{eta^2}{2c}+rac r2eta^2sigma^2,qquad
mathbb E[w]=ar u+rac{eta^2}{2c}+rac r2eta^2sigma^2.
]

设 (D=1+rcsigma^2>0)，将企业利润写成另一配方：
[
Pi(eta)=rac{veta}{c}-rac{Deta^2}{2c}-ar u
=rac{v^2}{2cD}-ar u-rac{D}{2c}left(eta-rac vD
ight)^2.
]

由 (D,c>0) 得到唯一最优激励 (eta^*=v/D)。在 (v=c=r=1) 时，(sigma^2=3) 与 (1) 分别给出 (1/4=0.25) 与 (1/2=0.5)。脚本以有理数系数的 Laurent 多项式逐项验证这些配方恒等式，并将最优努力及固定工资代回参与约束；这项核验说明代数关系一致，不证明现实中的噪声、效用、工资边界等假设成立。


精确算术与恒等式实际结果：
```json
{
  "passed": true,
  "checks": {
    "informationLoss": true,
    "EVSI": true,
    "threshold": true,
    "effortCompletingSquareIdentity": true,
    "bindingParticipationIdentity": true,
    "principalObjectiveIdentity": true,
    "optimalBetaCompletingSquareIdentity": true,
    "normalExponentialMomentIdentity": true,
    "betaSigmaSquared3": true,
    "betaSigmaSquared1": true,
    "twoPeriodMaintenanceEnumeration": true
  },
  "finiteDecision": {
    "priorBestLoss": "17",
    "signalPositiveJointLoss": "26/5",
    "signalNegativeJointLoss": "4",
    "informationLoss": "46/5",
    "EVSI": "39/5",
    "threshold": "1/6"
  },
  "twoPeriodMaintenance": {
    "withoutMaintenance": "20",
    "withMaintenance": "15"
  },
  "betaValues": {
    "sigmaSquared3": "1/4",
    "sigmaSquared1": "1/2"
  },
  "conditions": [
    "c>0",
    "r>0",
    "v>0",
    "sigmaSquared>=0",
    "e>=0 and beta>=0",
    "normal additive noise",
    "no extra lower bound on fixed wage",
    "principal compares expected profit"
  ],
  "interpretation": "Exact finite arithmetic and polynomial identities verify the displayed examples under their assumptions; they do not establish model applicability or pedagogical completeness."
}
```

## 交叉审查修订的复读

已依据 `cross-review-01`、`cross-review-02` 的关注点复读主线修订。

- 第一讲将订单决策限定为客户订单粒度及承诺交期前72小时；预测概率与行动效果分别说明，避免把风险排序直接作为加急排序。
- 维护比较分别处理维护消除风险与维护后存在残余风险的情形。后一情形比较维护费用加残余故障损失，与推迟维护的故障损失；停场和资源竞争费用计入相应行动。
- 新增两期维护例先规定第二期状态成本，再计算第一期两项行动的总期望成本。独立复算得到20与15，维护方案较优；该例与所述终止成本约定一致。
- 可积性、可测策略及有限状态情形的补充说明，与 Bellman 递推的概率和最优解条件配套。新增解释性建模说明区分研究目的与因果识别依据，没有将模型拟合本身当作机制成立的证明。
- 信息价值采用行动前计算的期望比较，应用后的经营改善另需实际行动、参照和结果记录。重复出现的表格分别承担分析定义与应用例示的功能，仍应结合课堂使用继续审阅其必要性。
- 第二讲的事件状态固定在事件发生时，后续活动另记事件；同一时点库存金额汇总要求币种与核算口径一致，数量汇总还要求单位和业务含义相容。
- 操纵分析段区分每次提交时分配的代理键与业务事件身份：新代理键只能区分记录，仍需根据业务事件唯一性及请求标识检查重复。相应说明已在作者源与发布正文中核对。

这些判断来自对相应新增段落的复读与有限算例复算，不由构建成功或文件哈希相同推出。


## 仍需人工判断的内容

手审应核对：概念首次出现是否得到解释；跨节过渡是否说明所回答的问题；案例事实、教学假设和推断是否分开；公式各符号的范围、单位和决策时点是否明确；经济模型中的正态扰动、风险厌恶、固定工资无额外下界和参与约束是否与结论配套。段落长度与词法扫描仅提供定位，不能评价解释是否充分，也不能代替逐段阅读。

数学保留检查忽略排版空格、定界符尺寸、对齐环境及结尾标点，检查完整公式或其在更长公式中的完整片段；无法覆盖的原式逐项列出。新增中间步骤并不自动证明旧条件得到保留。

## 错误与提醒

```json
{
  "errors": [],
  "warnings": []
}
```
