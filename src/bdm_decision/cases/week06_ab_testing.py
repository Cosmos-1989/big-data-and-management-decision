"""Week 06 case: statistical inference, A/B testing, and management judgment."""

from __future__ import annotations

from pathlib import Path

from bdm_decision.causal.ab_test import (
    ExperimentRecord,
    difference_in_means,
    format_metric_effect,
    load_experiment_records,
    required_sample_size_two_proportions,
    review_experiment_decision,
    summarize_by_variant,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"


def load_checkout_experiment(
    path: Path = SAMPLE_DIR / "ab_test_checkout.csv",
) -> list[ExperimentRecord]:
    return load_experiment_records(path)


def render_ab_test_report_markdown(records: list[ExperimentRecord] | None = None) -> str:
    records = records or load_checkout_experiment()
    summaries = summarize_by_variant(records)
    conversion_effect = difference_in_means(records, "converted")
    revenue_effect = difference_in_means(records, "revenue")
    page_load_effect = difference_in_means(records, "page_load_ms")
    decision = review_experiment_decision(records)
    baseline = next(summary for summary in summaries if summary.variant == "A").conversion_rate
    sample_size = required_sample_size_two_proportions(
        baseline_rate=baseline,
        minimum_detectable_effect=0.10,
    )

    lines = [
        "# Week 06 A/B Test Report",
        "",
        "## Arm summary",
        "",
        "| variant | n | conversions | conversion_rate | revenue_per_visitor | average_order_value | page_load_ms | support_ticket_rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in summaries:
        lines.append(
            f"| {summary.variant} | {summary.n} | {summary.conversions} | "
            f"{summary.conversion_rate:.4f} | {summary.revenue_per_visitor:.2f} | "
            f"{summary.average_order_value:.2f} | {summary.average_page_load_ms:.1f} | "
            f"{summary.support_ticket_rate:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Effects",
            "",
            f"- {format_metric_effect(conversion_effect)}",
            f"- {format_metric_effect(revenue_effect)}",
            f"- {format_metric_effect(page_load_effect)}",
            "",
            "## Planning",
            "",
            f"- baseline conversion rate: {baseline:.4f}",
            f"- per-arm sample size for 10 percentage-point MDE at 80% power: {sample_size}",
            "",
            "## Decision review",
            "",
            f"- recommendation: {decision.recommendation}",
        ]
    )
    lines.extend(f"- note: {note}" for note in decision.notes)
    return "\n".join(lines)


def main() -> None:
    print(render_ab_test_report_markdown())


if __name__ == "__main__":
    main()
