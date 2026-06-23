"""Week 08 causal inference case: coupon interventions and retention."""

from __future__ import annotations

from bdm_decision.causal.did import difference_in_differences, load_panel_records
from bdm_decision.causal.propensity_score import (
    covariate_balance,
    fit_propensity_score,
    inverse_probability_weighted_ate,
    inverse_probability_weights,
    load_coupon_records,
    naive_difference,
    risk_band_adjusted_effect,
)


def render_causal_report_markdown() -> str:
    """Render a concise Markdown report for the week-08 causal case."""

    records = load_coupon_records()
    naive = naive_difference(records)
    stratified = risk_band_adjusted_effect(records)
    propensity_model = fit_propensity_score(records, feature_names=("risk_score",))
    ipw_effect = inverse_probability_weighted_ate(records, propensity_model)
    raw_balance = covariate_balance(records)
    weights = inverse_probability_weights(records, propensity_model)
    weighted_balance = covariate_balance(records, weights=weights)
    did = difference_in_differences(load_panel_records())

    lines = [
        "# Week 08 Causal Inference Report",
        "",
        "## Observational coupon campaign",
        "",
        f"- rows: {len(records)}",
        f"- treated customers: {sum(record.coupon for record in records)}",
        f"- control customers: {sum(1 - record.coupon for record in records)}",
        "",
        "## Treatment effect estimates",
        "",
        "| method | treated_mean | control_mean | effect |",
        "|---|---:|---:|---:|",
        (
            f"| {naive.method} | {naive.treatment_mean:.4f} | "
            f"{naive.control_mean:.4f} | {naive.effect:.4f} |"
        ),
        (
            f"| {stratified.method} | {stratified.treatment_mean:.4f} | "
            f"{stratified.control_mean:.4f} | {stratified.effect:.4f} |"
        ),
        f"| inverse probability weighting | NA | NA | {ipw_effect:.4f} |",
        "",
        "## Propensity model coefficients",
        "",
        "| feature | coefficient |",
        "|---|---:|",
    ]
    for name, value in sorted(
        propensity_model.coefficients.items(),
        key=lambda item: abs(item[1]),
        reverse=True,
    ):
        lines.append(f"| {name} | {value:.4f} |")

    lines.extend(
        [
            "",
            "## Balance check",
            "",
            "| feature | raw_smd | weighted_smd |",
            "|---|---:|---:|",
        ]
    )
    weighted_by_feature = {row.feature: row for row in weighted_balance}
    for row in raw_balance:
        weighted_row = weighted_by_feature[row.feature]
        lines.append(
            f"| {row.feature} | {row.standardized_mean_difference:.4f} | "
            f"{weighted_row.standardized_mean_difference:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Difference-in-differences panel",
            "",
            "| group | pre | post | change |",
            "|---|---:|---:|---:|",
            (
                f"| treated | {did.treated_pre:.4f} | {did.treated_post:.4f} | "
                f"{did.treated_change:.4f} |"
            ),
            (
                f"| control | {did.control_pre:.4f} | {did.control_post:.4f} | "
                f"{did.control_change:.4f} |"
            ),
            "",
            f"- DID estimate: {did.did:.4f}",
            "",
            "## Management note",
            "",
            (
                "The naive comparison misses selection bias because higher-risk customers "
                "were more likely to receive coupons.  Adjustment improves the comparison, "
                "but causal claims still require explicit assumptions about unobserved "
                "confounding, overlap, SUTVA, and parallel trends."
            ),
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    print(render_causal_report_markdown())
