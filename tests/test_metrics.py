from bdm_decision.cases.week03_sql_kpi import (
    enrich_orders,
    load_sample_dataset,
    metric_dictionary,
    monthly_kpi_summary,
    region_kpi_summary,
    rolling_customer_revenue,
)
from bdm_decision.cases.week05_statistics_dashboard import (
    dashboard_kpis,
    descriptive_summary,
    detect_iqr_outliers,
    load_daily_operations,
    moving_average,
    vega_lite_dashboard_spec,
)
from bdm_decision.cases.week06_ab_testing import (
    load_checkout_experiment,
    render_ab_test_report_markdown,
)
from bdm_decision.cases.week07_prediction import (
    render_prediction_report_markdown,
    train_week07_churn_model,
)
from bdm_decision.cases.week08_causality import render_causal_report_markdown
from bdm_decision.cases.week09_optimization import render_optimization_report_markdown
from bdm_decision.cases.week10_process_mining import render_process_mining_report_markdown
from bdm_decision.causal.ab_test import (
    difference_in_means,
    required_sample_size_two_proportions,
    review_experiment_decision,
    summarize_by_variant,
)
from bdm_decision.causal.did import difference_in_differences, load_panel_records
from bdm_decision.causal.propensity_score import (
    fit_propensity_score,
    inverse_probability_weighted_ate,
    load_coupon_records,
    naive_difference,
    risk_band_adjusted_effect,
)
from bdm_decision.app.dashboard import render_dashboard_html
from bdm_decision.models.churn_model import plan_retention_actions, rank_customers_by_risk
from bdm_decision.models.evaluate import classification_metrics, confusion_matrix, log_loss, roc_auc
from bdm_decision.optimization.inventory_optimization import (
    evaluate_order_quantity,
    load_product_policies,
    marginal_values,
    optimize_replenishment,
)
from bdm_decision.process_mining.event_log import (
    average_throughput,
    bottleneck_transition,
    conformance_issues,
    directly_follows_graph,
    load_event_log,
    summarize_cases,
    summarize_variants,
)


def test_week03_monthly_kpi_summary() -> None:
    summary = monthly_kpi_summary(load_sample_dataset())

    assert len(summary) == 1
    march = summary[0]
    assert march["month"] == "2026-03"
    assert march["orders"] == 12
    assert march["delivered_orders"] == 12
    assert march["revenue"] == 71350.0
    assert march["gross_profit"] == 25360.0
    assert round(march["gross_margin"], 4) == 0.3554
    assert round(march["on_time_rate"], 4) == 0.5833


def test_week03_region_summary_keeps_ratio_denominators() -> None:
    summary = {row["region"]: row for row in region_kpi_summary(load_sample_dataset())}

    assert set(summary) == {"East", "North", "South", "West"}
    assert summary["East"]["delivered_orders"] == 4
    assert summary["East"]["revenue"] == 20550.0
    assert round(summary["East"]["on_time_rate"], 4) == 0.75
    assert summary["North"]["delivered_orders"] == 2
    assert round(summary["North"]["on_time_rate"], 4) == 0.5


def test_week03_rolling_customer_revenue() -> None:
    rolling = rolling_customer_revenue(load_sample_dataset())
    by_order = {row["order_id"]: row for row in rolling}

    assert by_order["O001"]["recent_revenue"] == 4800.0
    assert by_order["O005"]["recent_revenue"] == 11550.0
    assert by_order["O011"]["customer_order_sequence"] == 2


def test_week03_metric_dictionary_and_enrichment() -> None:
    dataset = load_sample_dataset()
    enriched = enrich_orders(dataset)
    metric_names = {metric.name for metric in metric_dictionary()}

    assert len(enriched) == 12
    assert {"revenue", "gross_margin", "on_time_delivery_rate"} <= metric_names
    assert all("region" in row and "category" in row for row in enriched)


