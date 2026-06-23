"""Week 05 case: descriptive statistics and dashboard-ready summaries."""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean, median


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"


@dataclass(frozen=True)
class DailyOperation:
    date: str
    revenue: float
    orders: int
    delivered_orders: int
    on_time_orders: int
    average_delay_days: float
    backlog_orders: int
    quality_issue_count: int


@dataclass(frozen=True)
class SummaryStats:
    n: int
    mean: float
    median: float
    q1: float
    q3: float
    iqr: float
    sample_std: float
    coefficient_of_variation: float
    minimum: float
    maximum: float


def load_daily_operations(path: Path = SAMPLE_DIR / "daily_operations.csv") -> list[DailyOperation]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return [
            DailyOperation(
                date=row["date"],
                revenue=float(row["revenue"]),
                orders=int(row["orders"]),
                delivered_orders=int(row["delivered_orders"]),
                on_time_orders=int(row["on_time_orders"]),
                average_delay_days=float(row["average_delay_days"]),
                backlog_orders=int(row["backlog_orders"]),
                quality_issue_count=int(row["quality_issue_count"]),
            )
            for row in rows
        ]


def _median_of_sorted(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot compute median of an empty list")
    size = len(values)
    mid = size // 2
    if size % 2:
        return values[mid]
    return (values[mid - 1] + values[mid]) / 2


def tukey_quartiles(values: list[float]) -> tuple[float, float, float]:
    sorted_values = sorted(values)
    size = len(sorted_values)
    if size < 2:
        value = sorted_values[0]
        return value, value, value
    mid = size // 2
    if size % 2:
        lower = sorted_values[:mid]
        upper = sorted_values[mid + 1 :]
    else:
        lower = sorted_values[:mid]
        upper = sorted_values[mid:]
    return _median_of_sorted(lower), _median_of_sorted(sorted_values), _median_of_sorted(upper)


def descriptive_summary(values: list[float]) -> SummaryStats:
    if not values:
        raise ValueError("Cannot summarize an empty list")
    q1, q2, q3 = tukey_quartiles(values)
    avg = mean(values)
    if len(values) > 1:
        variance = sum((value - avg) ** 2 for value in values) / (len(values) - 1)
        sample_std = math.sqrt(variance)
    else:
        sample_std = 0.0
    return SummaryStats(
        n=len(values),
        mean=avg,
        median=q2,
        q1=q1,
        q3=q3,
        iqr=q3 - q1,
        sample_std=sample_std,
        coefficient_of_variation=sample_std / avg if avg else 0.0,
        minimum=min(values),
        maximum=max(values),
    )


def detect_iqr_outliers(values: list[float]) -> list[float]:
    q1, _, q3 = tukey_quartiles(values)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return [value for value in values if value < lower or value > upper]


def moving_average(values: list[float], window: int = 3) -> list[float]:
    if window <= 0:
        raise ValueError("window must be positive")
    result = []
    for index in range(len(values)):
        window_values = values[max(0, index - window + 1) : index + 1]
        result.append(mean(window_values))
    return result


def dashboard_kpis(rows: list[DailyOperation]) -> dict[str, float]:
    delivered_orders = sum(row.delivered_orders for row in rows)
    total_delay_days = sum(row.average_delay_days * row.delivered_orders for row in rows)
    total_revenue = sum(row.revenue for row in rows)
    return {
        "total_revenue": total_revenue,
        "average_daily_revenue": total_revenue / len(rows) if rows else 0.0,
        "on_time_rate": sum(row.on_time_orders for row in rows) / delivered_orders
        if delivered_orders
        else 0.0,
        "average_delay_days": total_delay_days / delivered_orders if delivered_orders else 0.0,
        "latest_backlog_orders": rows[-1].backlog_orders if rows else 0,
        "quality_issue_count": sum(row.quality_issue_count for row in rows),
    }


def dashboard_records(rows: list[DailyOperation]) -> list[dict[str, object]]:
    rolling_revenue = moving_average([row.revenue for row in rows], window=3)
    return [
        {
            "date": row.date,
            "revenue": row.revenue,
            "revenue_ma3": round(rolling_revenue[index], 2),
            "orders": row.orders,
            "on_time_rate": row.on_time_orders / row.delivered_orders
            if row.delivered_orders
            else None,
            "average_delay_days": row.average_delay_days,
            "backlog_orders": row.backlog_orders,
            "quality_issue_count": row.quality_issue_count,
        }
        for index, row in enumerate(rows)
    ]


def vega_lite_dashboard_spec(rows: list[DailyOperation] | None = None) -> dict[str, object]:
    rows = rows or load_daily_operations()
    data_values = dashboard_records(rows)
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Week 05 Operating Dashboard",
        "vconcat": [
            {
                "title": "Daily revenue and 3-observation moving average",
                "width": 560,
                "height": 180,
                "data": {"values": data_values},
                "layer": [
                    {
                        "mark": {"type": "bar", "color": "#477699"},
                        "encoding": {
                            "x": {"field": "date", "type": "temporal", "title": "Date"},
                            "y": {"field": "revenue", "type": "quantitative", "title": "Revenue"},
                        },
                    },
                    {
                        "mark": {"type": "line", "color": "#b05a2a", "point": True},
                        "encoding": {
                            "x": {"field": "date", "type": "temporal"},
                            "y": {
                                "field": "revenue_ma3",
                                "type": "quantitative",
                                "title": "Revenue",
                            },
                        },
                    },
                ],
            },
            {
                "title": "Backlog and data quality issues",
                "width": 560,
                "height": 160,
                "data": {"values": data_values},
                "layer": [
                    {
                        "mark": {"type": "line", "color": "#355c7d", "point": True},
                        "encoding": {
                            "x": {"field": "date", "type": "temporal", "title": "Date"},
                            "y": {
                                "field": "backlog_orders",
                                "type": "quantitative",
                                "title": "Backlog orders",
                            },
                        },
                    },
                    {
                        "mark": {"type": "point", "filled": True, "color": "#b23a48", "size": 80},
                        "encoding": {
                            "x": {"field": "date", "type": "temporal"},
                            "y": {
                                "field": "quality_issue_count",
                                "type": "quantitative",
                                "title": "Quality issues",
                            },
                        },
                    },
                ],
            },
        ],
    }


