from bdm_decision.cases.week04_data_quality import (
    load_week04_dataset,
    quality_report,
    render_quality_report_markdown,
)
from bdm_decision.quality.data_profile import profile_table
from bdm_decision.quality.validation_rules import validate_orders_dataset


def test_week04_clean_dataset_has_no_quality_issues() -> None:
    dataset = load_week04_dataset(dirty=False)
    issues = validate_orders_dataset(dataset)

    assert issues == []


def test_week04_dirty_dataset_detects_expected_issue_types() -> None:
    dataset = load_week04_dataset(dirty=True)
    issues = validate_orders_dataset(dataset)
    check_ids = {issue.check_id for issue in issues}

    assert "required_customer_id" in check_ids
    assert "required_actual_date" in check_ids
    assert "unique_order_id" in check_ids
    assert "relationship_customer_id" in check_ids
    assert "relationship_product_id" in check_ids
    assert "positive_quantity" in check_ids
    assert "accepted_values_channel" in check_ids
    assert "accepted_values_priority" in check_ids
    assert "promised_date_after_order_date" in check_ids
    assert len(issues) == 10


def test_week04_profile_counts_missing_and_distinct_values() -> None:
    orders = load_week04_dataset(dirty=True)["orders"]
    profiles = {profile.column: profile for profile in profile_table(orders)}

    assert profiles["order_id"].row_count == 9
    assert profiles["order_id"].distinct_count == 8
    assert profiles["customer_id"].missing_count == 1
    assert profiles["actual_date"].missing_count == 1
    assert profiles["channel"].distinct_count == 4


def test_week04_quality_report_markdown() -> None:
    report = quality_report(dirty=True)
    markdown = render_quality_report_markdown(dirty=True)

    assert report["issue_count"] == 10
    assert report["by_severity"] == {"error": 8, "warning": 2}
    assert "Week 04 Data Quality Report" in markdown
    assert "relationship_product_id" in markdown
