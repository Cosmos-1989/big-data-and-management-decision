"""Week 04 case: data quality profiling, validation, and governance reporting."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from bdm_decision.quality.checks import QualityIssue
from bdm_decision.quality.data_profile import profile_table, render_profile_markdown
from bdm_decision.quality.validation_rules import validate_orders_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_week04_dataset(dirty: bool = True) -> dict[str, list[dict[str, str]]]:
    order_file = "orders_quality_issues.csv" if dirty else "orders.csv"
    return {
        "customers": load_csv_rows(SAMPLE_DIR / "customers.csv"),
        "products": load_csv_rows(SAMPLE_DIR / "products.csv"),
        "orders": load_csv_rows(SAMPLE_DIR / order_file),
    }


def quality_report(dirty: bool = True) -> dict[str, object]:
    dataset = load_week04_dataset(dirty=dirty)
    issues = validate_orders_dataset(dataset)
    by_severity = Counter(issue.severity for issue in issues)
    by_dimension = Counter(issue.dimension for issue in issues)
    return {
        "dirty": dirty,
        "row_count": len(dataset["orders"]),
        "profiles": profile_table(dataset["orders"]),
        "issues": issues,
        "issue_count": len(issues),
        "by_severity": dict(sorted(by_severity.items())),
        "by_dimension": dict(sorted(by_dimension.items())),
    }


def issues_as_dicts(issues: list[QualityIssue]) -> list[dict[str, str]]:
    return [asdict(issue) for issue in issues]


def render_issues_markdown(issues: list[QualityIssue]) -> str:
    header = "| severity | dimension | check_id | row_id | column | message |\n"
    separator = "|---|---|---|---|---|---|\n"
    rows = []
    for issue in issues:
        rows.append(
            "| "
            + " | ".join(
                [
                    issue.severity,
                    issue.dimension,
                    issue.check_id,
                    issue.row_id,
                    issue.column,
                    issue.message,
                ]
            )
            + " |\n"
        )
    return header + separator + "".join(rows)


def render_quality_report_markdown(dirty: bool = True) -> str:
    report = quality_report(dirty=dirty)
    lines = [
        "# Week 04 Data Quality Report",
        "",
        f"- dirty dataset: {report['dirty']}",
        f"- order rows: {report['row_count']}",
        f"- issue count: {report['issue_count']}",
        f"- by severity: {report['by_severity']}",
        f"- by dimension: {report['by_dimension']}",
        "",
        "## Column profile",
        "",
        render_profile_markdown(report["profiles"]),
        "",
        "## Failing records",
        "",
        render_issues_markdown(report["issues"]),
    ]
    return "\n".join(lines)


def main() -> None:
    print(render_quality_report_markdown(dirty=True))


if __name__ == "__main__":
    main()

