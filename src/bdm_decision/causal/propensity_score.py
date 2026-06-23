"""Propensity score utilities for observational management interventions."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_COUPON_DATA = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "sample"
    / "coupon_retention_observational.csv"
)

DEFAULT_COVARIATES = (
    "risk_score",
    "tenure_months",
    "monthly_spend",
    "support_tickets_90d",
    "usage_sessions_30d",
)


@dataclass(frozen=True)
class CouponRecord:
    """One customer observation in an observational coupon campaign."""

    customer_id: str
    risk_band: str
    risk_score: float
    tenure_months: float
    monthly_spend: float
    support_tickets_90d: float
    usage_sessions_30d: float
    coupon: int
    retained_30d: int

    def feature_value(self, name: str) -> float:
        return float(getattr(self, name))


@dataclass(frozen=True)
class PropensityScoreModel:
    """Small standardized logistic model for treatment assignment."""

    feature_names: tuple[str, ...]
    intercept: float
    coefficients: dict[str, float]
    means: dict[str, float]
    scales: dict[str, float]

    def probability(self, record: CouponRecord) -> float:
        score = self.intercept
        for name in self.feature_names:
            score += self.coefficients[name] * (
                (record.feature_value(name) - self.means[name]) / self.scales[name]
            )
        return sigmoid(score)


@dataclass(frozen=True)
class EffectEstimate:
    """Average treatment effect estimate for a binary intervention."""

    method: str
    treatment_mean: float
    control_mean: float
    effect: float
    treated_n: int
    control_n: int


@dataclass(frozen=True)
class BalanceRow:
    """Standardized mean difference before or after weighting."""

    feature: str
    treated_mean: float
    control_mean: float
    standardized_mean_difference: float


def load_coupon_records(path: str | Path = DEFAULT_COUPON_DATA) -> list[CouponRecord]:
    """Load week-08 observational coupon data."""

    records: list[CouponRecord] = []
    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(
                CouponRecord(
                    customer_id=row["customer_id"],
                    risk_band=row["risk_band"],
                    risk_score=float(row["risk_score"]),
                    tenure_months=float(row["tenure_months"]),
                    monthly_spend=float(row["monthly_spend"]),
                    support_tickets_90d=float(row["support_tickets_90d"]),
                    usage_sessions_30d=float(row["usage_sessions_30d"]),
                    coupon=int(row["coupon"]),
                    retained_30d=int(row["retained_30d"]),
                )
            )
    return records


def naive_difference(
    records: Sequence[CouponRecord],
    outcome: str = "retained_30d",
) -> EffectEstimate:
    """Compare treated and untreated outcomes without adjustment."""

    treated = [float(getattr(record, outcome)) for record in records if record.coupon == 1]
    control = [float(getattr(record, outcome)) for record in records if record.coupon == 0]
    if not treated or not control:
        raise ValueError("both treated and control groups are required")
    treatment_mean = sum(treated) / len(treated)
    control_mean = sum(control) / len(control)
    return EffectEstimate(
        method="naive difference",
        treatment_mean=treatment_mean,
        control_mean=control_mean,
        effect=treatment_mean - control_mean,
        treated_n=len(treated),
        control_n=len(control),
    )


def risk_band_adjusted_effect(records: Sequence[CouponRecord]) -> EffectEstimate:
    """Estimate an ATE by exact stratification on risk band."""

    bands = sorted({record.risk_band for record in records})
    total_n = len(records)
    weighted_effect = 0.0
    treated_total = 0
    control_total = 0
    for band in bands:
        band_records = [record for record in records if record.risk_band == band]
        treated = [record.retained_30d for record in band_records if record.coupon == 1]
        control = [record.retained_30d for record in band_records if record.coupon == 0]
        if not treated or not control:
            continue
        treated_total += len(treated)
        control_total += len(control)
        weighted_effect += (len(band_records) / total_n) * (
            sum(treated) / len(treated) - sum(control) / len(control)
        )

    naive = naive_difference(records)
    return EffectEstimate(
        method="risk-band stratification",
        treatment_mean=naive.treatment_mean,
        control_mean=naive.control_mean,
        effect=weighted_effect,
        treated_n=treated_total,
        control_n=control_total,
    )


def fit_propensity_score(
    records: Sequence[CouponRecord],
    feature_names: Sequence[str] = DEFAULT_COVARIATES,
    learning_rate: float = 0.08,
    epochs: int = 3000,
    l2_penalty: float = 0.02,
) -> PropensityScoreModel:
    """Fit a small logistic treatment-assignment model."""

    if not records:
        raise ValueError("at least one observation is required")
    feature_tuple = tuple(feature_names)
    means, scales = feature_statistics(records, feature_tuple)
    matrix = [standardize_record(record, feature_tuple, means, scales) for record in records]
    treatments = [record.coupon for record in records]

    treatment_rate = min(max(sum(treatments) / len(treatments), 1e-4), 1 - 1e-4)
    intercept = math.log(treatment_rate / (1 - treatment_rate))
    coefficients = [0.0 for _ in feature_tuple]

    for _ in range(epochs):
        intercept_gradient = 0.0
        gradients = [0.0 for _ in feature_tuple]
        for values, treatment in zip(matrix, treatments):
            probability = sigmoid(intercept + sum(w * x for w, x in zip(coefficients, values)))
            error = probability - treatment
            intercept_gradient += error
            for index, value in enumerate(values):
                gradients[index] += error * value

        n = len(records)
        intercept -= learning_rate * (intercept_gradient / n)
        for index, gradient in enumerate(gradients):
            regularization = l2_penalty * coefficients[index]
            coefficients[index] -= learning_rate * ((gradient / n) + regularization)

    return PropensityScoreModel(
        feature_names=feature_tuple,
        intercept=intercept,
        coefficients=dict(zip(feature_tuple, coefficients)),
        means=means,
        scales=scales,
    )


def inverse_probability_weighted_ate(
    records: Sequence[CouponRecord],
    model: PropensityScoreModel,
    outcome: str = "retained_30d",
    clip: float = 0.05,
) -> float:
    """Estimate the ATE with inverse probability weights."""

    total = 0.0
    for record in records:
        propensity = min(max(model.probability(record), clip), 1 - clip)
        value = float(getattr(record, outcome))
        if record.coupon == 1:
            total += value / propensity
        else:
            total -= value / (1 - propensity)
    return total / len(records)


def covariate_balance(
    records: Sequence[CouponRecord],
    feature_names: Sequence[str] = DEFAULT_COVARIATES,
    weights: dict[str, float] | None = None,
) -> list[BalanceRow]:
    """Compute standardized mean differences by feature."""

    rows: list[BalanceRow] = []
    for name in feature_names:
        treated = [record for record in records if record.coupon == 1]
        control = [record for record in records if record.coupon == 0]
        treated_values = [record.feature_value(name) for record in treated]
        control_values = [record.feature_value(name) for record in control]
        treated_weights = [weights.get(record.customer_id, 1.0) if weights else 1.0 for record in treated]
        control_weights = [weights.get(record.customer_id, 1.0) if weights else 1.0 for record in control]
        treated_mean = weighted_mean(treated_values, treated_weights)
        control_mean = weighted_mean(control_values, control_weights)
        pooled_std = pooled_standard_deviation(treated_values, control_values)
        rows.append(
            BalanceRow(
                feature=name,
                treated_mean=treated_mean,
                control_mean=control_mean,
                standardized_mean_difference=(treated_mean - control_mean) / pooled_std
                if pooled_std
                else 0.0,
            )
        )
    return rows


def inverse_probability_weights(
    records: Sequence[CouponRecord],
    model: PropensityScoreModel,
    clip: float = 0.05,
) -> dict[str, float]:
    """Return unstabilized inverse probability weights by customer id."""

    weights: dict[str, float] = {}
    for record in records:
        propensity = min(max(model.probability(record), clip), 1 - clip)
        weights[record.customer_id] = 1 / propensity if record.coupon else 1 / (1 - propensity)
    return weights


def feature_statistics(
    records: Sequence[CouponRecord],
    feature_names: Sequence[str],
) -> tuple[dict[str, float], dict[str, float]]:
    means: dict[str, float] = {}
    scales: dict[str, float] = {}
    for name in feature_names:
        values = [record.feature_value(name) for record in records]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        means[name] = mean
        scales[name] = math.sqrt(variance) or 1.0
    return means, scales


def standardize_record(
    record: CouponRecord,
    feature_names: Sequence[str],
    means: dict[str, float],
    scales: dict[str, float],
) -> list[float]:
    return [(record.feature_value(name) - means[name]) / scales[name] for name in feature_names]


def weighted_mean(values: Sequence[float], weights: Sequence[float]) -> float:
    if len(values) != len(weights):
        raise ValueError("values and weights must have the same length")
    denominator = sum(weights)
    return sum(value * weight for value, weight in zip(values, weights)) / denominator


def pooled_standard_deviation(treated: Sequence[float], control: Sequence[float]) -> float:
    values = list(treated) + list(control)
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)
