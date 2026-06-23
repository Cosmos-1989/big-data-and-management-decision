"""Week 07 prediction case: customer churn risk and retention decisions."""

from __future__ import annotations

from bdm_decision.models.churn_model import (
    CustomerChurnRecord,
    DEFAULT_FEATURES,
    LogisticChurnModel,
    fit_logistic_regression,
    load_churn_records,
    plan_retention_actions,
    rank_customers_by_risk,
    split_records,
)
from bdm_decision.models.evaluate import (
    calibration_table,
    classification_metrics,
    confusion_matrix,
    log_loss,
    roc_auc,
)


def train_week07_churn_model() -> tuple[
    LogisticChurnModel,
    list[CustomerChurnRecord],
    list[CustomerChurnRecord],
]:
    """Load the sample data and train the teaching churn model."""

    records = load_churn_records()
    train, test = split_records(records)
    model = fit_logistic_regression(train, feature_names=DEFAULT_FEATURES)
    return model, train, test


def render_prediction_report_markdown(threshold: float = 0.5) -> str:
    """Render a concise Markdown report for the week-07 case."""

    model, train, test = train_week07_churn_model()
    probabilities = [model.probability(record) for record in test]
    labels = [record.churned for record in test]
    matrix = confusion_matrix(labels, probabilities, threshold=threshold)
    metrics = classification_metrics(matrix)
    auc = roc_auc(labels, probabilities)
    loss = log_loss(labels, probabilities)
    top_risk = rank_customers_by_risk(model, test, limit=5)
    actions = plan_retention_actions(model, test)
    recommended = [action for action in actions if action.recommend_action]
    calibration = calibration_table(labels, probabilities, bins=4)

    lines = [
        "# Week 07 Prediction Report",
        "",
        "## Data split",
        "",
        f"- train rows: {len(train)}",
        f"- test rows: {len(test)}",
        f"- train churn rate: {sum(row.churned for row in train) / len(train):.4f}",
        f"- test churn rate: {sum(row.churned for row in test) / len(test):.4f}",
        "",
        "## Model coefficients",
        "",
        "| feature | coefficient |",
        "|---|---:|",
    ]
    for name, value in sorted(
        model.coefficients.items(),
        key=lambda item: abs(item[1]),
        reverse=True,
    ):
        lines.append(f"| {name} | {value:.4f} |")

    lines.extend(
        [
            "",
            "## Test metrics",
            "",
            f"- threshold: {threshold:.2f}",
            (
                "- confusion matrix: "
                f"TP={matrix.true_positive}, FP={matrix.false_positive}, "
                f"TN={matrix.true_negative}, FN={matrix.false_negative}"
            ),
            f"- accuracy: {metrics.accuracy:.4f}",
            f"- precision: {metrics.precision:.4f}",
            f"- recall: {metrics.recall:.4f}",
            f"- specificity: {metrics.specificity:.4f}",
            f"- f1: {metrics.f1:.4f}",
            f"- ROC AUC: {auc:.4f}",
            f"- log loss: {loss:.4f}",
            "",
            "## Highest-risk customers",
            "",
            "| customer | probability | actual_churned | segment | monthly_spend |",
            "|---|---:|---:|---|---:|",
        ]
    )
    for record, probability in top_risk:
        lines.append(
            "| "
            f"{record.customer_id} | {probability:.4f} | {record.churned} | "
            f"{record.segment} | {record.monthly_spend:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Retention action screen",
            "",
            "| customer | probability | expected_net_value | recommend |",
            "|---|---:|---:|---|",
        ]
    )
    for action in actions[:5]:
        recommend = "yes" if action.recommend_action else "no"
        lines.append(
            f"| {action.customer_id} | {action.churn_probability:.4f} | "
            f"{action.expected_net_value:.2f} | {recommend} |"
        )

    lines.extend(
        [
            "",
            f"- recommended actions: {len(recommended)}",
            "",
            "## Calibration check",
            "",
            "| bin | count | mean_probability | observed_rate |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in calibration:
        lines.append(
            f"| [{row.lower:.2f}, {row.upper:.2f}] | {row.count} | "
            f"{row.mean_probability:.4f} | {row.observed_rate:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Management note",
            "",
            (
                "The model is useful for prioritizing retention review, but the sample is "
                "small.  Threshold choice should be tied to offer cost, expected margin, "
                "capacity, and fairness checks rather than accuracy alone."
            ),
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    print(render_prediction_report_markdown())
