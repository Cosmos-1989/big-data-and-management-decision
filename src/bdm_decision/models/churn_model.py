"""Customer churn modeling utilities for week 07 prediction examples."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_CHURN_DATA = (
    Path(__file__).resolve().parents[3] / "data" / "sample" / "customer_churn.csv"
)

DEFAULT_FEATURES = (
    "tenure_months",
    "monthly_spend",
    "support_tickets_90d",
    "discount_rate",
    "usage_sessions_30d",
    "late_delivery_count_90d",
)


@dataclass(frozen=True)
class CustomerChurnRecord:
    """One customer-period observation for churn prediction."""

    customer_id: str
    split: str
    segment: str
    tenure_months: float
    monthly_spend: float
    support_tickets_90d: float
    discount_rate: float
    usage_sessions_30d: float
    late_delivery_count_90d: float
    churned: int

    def feature_value(self, name: str) -> float:
        return float(getattr(self, name))


@dataclass(frozen=True)
class LogisticChurnModel:
    """A small standardized logistic regression model."""

    feature_names: tuple[str, ...]
    intercept: float
    coefficients: dict[str, float]
    means: dict[str, float]
    scales: dict[str, float]

    def probability(self, record: CustomerChurnRecord) -> float:
        linear_score = self.intercept
        for name in self.feature_names:
            standardized = (record.feature_value(name) - self.means[name]) / self.scales[name]
            linear_score += self.coefficients[name] * standardized
        return sigmoid(linear_score)

    def score_components(self, record: CustomerChurnRecord) -> dict[str, float]:
        """Return per-feature contributions to the log-odds score."""

        return {
            name: self.coefficients[name]
            * ((record.feature_value(name) - self.means[name]) / self.scales[name])
            for name in self.feature_names
        }


@dataclass(frozen=True)
class RetentionAction:
    """Expected value summary for a retention action."""

    customer_id: str
    churn_probability: float
    monthly_spend: float
    expected_margin_at_risk: float
    expected_saved_margin: float
    offer_cost: float
    expected_net_value: float
    recommend_action: bool


def load_churn_records(path: str | Path = DEFAULT_CHURN_DATA) -> list[CustomerChurnRecord]:
    """Load the week-07 customer churn sample data."""

    records: list[CustomerChurnRecord] = []
    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(
                CustomerChurnRecord(
                    customer_id=row["customer_id"],
                    split=row["split"],
                    segment=row["segment"],
                    tenure_months=float(row["tenure_months"]),
                    monthly_spend=float(row["monthly_spend"]),
                    support_tickets_90d=float(row["support_tickets_90d"]),
                    discount_rate=float(row["discount_rate"]),
                    usage_sessions_30d=float(row["usage_sessions_30d"]),
                    late_delivery_count_90d=float(row["late_delivery_count_90d"]),
                    churned=int(row["churned"]),
                )
            )
    return records


def split_records(
    records: Iterable[CustomerChurnRecord],
) -> tuple[list[CustomerChurnRecord], list[CustomerChurnRecord]]:
    """Split records according to the explicit train/test column."""

    train: list[CustomerChurnRecord] = []
    test: list[CustomerChurnRecord] = []
    for record in records:
        if record.split == "train":
            train.append(record)
        elif record.split == "test":
            test.append(record)
        else:
            raise ValueError(f"unknown split: {record.split}")
    if not train or not test:
        raise ValueError("both train and test records are required")
    return train, test


def fit_logistic_regression(
    records: Sequence[CustomerChurnRecord],
    feature_names: Sequence[str] = DEFAULT_FEATURES,
    learning_rate: float = 0.08,
    epochs: int = 3000,
    l2_penalty: float = 0.01,
) -> LogisticChurnModel:
    """Fit a small logistic regression model by batch gradient descent."""

    if not records:
        raise ValueError("at least one training record is required")
    feature_tuple = tuple(feature_names)
    means, scales = feature_statistics(records, feature_tuple)
    matrix = [standardize_record(record, feature_tuple, means, scales) for record in records]
    labels = [record.churned for record in records]

    positive_rate = min(max(sum(labels) / len(labels), 1e-4), 1 - 1e-4)
    intercept = math.log(positive_rate / (1 - positive_rate))
    coefficients = [0.0 for _ in feature_tuple]

    for _ in range(epochs):
        gradient = [0.0 for _ in feature_tuple]
        intercept_gradient = 0.0
        for values, label in zip(matrix, labels):
            probability = sigmoid(intercept + sum(w * x for w, x in zip(coefficients, values)))
            error = probability - label
            intercept_gradient += error
            for index, value in enumerate(values):
                gradient[index] += error * value

        n = len(records)
        intercept -= learning_rate * (intercept_gradient / n)
        for index, value in enumerate(gradient):
            regularization = l2_penalty * coefficients[index]
            coefficients[index] -= learning_rate * ((value / n) + regularization)

    return LogisticChurnModel(
        feature_names=feature_tuple,
        intercept=intercept,
        coefficients=dict(zip(feature_tuple, coefficients)),
        means=means,
        scales=scales,
    )


def predict_probabilities(
    model: LogisticChurnModel,
    records: Iterable[CustomerChurnRecord],
) -> list[float]:
    """Predict churn probabilities for records."""

    return [model.probability(record) for record in records]


def rank_customers_by_risk(
    model: LogisticChurnModel,
    records: Iterable[CustomerChurnRecord],
    limit: int | None = None,
) -> list[tuple[CustomerChurnRecord, float]]:
    """Return customers sorted by predicted churn probability."""

    ranked = sorted(
        ((record, model.probability(record)) for record in records),
        key=lambda item: item[1],
        reverse=True,
    )
    return ranked if limit is None else ranked[:limit]


def plan_retention_actions(
    model: LogisticChurnModel,
    records: Iterable[CustomerChurnRecord],
    months_at_risk: int = 3,
    gross_margin: float = 0.45,
    retention_effect: float = 0.35,
    offer_cost: float = 35.0,
) -> list[RetentionAction]:
    """Rank retention actions by expected net value."""

    actions: list[RetentionAction] = []
    for record in records:
        probability = model.probability(record)
        margin_at_risk = record.monthly_spend * months_at_risk * gross_margin
        saved_margin = probability * margin_at_risk * retention_effect
        net_value = saved_margin - offer_cost
        actions.append(
            RetentionAction(
                customer_id=record.customer_id,
                churn_probability=probability,
                monthly_spend=record.monthly_spend,
                expected_margin_at_risk=margin_at_risk,
                expected_saved_margin=saved_margin,
                offer_cost=offer_cost,
                expected_net_value=net_value,
                recommend_action=net_value > 0,
            )
        )
    return sorted(actions, key=lambda action: action.expected_net_value, reverse=True)


def feature_statistics(
    records: Sequence[CustomerChurnRecord],
    feature_names: Sequence[str],
) -> tuple[dict[str, float], dict[str, float]]:
    """Return training means and population standard deviations."""

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
    record: CustomerChurnRecord,
    feature_names: Sequence[str],
    means: dict[str, float],
    scales: dict[str, float],
) -> list[float]:
    return [(record.feature_value(name) - means[name]) / scales[name] for name in feature_names]


def sigmoid(value: float) -> float:
    """Numerically stable logistic function."""

    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)
