"""Week 09 optimization case: replenishment planning under constraints."""

from __future__ import annotations

from bdm_decision.optimization.inventory_optimization import (
    format_plan_table,
    load_product_policies,
    marginal_values,
    optimize_replenishment,
)


DEFAULT_BUDGET_LIMIT = 2600.0
DEFAULT_STORAGE_LIMIT = 95.0


def render_optimization_report_markdown(
    budget_limit: float = DEFAULT_BUDGET_LIMIT,
    storage_limit: float = DEFAULT_STORAGE_LIMIT,
) -> str:
    """Render a concise Markdown report for the week-09 optimization case."""

    policies = load_product_policies()
    plan = optimize_replenishment(
        policies,
        budget_limit=budget_limit,
        storage_limit=storage_limit,
    )
    table = format_plan_table(plan, policies)

    lines = [
        "# Week 09 Optimization Report",
        "",
        "## Constraints",
        "",
        f"- budget limit: {budget_limit:.2f}",
        f"- storage limit: {storage_limit:.2f}",
        f"- budget used: {plan.total_budget_used:.2f}",
        f"- storage used: {plan.total_storage_used:.2f}",
        f"- total expected net value: {plan.total_expected_net_value:.2f}",
        "",
        "## Replenishment plan",
        "",
        (
            "| product | order_qty | expected_sales | expected_leftover | "
            "expected_unmet | budget_used | storage_used | expected_net_value |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in table:
        lines.append(
            f"| {row['product_id']} {row['product_name']} | "
            f"{row['order_quantity']} | {row['expected_sales']:.2f} | "
            f"{row['expected_leftover']:.2f} | {row['expected_unmet_demand']:.2f} | "
            f"{row['budget_used']:.2f} | {row['storage_used']:.2f} | "
            f"{row['expected_net_value']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## First marginal values",
            "",
            "| product | first five marginal values |",
            "|---|---|",
        ]
    )
    for policy in policies:
        margins = ", ".join(f"{value:.2f}" for value in marginal_values(policy)[:5])
        lines.append(f"| {policy.product_id} {policy.product_name} | {margins} |")

    lines.extend(
        [
            "",
            "## Management note",
            "",
            (
                "The plan converts demand forecasts and cost assumptions into a feasible "
                "order recommendation.  It should be reviewed against supplier lead times, "
                "service-level targets, substitution effects, and sensitivity to budget and "
                "storage limits before execution."
            ),
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    print(render_optimization_report_markdown())
