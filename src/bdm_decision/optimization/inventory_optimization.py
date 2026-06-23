"""Inventory optimization utilities for prescriptive analytics examples."""

from __future__ import annotations

import csv
import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_REPLENISHMENT_DATA = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "sample"
    / "replenishment_planning.csv"
)


@dataclass(frozen=True)
class DemandScenario:
    """A discrete demand scenario for one product."""

    demand: int
    probability: float


@dataclass(frozen=True)
class ProductPolicy:
    """Input policy and demand forecast for a product."""

    product_id: str
    product_name: str
    unit_cost: float
    contribution_margin: float
    holding_cost: float
    stockout_penalty: float
    current_inventory: int
    max_order_quantity: int
    storage_per_unit: float
    scenarios: tuple[DemandScenario, ...]


@dataclass(frozen=True)
class QuantityEvaluation:
    """Expected outcome of choosing one order quantity for a product."""

    product_id: str
    order_quantity: int
    expected_sales: float
    expected_leftover: float
    expected_unmet_demand: float
    procurement_cost: float
    expected_net_value: float
    budget_used: float
    storage_used: float


@dataclass(frozen=True)
class ReplenishmentPlan:
    """Optimal replenishment plan under budget and storage constraints."""

    decisions: tuple[QuantityEvaluation, ...]
    budget_limit: float
    storage_limit: float
    total_budget_used: float
    total_storage_used: float
    total_expected_net_value: float


def load_product_policies(path: str | Path = DEFAULT_REPLENISHMENT_DATA) -> list[ProductPolicy]:
    """Load product policies and three-point demand forecasts from CSV."""

    policies: list[ProductPolicy] = []
    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            scenarios = (
                DemandScenario(int(row["demand_low"]), float(row["prob_low"])),
                DemandScenario(int(row["demand_base"]), float(row["prob_base"])),
                DemandScenario(int(row["demand_high"]), float(row["prob_high"])),
            )
            probability_sum = sum(scenario.probability for scenario in scenarios)
            if round(probability_sum, 8) != 1.0:
                raise ValueError(f"scenario probabilities must sum to 1 for {row['product_id']}")
            policies.append(
                ProductPolicy(
                    product_id=row["product_id"],
                    product_name=row["product_name"],
                    unit_cost=float(row["unit_cost"]),
                    contribution_margin=float(row["contribution_margin"]),
                    holding_cost=float(row["holding_cost"]),
                    stockout_penalty=float(row["stockout_penalty"]),
                    current_inventory=int(row["current_inventory"]),
                    max_order_quantity=int(row["max_order_quantity"]),
                    storage_per_unit=float(row["storage_per_unit"]),
                    scenarios=scenarios,
                )
            )
    return policies


def evaluate_order_quantity(policy: ProductPolicy, order_quantity: int) -> QuantityEvaluation:
    """Evaluate expected net value for one product and one order quantity."""

    if order_quantity < 0 or order_quantity > policy.max_order_quantity:
        raise ValueError("order_quantity must be within [0, max_order_quantity]")

    available = policy.current_inventory + order_quantity
    expected_sales = 0.0
    expected_leftover = 0.0
    expected_unmet = 0.0
    for scenario in policy.scenarios:
        sales = min(available, scenario.demand)
        leftover = max(available - scenario.demand, 0)
        unmet = max(scenario.demand - available, 0)
        expected_sales += scenario.probability * sales
        expected_leftover += scenario.probability * leftover
        expected_unmet += scenario.probability * unmet

    procurement_cost = policy.unit_cost * order_quantity
    expected_net_value = (
        policy.contribution_margin * expected_sales
        - policy.holding_cost * expected_leftover
        - policy.stockout_penalty * expected_unmet
        - procurement_cost
    )
    return QuantityEvaluation(
        product_id=policy.product_id,
        order_quantity=order_quantity,
        expected_sales=expected_sales,
        expected_leftover=expected_leftover,
        expected_unmet_demand=expected_unmet,
        procurement_cost=procurement_cost,
        expected_net_value=expected_net_value,
        budget_used=procurement_cost,
        storage_used=policy.storage_per_unit * order_quantity,
    )


def enumerate_product_evaluations(policy: ProductPolicy) -> list[QuantityEvaluation]:
    """Evaluate every feasible order quantity for one product."""

    return [
        evaluate_order_quantity(policy, quantity)
        for quantity in range(policy.max_order_quantity + 1)
    ]


def optimize_replenishment(
    policies: Sequence[ProductPolicy],
    budget_limit: float,
    storage_limit: float,
) -> ReplenishmentPlan:
    """Find the best product-level replenishment plan by exhaustive enumeration."""

    if budget_limit < 0 or storage_limit < 0:
        raise ValueError("budget_limit and storage_limit must be nonnegative")
    if not policies:
        raise ValueError("at least one product policy is required")

    evaluations_by_product = [enumerate_product_evaluations(policy) for policy in policies]
    best_combo: tuple[QuantityEvaluation, ...] | None = None
    best_value: float | None = None

    for combo in itertools.product(*evaluations_by_product):
        budget_used = sum(item.budget_used for item in combo)
        storage_used = sum(item.storage_used for item in combo)
        if budget_used > budget_limit or storage_used > storage_limit:
            continue
        value = sum(item.expected_net_value for item in combo)
        if best_value is None or value > best_value:
            best_value = value
            best_combo = tuple(combo)

    if best_combo is None or best_value is None:
        raise ValueError("no feasible replenishment plan found")

    return ReplenishmentPlan(
        decisions=best_combo,
        budget_limit=budget_limit,
        storage_limit=storage_limit,
        total_budget_used=sum(item.budget_used for item in best_combo),
        total_storage_used=sum(item.storage_used for item in best_combo),
        total_expected_net_value=best_value,
    )


def marginal_values(policy: ProductPolicy) -> list[float]:
    """Return incremental expected net value from each additional ordered unit."""

    evaluations = enumerate_product_evaluations(policy)
    return [
        evaluations[index].expected_net_value - evaluations[index - 1].expected_net_value
        for index in range(1, len(evaluations))
    ]


def format_plan_table(
    plan: ReplenishmentPlan,
    policies: Iterable[ProductPolicy],
) -> list[dict[str, float | int | str]]:
    """Return a table-friendly representation of a replenishment plan."""

    names = {policy.product_id: policy.product_name for policy in policies}
    return [
        {
            "product_id": decision.product_id,
            "product_name": names[decision.product_id],
            "order_quantity": decision.order_quantity,
            "expected_sales": round(decision.expected_sales, 2),
            "expected_leftover": round(decision.expected_leftover, 2),
            "expected_unmet_demand": round(decision.expected_unmet_demand, 2),
            "budget_used": round(decision.budget_used, 2),
            "storage_used": round(decision.storage_used, 2),
            "expected_net_value": round(decision.expected_net_value, 2),
        }
        for decision in plan.decisions
    ]
