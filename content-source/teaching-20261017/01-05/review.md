# 第1—5讲幻灯片与真实案例审查

2026年10月17日。仅生成本目录内的可编辑来源；未直接修改共享dist或执行发布。

## 覆盖与保留

5讲原196页全部按原顺序保留，扩展为263页；新增17页概念桥接、25个案例共50页。37页原文在首次概念、定义精度和语序方面调整。原公式、代码、diagram、workedExample及原visual逐项一致；原正文行内TeX全部保留。

逐页复核标题、引入、正文、结论及延伸位置。新增案例第一页以机制流程承担结构，第二页解释判断、边界及思考题；每讲独立起算术语，未用章末术语表替代首次释义。

## 各讲教学逻辑

### 01_intro · 数据、信息与管理决策

新增两页区分数据仓库、ETL、OLAP和报表；在检测计算前解释先验、似然与后验；以目标约束、代理指标、可执行行动和跨期成本贯穿五个案例。保留原有损失矩阵、阈值推导、EVSI/EVPI、Bellman递推及全部算例。

现有50页，新增5例。

### 02_enterprise_data_model · 企业数据模型与治理机制

在首次讨论存储时解释快照、模式及表格式；在对象操作前解释状态机、版本核验与幂等；在激励推导前说明委托关系、风险与双方选择的先后顺序。五例分别展示身份范围、状态、空间粒度、元数据关系和责任关系。

现有47页，新增5例。

### 03_sql_kpi · 关系查询、指标计算与语义服务

开篇说明SQL、KPI、粒度与主键；连接前补足事实表、维度及引用完整性；条件聚合前解释NULL与三值逻辑。案例依次补充交易指标差别、定义版本、可合并状态、比率分母与来源时效。保留全部SQL注释、反例、OEE工时推导及队列计算。

现有52页，新增5例。

### 04_data_quality · 数据质量与证据可信度

以用途适配而非单一通过率解释质量；缺失偏差之前说明目标总体、期望、方差及协方差，回归衰减之前说明斜率与误差条件。案例区分恢复能力、模型输入风险、显式约束、分项评分与持续治理，避免把技术事故统称为错录。

现有55页，新增5例。

### 05_statistics_dashboard · 统计描述、过程波动与运营规律

开篇解释分位数、在制量、吞吐率和下钻；区分经验描述与未来推断；二项模型前说明相关缺陷与过度离散；排队模型前说明到达、服务、状态分布与记号。案例分别对应中心与尾部、结构标准化、平滑窗口、比较基准和异常响应。

现有59页，新增5例。

## 证据核验与解释边界

所有28个链接均在本轮通过网页检索或打开核验，限定企业官方披露、企业工程博客、企业作者论文及监管原文。不使用聚合转载、行业传闻、供应商演示数字或未经披露的内部KPI。未标发布日期的持续更新文档如实标记“未标注”；查阅日为2026-10-17。

新案例没有使用既有15张企业卡中的Skywise、Red Bull仿真、Palantir封测示例、Nasdaq、Snowflake/Genie、Froedtert、Assurance及Rolls-Royce等同一事实。

与其他讲次复用企业时按不同事实区分：UPS本讲专用2018年UPSNav的具体收货位置与执行界面，其他平台案例涉及更早路线平台；DataHub本讲分析对象身份、元数据实体和关系，平台讲次分析架构；Minerva本讲集中于指标定义版本及回填，平台讲次另论平台组合；Airbnb质量评分为2023年独立治理实践。Inditex、TSB与Knight Capital从本组移出，避免同一事件在不同讲次重复计数。

重要边界：CVS停售及Patagonia广告不能证明长期财务或环境净效应；Wells Fargo监管事实不能推及所有绩效工资；Unity年报并列两种产品问题，不把全部收入变化归因于单一客户数据；GitLab丢失部分数据库修改，不扩大为全部代码丢失；Deequ生产用途与论文的虚构业务演示分别说明；Citibank处罚涉及综合治理缺陷；Andon不等同于控制图；Prime Day总件数不是订单、顾客或促销净增量；各平台公开规则不自动证明客户实测收益。