def test_week05_descriptive_statistics() -> None:
    rows = load_daily_operations()
    revenue = [row.revenue for row in rows]
    summary = descriptive_summary(revenue)

    assert summary.n == 12
    assert round(summary.mean, 2) == 5945.83
    assert summary.median == 5100.0
    assert summary.q1 == 4100.0
    assert summary.q3 == 6975.0
    assert summary.iqr == 2875.0
    assert round(summary.sample_std, 2) == 2987.05
    assert detect_iqr_outliers(revenue) == [13500.0]


def test_week05_dashboard_kpis_and_moving_average() -> None:
    rows = load_daily_operations()
    kpis = dashboard_kpis(rows)
    moving = moving_average([row.revenue for row in rows], window=3)

    assert kpis["total_revenue"] == 71350.0
    assert round(kpis["on_time_rate"], 4) == 0.5833
    assert kpis["average_delay_days"] == 0.75
    assert kpis["latest_backlog_orders"] == 10
    assert kpis["quality_issue_count"] == 6
    assert round(moving[2], 2) == 6133.33
    assert moving[-1] == 5133.333333333333


def test_week05_dashboard_specs_and_html() -> None:
    rows = load_daily_operations()
    spec = vega_lite_dashboard_spec(rows)
    html = render_dashboard_html(rows)

    assert spec["$schema"].endswith("vega-lite/v5.json")
    assert len(spec["vconcat"]) == 2
    assert spec["vconcat"][0]["layer"][0]["mark"]["type"] == "bar"
    assert "Week 05 Operating Dashboard" in html
    assert "Total revenue" in html
    assert "<svg" in html


def test_week06_arm_summaries() -> None:
    records = load_checkout_experiment()
    summaries = {summary.variant: summary for summary in summarize_by_variant(records)}

    assert len(records) == 40
    assert summaries["A"].n == 20
    assert summaries["A"].conversions == 7
    assert summaries["B"].n == 20
    assert summaries["B"].conversions == 11
    assert summaries["A"].conversion_rate == 0.35
    assert summaries["B"].conversion_rate == 0.55
    assert summaries["B"].revenue_per_visitor == 31.65


def test_week06_effect_estimates_and_decision_review() -> None:
    records = load_checkout_experiment()
    conversion = difference_in_means(records, "converted")
    revenue = difference_in_means(records, "revenue")
    page_load = difference_in_means(records, "page_load_ms")
    decision = review_experiment_decision(records)

    assert round(conversion.difference, 4) == 0.2
    assert round(conversion.p_value, 4) == 0.2059
    assert round(revenue.difference, 2) == 14.7
    assert round(page_load.difference, 2) == 51.65
    assert decision.recommendation == "continue experiment or increase sample size before rollout"
    assert any("guardrail" in note for note in decision.notes)


def test_week06_sample_size_and_report() -> None:
    sample_size = required_sample_size_two_proportions(
        baseline_rate=0.35,
        minimum_detectable_effect=0.10,
    )
    report = render_ab_test_report_markdown()

    assert sample_size == 376
    assert "Week 06 A/B Test Report" in report
    assert "converted: control=0.3500" in report
    assert "page-load guardrail" in report


def test_week07_churn_model_training_and_signs() -> None:
    model, train, test = train_week07_churn_model()

    assert len(train) == 20
    assert len(test) == 10
    assert sum(row.churned for row in train) == 10
    assert model.coefficients["tenure_months"] < 0
    assert model.coefficients["support_tickets_90d"] > 0
    assert model.coefficients["usage_sessions_30d"] < 0


def test_week07_prediction_metrics_and_ranking() -> None:
    model, _, test = train_week07_churn_model()
    probabilities = [model.probability(row) for row in test]
    labels = [row.churned for row in test]
    matrix = confusion_matrix(labels, probabilities, threshold=0.5)
    metrics = classification_metrics(matrix)
    ranked = rank_customers_by_risk(model, test, limit=3)

    assert matrix.true_positive == 5
    assert matrix.false_positive == 1
    assert matrix.true_negative == 4
    assert matrix.false_negative == 0
    assert metrics.accuracy == 0.9
    assert round(metrics.f1, 4) == 0.9091
    assert roc_auc(labels, probabilities) == 1.0
    assert round(log_loss(labels, probabilities), 4) == 0.1397
    assert [record.customer_id for record, _ in ranked] == ["C030", "C028", "C021"]


