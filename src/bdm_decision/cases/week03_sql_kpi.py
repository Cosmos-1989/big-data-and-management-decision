"""Week 03 case: SQL-style KPI definitions and pure Python verification."""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    label: str
    metric_type: str
    grain: str
    description: str
    numerator: str
    denominator: str
    unit: str
    dimensions: tuple[str, ...]
    owner: str


METRIC_DEFINITIONS = [
    MetricDefinition(
        name="revenue",
        label="Revenue",
        metric_type="simple",
        grain="order",
        description="Standard sales amount computed from order quantity and product price.",
        numerator="sum(quantity * unit_price)",
        denominator="",
        unit="currency",
        dimensions=("region", "segment", "category", "channel"),
        owner="finance",
    ),
    MetricDefinition(
        name="gross_margin",
        label="Gross margin",
        metric_type="ratio",
        grain="order",
        description="Gross profit divided by revenue at the requested analysis grain.",
        numerator="sum(quantity * (unit_price - unit_cost))",
        denominator="sum(quantity * unit_price)",
        unit="ratio",
        dimensions=("region", "segment", "category", "channel"),
        owner="finance",
    ),
    MetricDefinition(
        name="on_time_delivery_rate",
        label="On-time delivery rate",
        metric_type="ratio",
        grain="delivered_order",
        description="Delivered orders whose actual date is no later than promised date.",
        numerator="sum(case when actual_date <= promised_date then 1 else 0 end)",
        denominator="count(delivered orders)",
        unit="ratio",
        dimensions=("region", "segment", "category", "priority", "channel"),
        owner="operations",
    ),
]


def parse_date(value: str) -> date | None:
    if value == "":
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_sample_dataset(sample_dir: Path = SAMPLE_DIR) -> dict[str, list[dict[str, str]]]:
    return {
        "customers": load_csv_rows(sample_dir / "customers.csv"),
        "products": load_csv_rows(sample_dir / "products.csv"),
        "orders": load_csv_rows(sample_dir / "orders.csv"),
        "inventory": load_csv_rows(sample_dir / "inventory.csv"),
    }


