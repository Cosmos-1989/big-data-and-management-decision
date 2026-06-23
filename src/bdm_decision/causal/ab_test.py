"""A/B testing utilities for teaching randomized management experiments."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist, mean


@dataclass(frozen=True)
class ExperimentRecord:
    visitor_id: str
    assignment_date: str
    segment: str
    variant: str
    converted: int
    revenue: float
    page_load_ms: float
    support_ticket: int


@dataclass(frozen=True)
class ArmSummary:
    variant: str
    n: int
    conversions: int
    conversion_rate: float
    total_revenue: float
    revenue_per_visitor: float
    average_order_value: float
    average_page_load_ms: float
    support_ticket_rate: float


@dataclass(frozen=True)
class MetricEffect:
    metric: str
    control_variant: str
    treatment_variant: str
    control_mean: float
    treatment_mean: float
    difference: float
    relative_lift: float | None
    standard_error: float
    z_score: float
    p_value: float
    confidence_level: float
    ci_low: float
    ci_high: float


@dataclass(frozen=True)
class DecisionReview:
    primary_effect: MetricEffect
    guardrail_effects: list[MetricEffect]
    recommendation: str
    notes: list[str]


def load_experiment_records(path: Path) -> list[ExperimentRecord]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return [
            ExperimentRecord(
                visitor_id=row["visitor_id"],
                assignment_date=row["assignment_date"],
                segment=row["segment"],
                variant=row["variant"],
                converted=int(row["converted"]),
                revenue=float(row["revenue"]),
                page_load_ms=float(row["page_load_ms"]),
                support_ticket=int(row["support_ticket"]),
            )
            for row in rows
        ]


def summarize_by_variant(records: list[ExperimentRecord]) -> list[ArmSummary]:
    variants = sorted({record.variant for record in records})
    summaries = []
    for variant in variants:
        arm = [record for record in records if record.variant == variant]
        conversions = sum(record.converted for record in arm)
        total_revenue = sum(record.revenue for record in arm)
        summaries.append(
            ArmSummary(
                variant=variant,
                n=len(arm),
                conversions=conversions,
                conversion_rate=conversions / len(arm) if arm else 0.0,
                total_revenue=total_revenue,
                revenue_per_visitor=total_revenue / len(arm) if arm else 0.0,
                average_order_value=total_revenue / conversions if conversions else 0.0,
                average_page_load_ms=mean([record.page_load_ms for record in arm]) if arm else 0.0,
                support_ticket_rate=sum(record.support_ticket for record in arm) / len(arm)
                if arm
                else 0.0,
            )
        )
    return summaries


def _metric_value(record: ExperimentRecord, metric: str) -> float:
    if not hasattr(record, metric):
        raise ValueError(f"Unknown experiment metric: {metric}")
    return float(getattr(record, metric))


def _sample_variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return sum((value - avg) ** 2 for value in values) / (len(values) - 1)


def difference_in_means(
    records: list[ExperimentRecord],
    metric: str,
    treatment_variant: str = "B",
    control_variant: str = "A",
    confidence_level: float = 0.95,
) -> MetricEffect:
    control = [_metric_value(record, metric) for record in records if record.variant == control_variant]
    treatment = [
        _metric_value(record, metric) for record in records if record.variant == treatment_variant
    ]
    if not control or not treatment:
        raise ValueError("Both control and treatment variants must contain observations")

    control_mean = mean(control)
    treatment_mean = mean(treatment)
    difference = treatment_mean - control_mean
    standard_error = math.sqrt(
        _sample_variance(control) / len(control)
        + _sample_variance(treatment) / len(treatment)
    )
    normal = NormalDist()
    z_score = difference / standard_error if standard_error else 0.0
    p_value = 2 * (1 - normal.cdf(abs(z_score))) if standard_error else 1.0
    z_critical = normal.inv_cdf(0.5 + confidence_level / 2)
    return MetricEffect(
        metric=metric,
        control_variant=control_variant,
        treatment_variant=treatment_variant,
        control_mean=control_mean,
        treatment_mean=treatment_mean,
        difference=difference,
        relative_lift=difference / control_mean if control_mean else None,
        standard_error=standard_error,
        z_score=z_score,
        p_value=p_value,
        confidence_level=confidence_level,
        ci_low=difference - z_critical * standard_error,
        ci_high=difference + z_critical * standard_error,
    )


def required_sample_size_two_proportions(
    baseline_rate: float,
    minimum_detectable_effect: float,
    alpha: float = 0.05,
    power: float = 0.8,
) -> int:
    if not 0 < baseline_rate < 1:
        raise ValueError("baseline_rate must be between 0 and 1")
    treatment_rate = baseline_rate + minimum_detectable_effect
    if not 0 < treatment_rate < 1:
        raise ValueError("baseline_rate + minimum_detectable_effect must be between 0 and 1")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    if not 0 < power < 1:
        raise ValueError("power must be between 0 and 1")

    normal = NormalDist()
    z_alpha = normal.inv_cdf(1 - alpha / 2)
    z_beta = normal.inv_cdf(power)
    pooled_rate = (baseline_rate + treatment_rate) / 2
    numerator = (
        z_alpha * math.sqrt(2 * pooled_rate * (1 - pooled_rate))
        + z_beta
        * math.sqrt(
            baseline_rate * (1 - baseline_rate)
            + treatment_rate * (1 - treatment_rate)
        )
    ) ** 2
    return math.ceil(numerator / minimum_detectable_effect**2)


def review_experiment_decision(
    records: list[ExperimentRecord],
    primary_metric: str = "converted",
    guardrail_metrics: tuple[str, ...] = ("page_load_ms", "support_ticket"),
    alpha: float = 0.05,
) -> DecisionReview:
    confidence_level = 1 - alpha
    primary = difference_in_means(
        records,
        metric=primary_metric,
        confidence_level=confidence_level,
    )
    guardrails = [
        difference_in_means(records, metric=metric, confidence_level=confidence_level)
        for metric in guardrail_metrics
    ]

    notes = []
    if primary.ci_low > 0:
        notes.append("primary metric is positive at the chosen confidence level")
    else:
        notes.append("primary metric is promising but still statistically uncertain")

    for guardrail in guardrails:
        if guardrail.metric == "page_load_ms" and guardrail.ci_low > 0:
            notes.append("page-load guardrail may deteriorate under treatment")
        if guardrail.metric == "support_ticket" and guardrail.ci_low > 0:
            notes.append("support-ticket guardrail may deteriorate under treatment")

    if primary.ci_low > 0 and not any("deteriorate" in note for note in notes):
        recommendation = "ship treatment with monitored rollout"
    else:
        recommendation = "continue experiment or increase sample size before rollout"

    return DecisionReview(
        primary_effect=primary,
        guardrail_effects=guardrails,
        recommendation=recommendation,
        notes=notes,
    )


def format_metric_effect(effect: MetricEffect) -> str:
    lift = "NA" if effect.relative_lift is None else f"{effect.relative_lift:.2%}"
    return (
        f"{effect.metric}: control={effect.control_mean:.4f}, "
        f"treatment={effect.treatment_mean:.4f}, diff={effect.difference:.4f}, "
        f"lift={lift}, ci=[{effect.ci_low:.4f}, {effect.ci_high:.4f}], "
        f"p={effect.p_value:.4f}"
    )
