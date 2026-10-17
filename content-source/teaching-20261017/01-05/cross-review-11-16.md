# 第11—16讲独立抽查

查阅日期：2026-10-17。只读核查11-16目录的最终decks.json、cases.json与term-audit.json；未修改被审内容。抽查9例，覆盖每讲至少1例；未重复核查TSB、Knight Capital或S3。另检查第11—13讲主要概念页、第14讲前置定义与GraphRAG、第15—16讲项目方法页。结论限于本次抽样，不代表30例或170页已由本审查者全部逐项核验。

## 需修正的中等问题

### M13被表述成了不同的要素体系

位置：`13_ontology_action_scenario`第16页“运营要素把异常转化为可核查的问题”。当前正文以“人员、设备、物料、方法、测量、环境”等要素解释M13，实际接近6M分类。

课程现行资料`docs/cases/semiconductor_kpi_m13_case.md`第71、80行明确M13按需求、产品、工艺路线、设备、产能、质量和交付等运营要素组织调查。`docs/course_upgrade_plan.md`第78—94行的教学抽象版列出需求、产品、路线、批次、设备、产能、在制品、质量、维护、物料、交付、成本、行动13项。当前幻灯片未按该口径解释，独立阅读者还无法知道M13名称的来源和13项范围。

建议：首次说明“M13是制造运营要素分类”，按上述现行13项分组呈现或准确概括，并明确其为调查组织框架；保留“关联不构成因果证据”的限定。不得把待企业导师确认的教学分类表述为已经获得企业认证的行业标准。term-audit中的简释及实际正文应保持一致。

未发现严重事实错误。9项案例核验及其证据边界未形成需要阻断发布的问题。

## 9例一手来源核验

|讲次与位置|案例|一手证据与核验结果|分析边界|
|---|---|---|---|
|11，第4页，b11-03|Shopify CDC|[Shopify Engineering](https://shopify.engineering/capturing-every-change-shopify-sharded-monolith)，2021-03-12。明确从查询式Longboat迁向日志CDC，并采用Kafka Connect与Debezium；还说明硬删除、中间状态和初始快照的限制。真实迁移行动有据。|正文未保证任意数据库适用或端到端恰好一次效果，边界适当。|
|12，第10页，b12-03|DoorDash Sibyl|[DoorDash Engineering](https://careersatdoordash.com/blog/doordashs-new-prediction-service/)，2020-06-29。实际搜索请求异步调用Sibyl做负载测试，返回结果未用于排序；随后先迁移延迟要求较宽松的反欺诈和配送员报酬模型。|把影子运行解释为承载和输出检验，没有据此宣称客户体验获得因果改善，合理。|
|12，第16页，b12-05|Stripe Radar|[Stripe Engineering](https://stripe.dev/blog/how-we-built-it-stripe-radar)，2023-03-29。明确2022年中从树模型加深度网络的组合转向纯深度网络，也讨论训练效率与误拒等约束。|标签延迟与评价安排被标为分析要求；没有照搬未独立验证的效果数字。|
|13，第13页，b13-02|Unilever Indaiatuba|[Unilever](https://www.unilever.com/news/news-search/2023/unilever-sites-join-network-of-worlds-most-digitally-advanced-factories/)，2023。说明巴西洗衣粉工厂利用机器学习数字孪生预测新配方的过程参数，并有员工训练背景。实际应用有据。|没有把宣传中的节能、效率变化全部归因于单一数字孪生。流程图最后的“试验确认”建议再作精确化，见下文。|
|14，第12页，b14-01|Morgan Stanley内部知识服务|[Morgan Stanley](https://www.morganstanley.com/press-releases/key-milestone-in-innovation-journey-with-openai)，2023-03-14。公告确有面向顾问开发内部服务、答案来自自有内容并附原始文档链接的设计。|使用“宣布开发”而未把当时公告写成已全面部署；保留顾问责任和引用仍需核查的条件。|
|14，第21页，b14-02|Box Gizmo|[Box IT](https://blog.box.com/building-closed-loop-knowledge-system-ai-powered-it-support-box)，2026-07-02。正文确有Slack入口、经治理知识的检索资格、每七日对未解决及负面反馈请求进行缺口分析，修订建议经团队审查再走发布程序。|没有把模型建议直接称为正式制度，也未捏造净收益；本例对闭环知识治理的解释具体且一致。|
|15，综合项目第11页，b15-05|BMW AIQX|[BMW Group](https://www.bmwgroup.com/en/news/general/2023/BMWGroupIT.html)，2023-01-29。确有产线相机、实时车辆定位触发拍摄、云端深度学习分析。|将端到端验收作为课程分析，没有推定BMW内部阈值、错误率或最终放行程序。|
|16，综合项目第35—36页，b16-01|Zillow Offers|[Zillow Group](https://investors.zillowgroup.com/news-and-events/news/news-details/2021/Zillow-Group-Reports-Third-Quarter-2021-Financial-Results--Shares-Plan-to-Wind-Down-Zillow-Offers-Operations/default.aspx)，2021-11-02。公告明确结束Offers，管理层提及房价预测不可预见性、损益及资产负债表波动；同份财报也说明整修与转售能力约束。|没有把全部损失归于单一算法，也未推出所有自动估价业务均不可行；将预测和运营容量共同纳入规模判断，逻辑完整。|
|16，综合项目第30—31页，b16-04|Microsoft Tay|[Microsoft](https://blogs.microsoft.com/blog/2016/03/25/learning-tays-introduction/)，2016-03-25。明确上线前过滤和测试、上线后协同攻击利用疏漏、产生不当内容、暂停及重新开放的条件。|未误称为现代RAG文档注入，也没有编造训练或权限机制；对抗测试与暂停条件属于明确标识的方案分析。|

## 关键定义与推理检查

- 第11讲区分事务系统、仓库、湖和湖仓；ETL/ELT按转换位置解释，未把架构名称当作质量保证。快照可复现分析与业务补偿分开，符合概念边界。
- 第12讲把部署、推理、特征和标签区别开；影子运行与灰度发布是否改变实际行动的区别明确。灰度比例不被误认为随机分配，数据漂移与条件关系漂移也分别说明证据要求。
- 第13讲的关系有效期、前置/后置条件、不变量和幂等处理有具体失败情形支撑；实际状态与情景假设分开。需要修正的M13问题如上。
- 第14讲工具、技能、记忆及运行控制的职责能够衔接；RAG中的相关性与事实支持、权限分别说明。GraphRAG写成可利用关系和社区摘要的方法，没有声称社区汇总是所有图检索实现的必要条件。
- 第15—16讲将原型、概念验证、影子运行、真实试点区分，并要求基线及实际风险边界；退出、回滚与已发生业务后果没有混为一谈。

## 轻微表述建议

1. 第13讲Unilever流程图的末节点“试验确认”容易被当成该企业实际采用物理试验的事实，但原文对该用途称数字孪生免去了物理试验。建议改成“适用性与质量核验”，或将整个图明确标为“参数建议的可行性核查”。企业已披露过程与一般验证要求宜继续区分。
2. 第11讲“自然语言问数（NL2SQL）”可更精确地写成“自然语言转SQL（NL2SQL）”；自然语言问数产品还可能采用其他检索或查询路径。
3. 个别边界仍有“本课不把企业宣传概括为……”和“本课不推定……”等自指表达。可直接改成“材料未给出……，因此不能确定……”。这是正式语言修饰，不改变事实判断，也不需要删除必要的证据限制。