def test_week07_retention_actions_and_report() -> None:
    model, _, test = train_week07_churn_model()
    actions = plan_retention_actions(model, test)
    report = render_prediction_report_markdown()

    assert actions[0].customer_id == "C028"
    assert actions[0].recommend_action is True
    assert sum(action.recommend_action for action in actions) == 4
    assert "Week 07 Prediction Report" in report
    assert "accuracy: 0.9000" in report
    assert "recommended actions: 4" in report


def test_week08_observational_adjustment() -> None:
    records = load_coupon_records()
    naive = naive_difference(records)
    stratified = risk_band_adjusted_effect(records)
    propensity_model = fit_propensity_score(records, feature_names=("risk_score",))
    ipw = inverse_probability_weighted_ate(records, propensity_model)

    assert len(records) == 24
    assert naive.effect == 0.0
    assert round(stratified.effect, 4) == 0.25
    assert round(propensity_model.coefficients["risk_score"], 4) == 1.0084
    assert round(ipw, 4) == 0.2199


def test_week08_difference_in_differences_and_report() -> None:
    estimate = difference_in_differences(load_panel_records())
    report = render_causal_report_markdown()

    assert round(estimate.treated_change, 4) == 0.0925
    assert round(estimate.control_change, 4) == 0.0150
    assert round(estimate.did, 4) == 0.0775
    assert "Week 08 Causal Inference Report" in report
    assert "risk-band stratification" in report
    assert "DID estimate: 0.0775" in report


def test_week09_replenishment_plan() -> None:
    policies = load_product_policies()
    plan = optimize_replenishment(policies, budget_limit=2600.0, storage_limit=95.0)
    quantities = {decision.product_id: decision.order_quantity for decision in plan.decisions}

    assert len(policies) == 4
    assert quantities == {"P01": 18, "P02": 16, "P03": 10, "P04": 8}
    assert plan.total_budget_used == 2596.0
    assert plan.total_storage_used == 93.0
    assert round(plan.total_expected_net_value, 2) == 3914.60


def test_week09_product_evaluation_and_report() -> None:
    policies = {policy.product_id: policy for policy in load_product_policies()}
    p02 = evaluate_order_quantity(policies["P02"], 16)
    p04_margins = marginal_values(policies["P04"])
    report = render_optimization_report_markdown()

    assert round(p02.expected_sales, 2) == 22.40
    assert round(p02.expected_unmet_demand, 2) == 2.00
    assert round(p02.expected_net_value, 2) == 1113.60
    assert p04_margins[:5] == [86.0, 86.0, 86.0, 86.0, 86.0]
    assert "Week 09 Optimization Report" in report
    assert "total expected net value: 3914.60" in report


def test_week10_event_log_summary_and_variants() -> None:
    events = load_event_log()
    cases = summarize_cases(events)
    variants = summarize_variants(cases)

    assert len(events) == 67
    assert len(cases) == 8
    assert len(variants) == 4
    assert round(average_throughput(cases), 2) == 114.88
    assert variants[0].case_count == 4
    assert variants[0].share == 0.5
    assert [case.case_id for case in cases if case.has_rework] == ["O2C003", "O2C006"]


def test_week10_bottleneck_conformance_and_report() -> None:
    events = load_event_log()
    cases = summarize_cases(events)
    transitions = directly_follows_graph(events)
    bottleneck = bottleneck_transition(transitions)
    issues = conformance_issues(cases)
    report = render_process_mining_report_markdown()

    assert bottleneck.source == "invoice_sent"
    assert bottleneck.target == "payment_received"
    assert round(bottleneck.average_elapsed_hours, 2) == 71.57
    assert [(issue.case_id, issue.issue) for issue in issues] == [
        ("O2C004", "missing credit_check"),
        ("O2C007", "activity order violation"),
    ]
    assert "Week 10 Process Mining Report" in report
    assert "variants: 4" in report
    assert "slowest average edge: invoice_sent > payment_received" in report
