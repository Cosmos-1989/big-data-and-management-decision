# 第6–10讲幻灯片审校与新增案例记录

基准为网站提交 `2fde9b0`。已使用 humanizer 完整阅读五讲原有207页，保留原页标题与顺序、全部显示公式和行内数学序列、数值算例、代码、图解及讲义延伸锚点。针对首次概念、定义与假设之间的衔接作40次正文修订；新增22页概念桥接和50页案例阐释，五讲合计279页。

每例两页分别说明业务背景与实施事实、课程分析与证据限制；第一页的流程图表现业务机制，第二页的对照图表现比较依据。未采用企业宣传中的收益数值，未将相关关系、离线精度或平台部署事实写成已识别净收益。新页均标记compact，实际逐页渲染由主代理统一完成。

## 逐讲范围

|讲次|原页数|现页数|新增真实案例|首用释义项目|重点修订|
|---|---:|---:|---:|---:|---|
|6|44|58|5|23|随机实验、潜在结果、标准误、区间、功效与序贯监测；分别解释随机单元、重复分配和推广价值。|
|7|39|55|5|36|标签时点、泄漏、损失、正则化、概率校准与共形预测；区分预测对象、概率分布和决策。|
|8|42|57|5|29|反事实、识别、混杂、标准化、IPW/AIPW、DID与工具变量；明确估计参数及外推人群。|
|9|37|50|5|19|变量与可行域、硬约束、对偶与界、尾部风险及排程；区分可行方案、软偏好和已证最优。|
|10|45|59|5|30|实例、事件、轨迹、DFG、Petri网与对象关联；区分过程线索、合规判断和执行确认。|

## 首用解释

137个释义项目均在其首次可见出现页的正文中解释，或由此前的概念页解释。核对title、lead、body、points、takeaway、visual、diagram、workedExample、prompts，排除来源与讲义导航元数据；首用晚释义为0。`term-audit.json`逐项保存首用页和定义页，正文不依赖末尾词汇表。

新释义的二次审查修正了三处易误解之处：实验单元不要求分配指示变量彼此独立；中心极限定理陈述为独立同分布、有限正方差下的极限结果，并另说有限样本近似；共形保证为可交换等条件下的边际覆盖，不是逐特征条件覆盖。

## 真实案例与来源

