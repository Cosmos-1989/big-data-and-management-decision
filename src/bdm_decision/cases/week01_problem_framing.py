"""Week 01 case: convert operating symptoms into decision analytics questions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OperatingSymptom:
    name: str
    business_question: str
    candidate_data: list[str]
    kpis: list[str]
    analysis_type: str
    decision_action: str


SYMPTOMS = [
    OperatingSymptom(
        name="库存积压",
        business_question="哪些产品积压，积压是否来自需求下降、补货过量或渠道错配？",
        candidate_data=["订单明细", "库存快照", "产品主数据", "补货记录", "促销日历"],
        kpis=["库存周转率", "滞销库存金额", "缺货率", "毛利率"],
        analysis_type="诊断分析 + 处方分析",
        decision_action="调整补货量、促销策略或渠道分配",
    ),
    OperatingSymptom(
        name="交付延期",
        business_question="哪些订单有延期风险，瓶颈来自供应商、产能还是物流？",
        candidate_data=["订单状态", "供应商交期", "生产排程", "物流轨迹", "流程日志"],
        kpis=["准时交付率", "平均延期天数", "高风险订单数", "加急成本"],
        analysis_type="预测分析 + 优化决策",
        decision_action="选择订单加急、产能重排或供应商替代",
    ),
    OperatingSymptom(
        name="客户流失",
        business_question="哪些客户可能流失，干预是否真的能提升留存？",
        candidate_data=["客户画像", "交易历史", "服务记录", "营销触达", "优惠券发放"],
        kpis=["流失率", "复购率", "客户终身价值", "干预转化率"],
        analysis_type="预测分析 + 因果评估",
        decision_action="将有限优惠预算分配给最可能被挽回的客户",
    ),
    OperatingSymptom(
        name="产能瓶颈",
        business_question="哪些资源限制了吞吐量，如何在约束下重新分配任务？",
        candidate_data=["工单", "设备状态", "人员班次", "加工时间", "流程事件日志"],
        kpis=["吞吐时间", "资源利用率", "等待时间", "单位产能成本"],
        analysis_type="流程分析 + 优化决策",
        decision_action="调整排班、任务优先级或产能分配",
    ),
]


def decision_pipeline(symptom: OperatingSymptom) -> list[str]:
    return [
        f"业务症状：{symptom.name}",
        f"管理问题：{symptom.business_question}",
        f"数据表达：{', '.join(symptom.candidate_data)}",
        f"指标体系：{', '.join(symptom.kpis)}",
        f"分析类型：{symptom.analysis_type}",
        f"行动闭环：{symptom.decision_action}",
    ]


def render_case_table() -> str:
    header = "| 业务症状 | 管理问题 | 数据 | KPI | 分析类型 | 行动 |\n"
    separator = "|---|---|---|---|---|---|\n"
    rows = []
    for symptom in SYMPTOMS:
        rows.append(
            "| "
            + " | ".join(
                [
                    symptom.name,
                    symptom.business_question,
                    "、".join(symptom.candidate_data),
                    "、".join(symptom.kpis),
                    symptom.analysis_type,
                    symptom.decision_action,
                ]
            )
            + " |\n"
        )
    return header + separator + "".join(rows)


if __name__ == "__main__":
    print(render_case_table())

