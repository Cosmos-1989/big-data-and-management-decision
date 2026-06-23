"""Validation rules for sample enterprise data."""

from __future__ import annotations

from bdm_decision.quality.checks import (
    QualityIssue,
    check_accepted_values,
    check_date_order,
    check_positive_number,
    check_relationship,
    check_required,
    check_unique,
)


ORDER_REQUIRED_COLUMNS = (
    "order_id",
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "promised_date",
    "actual_date",
)

ACCEPTED_CHANNELS = {"Direct", "Partner", "Online"}
ACCEPTED_PRIORITIES = {"High", "Normal"}


def validate_orders_dataset(dataset: dict[str, list[dict[str, str]]]) -> list[QualityIssue]:
    orders = dataset["orders"]
    customers = dataset["customers"]
    products = dataset["products"]
    issues: list[QualityIssue] = []

    issues.extend(
        check_required(
            orders,
            table="orders",
            columns=ORDER_REQUIRED_COLUMNS,
            key_column="order_id",
            severity="error",
        )
    )
    issues.extend(check_unique(orders, table="orders", column="order_id", severity="error"))
    issues.extend(
        check_relationship(
            orders,
            customers,
            child_table="orders",
            parent_table="customers",
            child_column="customer_id",
            parent_column="customer_id",
            key_column="order_id",
            severity="error",
        )
    )
    issues.extend(
        check_relationship(
            orders,
            products,
            child_table="orders",
            parent_table="products",
            child_column="product_id",
            parent_column="product_id",
            key_column="order_id",
            severity="error",
        )
    )
    issues.extend(
        check_positive_number(
            orders,
            table="orders",
            column="quantity",
            key_column="order_id",
            severity="error",
        )
    )
    issues.extend(
        check_accepted_values(
            orders,
            table="orders",
            column="channel",
            accepted_values=ACCEPTED_CHANNELS,
            key_column="order_id",
            severity="warning",
        )
    )
    issues.extend(
        check_accepted_values(
            orders,
            table="orders",
            column="priority",
            accepted_values=ACCEPTED_PRIORITIES,
            key_column="order_id",
            severity="warning",
        )
    )
    issues.extend(
        check_date_order(
            orders,
            table="orders",
            start_column="order_date",
            end_column="promised_date",
            key_column="order_id",
            check_id="promised_date_after_order_date",
            severity="error",
        )
    )
    issues.extend(
        check_date_order(
            orders,
            table="orders",
            start_column="order_date",
            end_column="actual_date",
            key_column="order_id",
            check_id="actual_date_after_order_date",
            severity="error",
        )
    )
    return sorted(issues, key=lambda issue: (issue.severity, issue.check_id, issue.row_id))

