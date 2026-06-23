# Sample Data

本目录用于放置课程样例企业运营数据：

- `orders.csv`
- `customers.csv`
- `products.csv`
- `inventory.csv`
- `suppliers.csv`
- `logistics.csv`
- `event_log.csv`

当前已提供第 3 周 SQL/KPI 实验所需的最小样例数据：

- `customers.csv`: 客户维度，粒度为一行一个客户。
- `products.csv`: 产品维度，粒度为一行一个产品，包含标准售价与单位成本。
- `orders.csv`: 订单事实，粒度为一行一个订单。
- `inventory.csv`: 库存快照，粒度为一行一个产品、仓库、快照日期。

第 3 周代码使用这些表计算销售额、毛利、毛利率、准时交付率、延期天数和滚动收入。

第 4 周新增 `orders_quality_issues.csv`，用于数据质量实验。该文件故意包含重复主键、缺失外键、非法枚举、非正数量、日期顺序错误和缺失实际交付日期等问题。

第 5 周新增 `daily_operations.csv`，用于描述统计与 dashboard 实验。该文件的粒度为一行一个经营日期，包含收入、订单数、准时订单数、平均延期天数、待处理订单数和质量问题数。

第 6 周新增 `ab_test_checkout.csv`，用于统计推断与 A/B 测试实验。该文件的粒度为一行一个被随机分配的访客，包含实验组别、转化、收入、页面加载时间和客服工单等主指标与护栏指标。

第 7 周新增 `customer_churn.csv`，用于预测模型基础实验。该文件的粒度为一行一个客户观测，显式区分训练集和测试集，包含客户关系时长、月消费、客服工单、折扣、使用活跃度、履约延迟和是否流失等字段。

第 8 周新增 `coupon_retention_observational.csv` 和 `coupon_retention_panel.csv`，用于因果推断基础实验。前者是一行一个客户的观测性优惠券干预数据，用于说明混杂、选择偏差、倾向得分和加权；后者是一行一个门店-时期观测的两期面板数据，用于说明差分中的差分。

第 9 周新增 `replenishment_planning.csv`，用于优化与处方分析实验。该文件的粒度为一行一个 SKU 补货策略输入，包含单位成本、贡献毛利、持有成本、缺货惩罚、当前库存、最大订货量、库容占用和三点需求预测。

第 10 周新增 `order_to_cash_event_log.csv`，用于流程数据与过程挖掘实验。该文件的粒度为一行一个事件，包含 case id、event id、activity、timestamp、resource、订单金额和区域，可用于构造流程变体、直接跟随图、吞吐时间、返工和合规异常指标。