def render_statistics_markdown(rows: list[DailyOperation] | None = None) -> str:
    rows = rows or load_daily_operations()
    revenue_summary = descriptive_summary([row.revenue for row in rows])
    kpis = dashboard_kpis(rows)
    outliers = detect_iqr_outliers([row.revenue for row in rows])
    lines = [
        "# Week 05 Statistics and Dashboard Summary",
        "",
        f"- total revenue: {kpis['total_revenue']:.2f}",
        f"- average daily revenue: {kpis['average_daily_revenue']:.2f}",
        f"- on-time delivery rate: {kpis['on_time_rate']:.4f}",
        f"- average delay days: {kpis['average_delay_days']:.2f}",
        f"- latest backlog orders: {int(kpis['latest_backlog_orders'])}",
        f"- quality issue count: {int(kpis['quality_issue_count'])}",
        "",
        "## Revenue distribution",
        "",
        f"- n: {revenue_summary.n}",
        f"- mean: {revenue_summary.mean:.2f}",
        f"- median: {revenue_summary.median:.2f}",
        f"- q1: {revenue_summary.q1:.2f}",
        f"- q3: {revenue_summary.q3:.2f}",
        f"- iqr: {revenue_summary.iqr:.2f}",
        f"- sample std: {revenue_summary.sample_std:.2f}",
        f"- coefficient of variation: {revenue_summary.coefficient_of_variation:.4f}",
        f"- iqr outliers: {outliers}",
        "",
        "## Vega-Lite spec",
        "",
        "```json",
        json.dumps(vega_lite_dashboard_spec(rows), ensure_ascii=False, indent=2),
        "```",
    ]
    return "\n".join(lines)


def main() -> None:
    print(render_statistics_markdown())


if __name__ == "__main__":
    main()

