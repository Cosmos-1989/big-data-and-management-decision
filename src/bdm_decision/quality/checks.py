"""Reusable data quality checks for course sample data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable


@dataclass(frozen=True)
class QualityIssue:
    check_id: str
    dimension: str
    severity: str
    table: str
    column: str
    row_id: str
    message: str


def is_missing(value: object) -> bool:
    return value is None or str(value).strip() == ""


def parse_iso_date(value: str) -> date | None:
    if is_missing(value):
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def check_required(
    rows: Iterable[dict[str, str]],
    *,
    table: str,
    columns: tuple[str, ...],
    key_column: str,
    severity: str = "error",
) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    for index, row in enumerate(rows, start=1):
        row_id = row.get(key_column) or f"row-{index}"
        for column in columns:
            if is_missing(row.get(column)):
                issues.append(
                    QualityIssue(
                        check_id=f"required_{column}",
                        dimension="completeness",
                        severity=severity,
                        table=table,
                        column=column,
                        row_id=row_id,
                        message=f"{column} is required but missing.",
                    )
                )
    return issues


def check_unique(
    rows: Iterable[dict[str, str]],
    *,
    table: str,
    column: str,
    severity: str = "error",
) -> list[QualityIssue]:
    seen: dict[str, int] = {}
    duplicates: set[str] = set()
    for row in rows:
        value = row.get(column, "")
        if is_missing(value):
            continue
        if value in seen:
            duplicates.add(value)
        seen[value] = seen.get(value, 0) + 1
    return [
        QualityIssue(
            check_id=f"unique_{column}",
            dimension="uniqueness",
            severity=severity,
            table=table,
            column=column,
            row_id=value,
            message=f"{column}={value} appears {seen[value]} times.",
        )
        for value in sorted(duplicates)
    ]


def check_relationship(
    child_rows: Iterable[dict[str, str]],
    parent_rows: Iterable[dict[str, str]],
    *,
    child_table: str,
    parent_table: str,
    child_column: str,
    parent_column: str,
    key_column: str,
    severity: str = "error",
) -> list[QualityIssue]:
    parent_values = {row[parent_column] for row in parent_rows if not is_missing(row.get(parent_column))}
    issues: list[QualityIssue] = []
    for index, row in enumerate(child_rows, start=1):
        value = row.get(child_column, "")
        if is_missing(value):
            continue
        if value not in parent_values:
            issues.append(
                QualityIssue(
                    check_id=f"relationship_{child_column}",
                    dimension="consistency",
                    severity=severity,
                    table=child_table,
                    column=child_column,
                    row_id=row.get(key_column) or f"row-{index}",
                    message=(
                        f"{child_column}={value} does not exist in "
                        f"{parent_table}.{parent_column}."
                    ),
                )
            )
    return issues


def check_accepted_values(
    rows: Iterable[dict[str, str]],
    *,
    table: str,
    column: str,
    accepted_values: set[str],
    key_column: str,
    severity: str = "warning",
) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    for index, row in enumerate(rows, start=1):
        value = row.get(column, "")
        if is_missing(value):
            continue
        if value not in accepted_values:
            issues.append(
                QualityIssue(
                    check_id=f"accepted_values_{column}",
                    dimension="validity",
                    severity=severity,
                    table=table,
                    column=column,
                    row_id=row.get(key_column) or f"row-{index}",
                    message=f"{column}={value} is outside {sorted(accepted_values)}.",
                )
            )
    return issues


def check_positive_number(
    rows: Iterable[dict[str, str]],
    *,
    table: str,
    column: str,
    key_column: str,
    severity: str = "error",
) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    for index, row in enumerate(rows, start=1):
        value = row.get(column, "")
        if is_missing(value):
            continue
        try:
            numeric_value = float(value)
        except ValueError:
            numeric_value = 0
        if numeric_value <= 0:
            issues.append(
                QualityIssue(
                    check_id=f"positive_{column}",
                    dimension="validity",
                    severity=severity,
                    table=table,
                    column=column,
                    row_id=row.get(key_column) or f"row-{index}",
                    message=f"{column}={value} must be positive.",
                )
            )
    return issues


def check_date_order(
    rows: Iterable[dict[str, str]],
    *,
    table: str,
    start_column: str,
    end_column: str,
    key_column: str,
    check_id: str,
    severity: str = "error",
) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    for index, row in enumerate(rows, start=1):
        start_date = parse_iso_date(row.get(start_column, ""))
        end_date = parse_iso_date(row.get(end_column, ""))
        if start_date is None or end_date is None:
            continue
        if end_date < start_date:
            issues.append(
                QualityIssue(
                    check_id=check_id,
                    dimension="consistency",
                    severity=severity,
                    table=table,
                    column=end_column,
                    row_id=row.get(key_column) or f"row-{index}",
                    message=f"{end_column} is earlier than {start_column}.",
                )
            )
    return issues