|编号|企业与独立事实|一手来源|证据边界|
|---|---|---|---|
|b06-01|Netflix：同一影片的封面应如何比较|[Netflix Technology Blog](https://netflixtechblog.com/artwork-personalization-c589f074ad76)|文章说明当时的系统和研究过程，未公开可重算的完整实验资料；不把企业报告的改善直接外推到其他内容平台，也不据此宣称单张图片对某个会员的个体效应。|
|b06-02|Airbnb：房源实验为何受到邻近房源影响|[Management Science](https://pubsonline.informs.org/doi/10.1287/mnsc.2020.01157)|证据针对特定平台费用变化和集群构造；不能推定任何房源实验都具有相同偏差，也不能认为集群随机化已经消除所有干扰。应分别审查地域边界与集群间联系。|
|b06-03|Booking.com：实验记录为什么要保存失败结果|[Booking.com authors / arXiv](https://arxiv.org/abs/1710.08217)|论文描述组织和平台机制，不提供“建立知识库必然提高利润”的独立因果识别。不同版本、受众和时期的实验不能仅凭名称合并，更不能把不显著结果解释为严格零效应。|
|b06-04|Uber：结果显著之前先检查实验是否按计划运行|[Uber Engineering](https://www.uber.com/us/en/blog/xp/)|这是企业对当时平台的技术说明，不能证明所有实验完全避免故障。观察到跨版本对象后是否排除，必须依预先规则和研究目标判断，选择性删除会另生偏差。|
|b06-05|DoorDash：调度实验按地区和时间切换|[DoorDash Engineering](https://careersatdoordash.com/blog/switchback-tests-and-randomized-experimentation-under-network-effects-at-doordash/)|方法不能自动消除相邻窗口残留、跨区调度和共同时间冲击；清洗长度、分层与方差估计需结合具体运行机制。此处不引用厂商宣传中的实验增速作为业务净收益。|
|b07-01|Amazon：补货为何需要需求分布|[Amazon Science / VLDB](https://www.amazon.science/publications/probabilistic-demand-forecasting-at-scale)|论文说明平台架构及预测工作，不公开所有商品的商业决策规则。课程中的成本映射是方法分析，不能宣称企业采用某一固定分位数，也不能凭预测改进推定利润增量。|
|b07-02|Uber DeepETA：在道路模型上预测残差|[Uber Engineering](https://www.uber.com/us/en/blog/deepeta-how-uber-predicts-arrival-times/)|这是已部署系统的设计说明；公开资料不支持还原全部数据或认定相同架构在任意城市都更优。到达时间预测本身也不证明改变匹配规则会改善全网结果。|
|b07-03|DoorDash：把配送预测与承诺决策分开|[DoorDash Engineering](https://careersatdoordash.com/blog/improving-etas-with-multi-task-models-deep-learning-and-probabilistic-forecasts/)|公开文章介绍概率系统，并未声称采用本课后续的共形方法；二者的联系在于都要求说明不确定性。展示区间不自动具有给定频率覆盖保证，需核验其构造与数据条件。|
|b07-04|Netflix：评分预测为何不足以设计首页|[Netflix Technology Blog](https://netflixtechblog.com/learning-a-personalized-homepage-aa8ec670359a)|文章描述特定时期的推荐系统，没有给出所有模型的通用优劣排序。本例不把首页设计写成单一预测问题，也不把企业模型演进解释为某个算法已具有普遍因果优势。|
|b07-05|Google Maps：道路相互连接怎样影响预测|[Google DeepMind](https://deepmind.google/blog/traffic-prediction-with-advanced-graph-neural-networks/)|公开材料支持当时的系统机制，不提供跨全部城市的统一改善保证。交通模式突变时仍需监测漂移，即输入分布或输入与结果关系的变化；道路预测准确也不等于任意导航策略的整体交通效应已被识别。|
|b08-01|eBay：搜索广告转化与增量购买|[NBER / eBay Research collaborators](https://www.nber.org/papers/w20171)|实验结论针对当时 eBay 的搜索广告、用户与窗口；“短期未测得效益”不等于所有品牌广告长期无效。课程未将该研究的回报数值外推至其他企业。|
|b08-02|Uber：不同促销需要比较净增量价值|[Uber authors / IEEE DSAA](https://arxiv.org/abs/1908.05372)|论文中的真实实验和模拟结果需要分别阅读，不能把算法在模拟中的排名称为生产收益。个体预测分数不等于已观察的个体真实因果效应；未来分配仍需重叠、目标人群与费用条件适用。|
|b08-03|Google：广告效果可以在地区层面识别|[Google Research](https://research.google/pubs/measuring-ad-effectiveness-using-geo-experiments/)|研究描述一类设计，未表明所有广告都能形成足够多且互不干扰的地区。边界购买、全国媒体及同期政策可能破坏比较；观测地理相关本身不等于已实施随机地理实验。|
|b08-04|Facebook：丰富特征能否代替随机比较|[Marketing Science](https://pubsonline.informs.org/doi/abs/10.1287/mksc.2018.1135)|结论针对论文中的广告研究，不证明任何观测方法在任何场景都失败。随机实验也须核验分配、干扰和缺失；本例支持审查识别依据，不能据此给所有方法排一个普遍名次。|
|b08-05|Tripadvisor：会员注册便利化与实际采用|[Microsoft Research / TripAdvisor](https://www.microsoft.com/en-us/research/group/alice/case-study/)|官方案例报告会员作用随用户特征而异，未公开可重算的全部原始记录。注册流程若直接改变访问体验，排除限制便需另行论证；不能把所估局部效果无条件解释为强制所有人注册的效果。|
|b09-01|Zara：有限库存怎样分给不同门店|[Operations Research](https://pubsonline.informs.org/doi/10.1287/opre.1090.0698)|事实来自特定历史项目，不能将其模型视为 Zara 当前全部库存技术。论文销量结果有明确试点背景；此处不把其历史收益数字当作其他零售商可直接获得的收益。|
|b09-02|Google：冷却优化为何需要双层约束核验|[Google DeepMind](https://deepmind.google/blog/safety-first-ai-for-autonomous-data-centre-cooling-and-industrial-control/)|公开节能数据来自企业报告，缺少本课可重算的全部比较资料。案例证明企业采用了约束和接管机制，并不证明某一约束集覆盖所有故障，也不代表预测模型自身能够保证安全。|
|b09-03|Lufthansa：模拟机排程中的硬条件与偏好|[Gurobi customer case](https://www.gurobi.com/resources/case-studies/lufthansa-flight-training-gmbh)|来源为供应商客户案例，涉及历史业务和系统。文中的具体休息时间属于该案例条件，不是所有航空训练通用法规；高质量可行解也不能一概称作已经证明的全局最优解。|
|b09-04|Walmart：运输优化同时决定路线与装载|[Walmart](https://corporate.walmart.com/news/2024/03/14/walmart-commerce-technologies-launches-ai-powered-logistics-product)|新闻稿中的总体节约属于企业自报，不能据此识别每项功能的独立效果。本例说明建模关系，不还原 Walmart 的私有目标权重、求解器或全部运营约束。|
|b09-05|Uber：一次派单也会改变下一时段的供需|[Uber Engineering](https://www.uber.com/us/en/blog/reinforcement-learning-for-modeling-marketplace-balance/)|企业文章不公开所有策略及长期效果的独立识别资料。价值模型依赖状态和训练资料，未来市场变化可使估计失准；单次离线预测改进不能直接证明动态匹配策略优于现行规则。|
|b10-01|Vodafone：采购流程图与实际路径的差距|[Celonis customer case](https://www.celonis.com/solutions/stories/vodafone-transparency-process-mining)|来源为供应商客户案例，支持实践用途，不构成可独立重算的净效果识别。公开数字的币种、期间与单位还需逐项核对，课程不采用其中含混数量作绩效证据。|
|b10-02|DHL：人事工单结束，财务付款是否也已结束|[Celonis / DHL Group customer case](https://www.celonis.com/solutions/stories/dhl-group)|来源为供应商客户叙述，其累计节约不直接等于单一自动化的因果收益。课程只讨论公开的问题和对象关系，不推定所有持续支付都属违规，也不披露或重构个人数据。|
|b10-03|Deutsche Telekom：付款更早并不总是更好|[Celonis / Deutsche Telekom customer case](https://www.celonis.com/solutions/stories/deutsche-telekom-procure-to-pay-process-mining)|来源为供应商客户案例，所述节约为企业报告而非本课独立识别。本例不把越快付款视为普遍目标，也不把相同金额和供应商直接视为重复付款的充分证据。|
|b10-04|ABB：跨业务流程需要共同语义|[Celonis / ABB customer account](https://www.celonis.com/blog/abb-and-celonis-the-art-of-co-innovation)|材料支持企业实践范围，不能证明不同部门已天然可比；提到运输排放分析也不等于所有供应链排放已完整覆盖。课程不以厂商评价替代模型边界和数据完整性的核验。|
|b10-05|Stripe：超时重试怎样避免重复业务影响|[Stripe Engineering](https://stripe.com/blog/idempotency)|具体接口的保存期限、错误处理和并发语义以当期文档为准。幂等键不自动使所有外部系统操作具有一次且仅一次保证；跨服务的业务验收仍要检查最终状态和相关事件。|

## 去重与资格核验

与既有15张企业案例卡逐项对照，新增案例均为不同的具名企业实践或企业参与的实际研究。第7讲未采用Zillow Offers退出，避免与主代理第16讲相同事件重复；第9讲未采用UPS ORION，而采用Zara历史库存配送优化，与第1讲Inditex RFID盘点不同。Stripe幂等恢复与第2讲PaymentIntent对象生命周期也是不同机制。

第8讲初选的Uber Eats配送延迟因果图和Booking.com自愿采用文章含说明性情境，未据此充当两项实际落地案例。最终替换为Uber作者论文中真实多促销实验与生产实现，以及Tripadvisor和Microsoft实际合作的会员便捷注册实验。25例各有明确实施依据。

Vodafone原文直接列有采购订单/收货/发票的三单匹配及跳过批准步骤；Netflix封面案例明确观看参与质量是原文结果标签，未虚构统一判定阈值。

## 校验与待完成项

- `content-check.json`：5讲、279页、25例、137个释义，首用晚释义0；原数学/图解/代码/锚点保护断言通过。
- `formula-check.json`：1005次数学排版检查，无KaTeX解析错误。
- `sources-verified.json`：25个一手来源的支持事实与限制；未知发布日期保留null，未编造日期。
- NBER的open遇403，依据同站搜索返回的完整作者摘要核验；MSR页面open暂时失败，官方搜索返回完整案例正文，已核验。其他来源均读到正文、出版社摘要或企业作者原论文。
- 仍需主代理合并后统一逐页视觉检查、移动端交互检查、发布和线上核验；本子任务未改dist或共享构建代码，未执行发布。