def index_unique(rows: Iterable[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row[key]
        if value in indexed:
            raise ValueError(f"Duplicate key {value!r} for {key}")
        indexed[value] = row
    return indexed


def enrich_orders(dataset: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    customers = index_unique(dataset["customers"], "customer_id")
    products = index_unique(dataset["products"], "product_id")
    enriched: list[dict[str, object]] = []

    for order in dataset["orders"]:
        customer = customers[order["customer_id"]]
        product = products[order["product_id"]]
        quantity = int(order["quantity"])
        unit_price = float(product["unit_price"])
        unit_cost = float(product["unit_cost"])
        order_date = parse_date(order["order_date"])
        promised_date = parse_date(order["promised_date"])
        actual_date = parse_date(order["actual_date"])
        if order_date is None or promised_date is None:
            raise ValueError(f"Order {order['order_id']} has missing required dates")
        if actual_date is None:
            delay_days = None
            on_time_flag = None
        else:
            delay_days = max((actual_date - promised_date).days, 0)
            on_time_flag = 1 if actual_date <= promised_date else 0

        revenue = quantity * unit_price
        gross_profit = quantity * (unit_price - unit_cost)
        enriched.append(
            {
                "order_id": order["order_id"],
                "customer_id": order["customer_id"],
                "product_id": order["product_id"],
                "order_date": order_date,
                "month": order_date.strftime("%Y-%m"),
                "quantity": quantity,
                "promised_date": promised_date,
                "actual_date": actual_date,
                "channel": order["channel"],
                "priority": order["priority"],
                "customer_name": customer["customer_name"],
                "region": customer["region"],
                "segment": customer["segment"],
                "product_name": product["product_name"],
                "category": product["category"],
                "unit_price": unit_price,
                "unit_cost": unit_cost,
                "revenue": revenue,
                "gross_profit": gross_profit,
                "on_time_flag": on_time_flag,
                "delay_days": delay_days,
            }
        )
    return enriched


def summarize_by(
    rows: Iterable[dict[str, object]],
    group_keys: tuple[str, ...],
) -> list[dict[str, object]]:
    buckets: dict[tuple[object, ...], dict[str, float]] = defaultdict(
        lambda: {
            "orders": 0.0,
            "delivered_orders": 0.0,
            "revenue": 0.0,
            "gross_profit": 0.0,
            "on_time_orders": 0.0,
            "delay_days": 0.0,
        }
    )
    for row in rows:
        key = tuple(row[group_key] for group_key in group_keys)
        bucket = buckets[key]
        bucket["orders"] += 1
        bucket["revenue"] += float(row["revenue"])
        bucket["gross_profit"] += float(row["gross_profit"])
        if row["actual_date"] is not None:
            bucket["delivered_orders"] += 1
            bucket["on_time_orders"] += float(row["on_time_flag"])
            bucket["delay_days"] += float(row["delay_days"])

    summaries: list[dict[str, object]] = []
    for key, bucket in buckets.items():
        delivered_orders = int(bucket["delivered_orders"])
        revenue = bucket["revenue"]
        gross_profit = bucket["gross_profit"]
        summary = {group_keys[index]: value for index, value in enumerate(key)}
        summary.update(
            {
                "orders": int(bucket["orders"]),
                "delivered_orders": delivered_orders,
                "revenue": round(revenue, 2),
                "gross_profit": round(gross_profit, 2),
                "gross_margin": gross_profit / revenue if revenue else None,
                "on_time_rate": bucket["on_time_orders"] / delivered_orders
                if delivered_orders
                else None,
                "average_delay_days": bucket["delay_days"] / delivered_orders
                if delivered_orders
                else None,
            }
        )
        summaries.append(summary)
    return sorted(summaries, key=lambda item: tuple(str(item[key]) for key in group_keys))


def monthly_kpi_summary(dataset: dict[str, list[dict[str, str]]] | None = None) -> list[dict[str, object]]:
    dataset = dataset or load_sample_dataset()
    return summarize_by(enrich_orders(dataset), ("month",))


def region_kpi_summary(dataset: dict[str, list[dict[str, str]]] | None = None) -> list[dict[str, object]]:
    dataset = dataset or load_sample_dataset()
    return summarize_by(enrich_orders(dataset), ("region",))


def rolling_customer_revenue(
    dataset: dict[str, list[dict[str, str]]] | None = None,
    window: int = 3,
) -> list[dict[str, object]]:
    dataset = dataset or load_sample_dataset()
    rows = enrich_orders(dataset)
    by_customer: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_customer[str(row["customer_id"])].append(row)

    output: list[dict[str, object]] = []
    for customer_id, customer_rows in sorted(by_customer.items()):
        customer_rows.sort(key=lambda item: (item["order_date"], item["order_id"]))
        for index, row in enumerate(customer_rows):
            recent_rows = customer_rows[max(0, index - window + 1) : index + 1]
            output.append(
                {
                    "customer_id": customer_id,
                    "order_id": row["order_id"],
                    "order_date": row["order_date"],
                    "revenue": row["revenue"],
                    "recent_revenue": round(sum(float(item["revenue"]) for item in recent_rows), 2),
                    "customer_order_sequence": index + 1,
                }
            )
    return output


def metric_dictionary() -> list[MetricDefinition]:
    return METRIC_DEFINITIONS


def render_summary_table(rows: list[dict[str, object]], group_key: str) -> str:
    header = (
        f"| {group_key} | orders | revenue | gross_margin | on_time_rate | average_delay_days |\n"
        "|---|---:|---:|---:|---:|---:|\n"
    )
    body = []
    for row in rows:
        body.append(
            "| "
            + " | ".join(
                [
                    str(row[group_key]),
                    str(row["orders"]),
                    f"{float(row['revenue']):.2f}",
                    f"{float(row['gross_margin']):.4f}",
                    f"{float(row['on_time_rate']):.4f}",
                    f"{float(row['average_delay_days']):.2f}",
                ]
            )
            + " |\n"
        )
    return header + "".join(body)


def main() -> None:
    dataset = load_sample_dataset()
    print("## Monthly KPI summary")
    print(render_summary_table(monthly_kpi_summary(dataset), "month"))
    print("## Region KPI summary")
    print(render_summary_table(region_kpi_summary(dataset), "region"))
    print("## Rolling customer revenue")
    for row in rolling_customer_revenue(dataset)[:8]:
        print(row)


if __name__ == "__main__":
    main()