|案例|企业|机制与分析位置|主要证据|
|---|---|---|---|
|b01-01|UPS|UPSNav：路线顺序如何成为可执行行动|[UPS](https://about.ups.com/us/en/newsroom/press-releases/innovation-driven/ups-deploys-purpose-built-navigation-for-ups-service-personnel.html)|
|b01-02|CVS Health|CVS停售烟草：企业目标如何界定行动集合|[CVS Health](https://www.cvshealth.com/campaigns/quitting-tobacco.html)；[CVS Caremark](https://www.cvs.com/bizcontent/minuteclinic/desktop/pressreleases/020514-stop-tobacco.pdf)|
|b01-03|Wells Fargo|Wells Fargo：开户数量为何偏离客户价值|[Consumer Financial Protection Bureau](https://www.consumerfinance.gov/archive/newsroom/consumer-financial-protection-bureau-fines-wells-fargo-100-million-widespread-illegal-practice-secretly-opening-unauthorized-accounts/)；[Wells Fargo / SEC EDGAR](https://www.sec.gov/Archives/edgar/data/72971/000119312517065587/d344612ddefa14a.htm)|
|b01-04|Patagonia|Patagonia：产品销售与资源消耗的跨期权衡|[Patagonia](https://www.patagonia.com/stories/planet/activism/dont-buy-this-jacket-black-friday-and-the-new-york-times/story-18615.html)|
|b01-05|Amazon|Amazon：可逆性改变信息等待的代价|[Amazon](https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders)|
|b02-01|Shopify|Shopify：数字编号相同，对象未必相同|[Shopify](https://shopify.dev/docs/api/usage/gids)|
|b02-02|Stripe|Stripe PaymentIntent：支付不是一个成功布尔值|[Stripe](https://docs.stripe.com/payments/paymentintents/lifecycle)|
|b02-03|Uber|Uber H3：地理汇总先确定空间单位|[Uber Engineering](https://www.uber.com/us/en/blog/h3/)|
|b02-04|LinkedIn|LinkedIn DataHub：数据集之外还要记录关系|[LinkedIn Engineering](https://www.linkedin.com/blog/engineering/archive/data-hub)|
|b02-05|Spotify|Spotify Backstage：服务身份与责任归属|[Spotify Engineering](https://engineering.atspotify.com/2020/3/what-the-heck-is-backstage-anyway)|
|b03-01|Airbnb|Airbnb Minerva：定义变化后，历史应怎样比较|[Airbnb Engineering](https://medium.com/airbnb-engineering/how-airbnb-achieved-metric-consistency-at-scale-f23cc53dea70)|
|b03-02|Uber|Uber uMetric：实时与离线为何算出不同结果|[Uber Engineering](https://www.uber.com/qa/en/blog/umetric/)|
|b03-03|DoorDash|DoorDash Curie：为何保留事件级事实|[DoorDash Engineering](https://careersatdoordash.com/blog/using-metrics-layer-to-standardize-and-scale-experimentation-at-doordash-2/)|
|b03-04|Spotify|Spotify streamshare：播放量不是统一单价|[Spotify for Artists](https://artists.spotify.com/en/royalties-guide)|
|b03-05|Shopify|Shopify GMV：交易规模与平台收入|[Shopify](https://www.shopify.com/news/shopify-announces-fourth-quarter-and-full-year-2023-financial-results)|
|b04-01|GitLab|GitLab数据库事件：备份存在不等于能够恢复|[GitLab](https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/)|
|b04-02|Unity Software|Unity：错误数据如何进入模型反馈|[Unity Software / SEC EDGAR](https://www.sec.gov/Archives/edgar/data/1810806/000181080623000016/unity-20221231.htm)|
|b04-03|Amazon|Amazon Deequ：把数据假设写成可检验约束|[Amazon Research / ACM SIGMOD](https://assets.amazon.science/12/62/7a066bf44199afea06ec73f23ad0/unit-testing-data-with-deequ.pdf)|
|b04-04|Airbnb|Airbnb质量评分：总分如何保留解释性|[Airbnb Engineering](https://medium.com/airbnb-engineering/data-quality-score-the-next-chapter-of-data-quality-at-airbnb-851dccda19c3)|
|b04-05|Citibank|Citibank监管整改：数据治理是持续责任|[Office of the Comptroller of the Currency](https://www.occ.gov/news-issuances/news-releases/2020/nr-occ-2020-132.html)|
|b05-01|Netflix|Netflix ISP指数：先固定观看结构再比较网络|[Netflix](https://ispspeedindex.netflix.net/about/)|
|b05-02|Google|Google SRE：平均时延为什么不够|[Google SRE](https://sre.google/sre-book/monitoring-distributed-systems/)；[Google SRE](https://sre.google/sre-book/service-level-objectives/)|
|b05-03|Toyota|Toyota Andon：可视化信号需要处置责任|[Toyota Motor Corporation](https://global.toyota/en/company/vision-and-philosophy/production-system/)|
|b05-04|Amazon|Prime Day：活动高峰如何影响经营摘要|[Amazon](https://www.aboutamazon.com/news/retail/amazon-prime-day-2023-stats)|
|b05-05|McDonald’s|McDonald’s：同店销售增长不等于客流增长|[McDonald’s / SEC EDGAR](https://www.sec.gov/Archives/edgar/data/63908/000006390824000072/mcd-20231231.htm)|

## 首次术语释义位置

下表只索引本讲实际出现且有必要解释的术语。完整简释、同义称呼和起算讲次见term-audit.json。definitionSlideTitle不晚于firstSlideTitle；正文中的简释可直接阅读，延伸锚点仅用于查阅更完整推导。

|讲次|术语|首次页|解释所在页标题|
|---|---|---:|---|
|1|数据仓库|6|数据仓库与ETL：形成分析资料|
|1|ETL|6|数据仓库与ETL：形成分析资料|
|1|OLAP|7|OLAP与报表：两种阅读数据的方式|
|1|报表系统|7|OLAP与报表：两种阅读数据的方式|
|1|维度|7|OLAP与报表：两种阅读数据的方式|
|1|BI|8|商业智能、决策支持与决策智能|
|1|DSS|8|商业智能、决策支持与决策智能|
|1|KPI|9|对象、行动范围与指标口径|
|1|代理指标|10|Wells Fargo：开户数量为何偏离客户价值|
|1|潜在结果|15|条件期望损失与行动选择|
|1|损失函数|15|条件期望损失与行动选择|
|1|条件期望|15|条件期望损失与行动选择|
|1|封测|20|以损失矩阵评价信息|
|1|先验|22|先验、信号与后验|
|1|似然|22|先验、信号与后验|
|1|后验|22|先验、信号与后验|
|1|贝叶斯公式|22|先验、信号与后验|
|1|EVSI|28|样本信息价值与完全信息价值|
|1|EVPI|28|样本信息价值与完全信息价值|
|1|马尔可夫性质|37|Bellman 递推：从未来回到当前|
|1|CRISP-DM|41|CRISP-DM：组织可检验的迭代|
|1|OCI|46|赛事仿真：比较候选策略|
|1|校准|46|赛事仿真：比较候选策略|
|1|蒙特卡罗|47|用蒙特卡罗估计策略损失|
|1|AI|49|生产率改善须固定分母与质量|
|1|SKU|50|检验一个决策任务是否完整|
|2|CRM|1|统一身份与业务含义|
|2|主键|2|数据模型与治理责任|
|2|事实粒度|2|数据模型与治理责任|
|2|数据血缘|2|数据模型与治理责任|
|2|元数据|2|数据模型与治理责任|
|2|AI|5|企业 AI 系统的六项职能|
|2|快照|6|快照、模式与表格式|
|2|模式|6|快照、模式与表格式|
|2|模式演化|6|快照、模式与表格式|
|2|开放表格式|6|快照、模式与表格式|
|2|对象存储|6|快照、模式与表格式|
|2|设备综合效率|7|存储、语义与权限|
|2|实体|9|企业数据的六类语义|
|2|超键|11|键与三类完整性约束|
|2|候选键|11|键与三类完整性约束|
|2|自然键|11|键与三类完整性约束|
|2|代理键|11|键与三类完整性约束|
|2|外键|11|键与三类完整性约束|
|2|ER|14|关系基数与模型层次|
|2|函数依赖|16|函数依赖与第三范式|
|2|第三范式|16|函数依赖与第三范式|
|2|事实表|19|事务模型与星型模型|
|2|维度|19|事务模型与星型模型|
|2|KPI|24|制造 KPI 的事实基础|
|2|CT|23|制造指标先固定测量对象|
|2|WIP|23|制造指标先固定测量对象|
|2|OTD|9|企业数据的六类语义|
|2|状态机|27|状态机与幂等请求|
|2|幂等请求|27|状态机与幂等请求|
|2|语义层|31|语义层约束自然语言问数|
|2|委托人|32|绩效合同：为何要同时考虑努力与风险|
|2|代理人|32|绩效合同：为何要同时考虑努力与风险|
|2|风险厌恶|32|绩效合同：为何要同时考虑努力与风险|
|2|CE|34|产出信号、合同与风险成本|
|2|Ontology|42|对象关系与元数据目录|
|3|SQL|1|查询正确性与业务语义|
|3|粒度|1|查询正确性与业务语义|
|3|主键|1|查询正确性与业务语义|
|3|KPI|1|查询正确性与业务语义|
|3|统计状态|2|SQL 的逻辑处理顺序|
|3|关系代数|6|关系运算与事实集合|
|3|多重集|8|SQL 的重复行语义|
|3|GMV|10|Shopify GMV：交易规模与平台收入|
|3|GPV|10|Shopify GMV：交易规模与平台收入|
|3|MRR|10|Shopify GMV：交易规模与平台收入|
|3|事实表|12|事实表与维度表|
|3|维度表|12|事实表与维度表|
|3|外键|4|区域收入查询：逐层核查|
|3|引用完整性|12|事实表与维度表|
|3|半连接|15|半连接：只判断是否存在匹配|
|3|OTD|16|指标定义的形式化表示|
|3|CT|24|良率与周期的权重|
|3|OEE|25|OEE 的分解与约分|
|3|WIP|29|WIP 的时点与时间平均|
|3|NULL|34|NULL、三值逻辑与条件聚合|
|3|三值逻辑|34|NULL、三值逻辑与条件聚合|
|3|变形测试|48|结果验证与不变量|
|3|参数绑定|49|受限执行与独立授权|
|3|KV|51|本地部署：位置与资源边界|
|4|OTD|1|数据质量：从记录条件到决策证据|
|4|数据质量|1|数据质量：从记录条件到决策证据|
|4|数据血缘|5|数据生成环节与质量风险|
|4|数据剖析|13|数据剖析与规则检验|
|4|枚举|9|质量维度：覆盖、取值与关系|
|4|期望|14|观察总体、记录概率与协方差|
|4|方差|14|观察总体、记录概率与协方差|
|4|协方差|14|观察总体、记录概率与协方差|
|4|MCAR|17|缺失机制与可用识别条件|
|4|MAR|17|缺失机制与可用识别条件|
|4|MNAR|17|缺失机制与可用识别条件|
|4|回归|19|回归斜率与测量误差|
|4|测量误差|1|数据质量：从记录条件到决策证据|
|4|经典误差模型|19|回归斜率与测量误差|
|4|识别区间|22|缺失结果的部分识别|
|4|置信区间|22|缺失结果的部分识别|
|4|元数据|28|质量规则与失败行标识|
|4|数据契约|42|数据契约、血缘与变更控制|
|4|数据可观测性|48|Assurance 案例：持续质量监测|
|4|MTTD|49|质量事件持续时间与损失|
|4|MTTR|49|质量事件持续时间与损失|
|4|RAG|51|检索增强生成的证据质量|
|4|哈希|51|检索增强生成的证据质量|
|5|ISP|18|Netflix ISP指数：先固定观看结构再比较网络|
|5|SRE|7|Google SRE：平均时延为什么不够|
|5|均值|1|描述统计与运营解释|
|5|分位数|1|描述统计与运营解释|
|5|在制量|1|描述统计与运营解释|
|5|吞吐率|1|描述统计与运营解释|
|5|下钻|1|描述统计与运营解释|
|5|经验分布|3|样本描述与总体推断|
|5|独立同分布|3|样本描述与总体推断|
|5|中位数|3|样本描述与总体推断|
|5|标准差|10|离散程度与相对波动|
|5|CV|10|离散程度与相对波动|
|5|IQR|11|四分位距与描述性异常|
|5|移动平均|20|后向移动平均与原始时间序列|
|5|二项分布|23|二项模型与过程波动|
|5|过度离散|23|二项模型与过程波动|
|5|控制界限|23|二项模型与过程波动|
|5|泊松|33|Little 定律的面积论证|
|5|M/M/1|35|到达、服务与排队模型记号|
|5|GI/G/1|35|到达、服务与排队模型记号|
|5|利用率|36|单服务台模型中的利用率与等待|
|5|稳态|35|到达、服务与排队模型记号|
|5|TTFT|44|人工智能服务的测量边界|
|5|token|45|无排队服务时间的构成|
|5|OTD|53|制造看板的五种测量对象|
|5|OEE|53|制造看板的五种测量对象|

## 本组验证

validation.json记录页数、案例数、来源URL数和原内容保护检查。全部263页的讲义延伸锚点有效，行内TeX初步试渲染965处通过。新增页使用既有flow/cards/compare或课堂思考组件，单页最多一个支持组件；未引入新的样式或运行依赖。完整桌面/移动端渲染与宋体字形覆盖由主任务集成后验收，本组不将未执行的浏览器检查称为通过。
