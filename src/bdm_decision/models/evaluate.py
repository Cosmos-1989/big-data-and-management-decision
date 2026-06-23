"""Model evaluation utilities for teaching predictive modeling.

The functions in this module intentionally use only the Python standard
library.  That keeps the week-07 examples transparent: students can inspect how
confusion matrices, log loss, ROC AUC, and calibration summaries are computed
before they move to scikit-learn.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ConfusionMatrix:
    """Confusion matrix for a binary classifier with positive label 1."""

    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int

    @property
    def total(self) -> int:
        return (
            self.true_positive
            + self.false_positive
            + self.true_negative
            + self.false_negative
        )


@dataclass(frozen=True)
class ClassificationMetrics:
    """Common threshold-based classification metrics."""

    accuracy: float
    precision: float
    recall: float
    specificity: float
    f1: float


@dataclass(frozen=True)
class CalibrationBin:
    """Observed outcome rate inside a probability interval."""

    lower: float
    upper: float
    count: int
    mean_probability: float
    observed_rate: float


def confusion_matrix(
    labels: Sequence[int],
    probabilities: Sequence[float],
    threshold: float = 0.5,
) -> ConfusionMatrix:
    """Return a binary confusion matrix for predicted probabilities."""

    if len(labels) != len(probabilities):
        raise ValueError("labels and probabilities must have the same length")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be in [0, 1]")

    tp = fp = tn = fn = 0
    for label, probability in zip(labels, probabilities):
        prediction = 1 if probability >= threshold else 0
        if label == 1 and prediction == 1:
            tp += 1
        elif label == 0 and prediction == 1:
            fp += 1
        elif label == 0 and prediction == 0:
            tn += 1
        elif label == 1 and prediction == 0:
            fn += 1
        else:
            raise ValueError("labels must be 0 or 1")
    return ConfusionMatrix(tp, fp, tn, fn)


def classification_metrics(matrix: ConfusionMatrix) -> ClassificationMetrics:
    """Compute accuracy, precision, recall, specificity, and F1."""

    accuracy = _safe_divide(matrix.true_positive + matrix.true_negative, matrix.total)
    precision = _safe_divide(matrix.true_positive, matrix.true_positive + matrix.false_positive)
    recall = _safe_divide(matrix.true_positive, matrix.true_positive + matrix.false_negative)
    specificity = _safe_divide(matrix.true_negative, matrix.true_negative + matrix.false_positive)
    f1 = _safe_divide(2 * precision * recall, precision + recall)
    return ClassificationMetrics(accuracy, precision, recall, specificity, f1)


def log_loss(labels: Sequence[int], probabilities: Sequence[float], eps: float = 1e-12) -> float:
    """Return average binary cross-entropy loss."""

    if len(labels) != len(probabilities):
        raise ValueError("labels and probabilities must have the same length")
    if not labels:
        raise ValueError("at least one observation is required")

    total = 0.0
    for label, probability in zip(labels, probabilities):
        if label not in {0, 1}:
            raise ValueError("labels must be 0 or 1")
        p = min(max(probability, eps), 1 - eps)
        total += -(label * math.log(p) + (1 - label) * math.log(1 - p))
    return total / len(labels)


def roc_auc(labels: Sequence[int], probabilities: Sequence[float]) -> float:
    """Compute ROC AUC as the probability that a positive ranks above a negative."""

    if len(labels) != len(probabilities):
        raise ValueError("labels and probabilities must have the same length")

    positives = [p for label, p in zip(labels, probabilities) if label == 1]
    negatives = [p for label, p in zip(labels, probabilities) if label == 0]
    if not positives or not negatives:
        raise ValueError("ROC AUC requires both positive and negative labels")

    wins = 0.0
    for positive in positives:
        for negative in negatives:
            if positive > negative:
                wins += 1.0
            elif positive == negative:
                wins += 0.5
    return wins / (len(positives) * len(negatives))


def calibration_table(
    labels: Sequence[int],
    probabilities: Sequence[float],
    bins: int = 5,
) -> list[CalibrationBin]:
    """Summarize predicted probability and observed rate by equal-width bins."""

    if len(labels) != len(probabilities):
        raise ValueError("labels and probabilities must have the same length")
    if bins <= 0:
        raise ValueError("bins must be positive")

    rows: list[CalibrationBin] = []
    width = 1.0 / bins
    for index in range(bins):
        lower = index * width
        upper = 1.0 if index == bins - 1 else (index + 1) * width
        bucket: list[tuple[int, float]] = []
        for label, probability in zip(labels, probabilities):
            in_last_bin = index == bins - 1 and lower <= probability <= upper
            in_regular_bin = index < bins - 1 and lower <= probability < upper
            if in_last_bin or in_regular_bin:
                bucket.append((label, probability))
        if not bucket:
            rows.append(CalibrationBin(lower, upper, 0, 0.0, 0.0))
            continue
        count = len(bucket)
        mean_probability = sum(probability for _, probability in bucket) / count
        observed_rate = sum(label for label, _ in bucket) / count
        rows.append(CalibrationBin(lower, upper, count, mean_probability, observed_rate))
    return rows


def _safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0
