"""Small capacity-allocation helpers for optimization teaching examples."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class AllocationOption:
    """One optional use of limited operational capacity."""

    item_id: str
    capacity_required: float
    expected_value: float


@dataclass(frozen=True)
class AllocationResult:
    """Best subset of options under one capacity limit."""

    selected: tuple[AllocationOption, ...]
    capacity_limit: float
    capacity_used: float
    total_expected_value: float


def optimize_binary_allocation(
    options: Sequence[AllocationOption],
    capacity_limit: float,
) -> AllocationResult:
    """Solve a tiny 0-1 capacity allocation problem by enumeration."""

    if capacity_limit < 0:
        raise ValueError("capacity_limit must be nonnegative")

    best: tuple[AllocationOption, ...] = ()
    best_value = 0.0
    for mask in range(1 << len(options)):
        selected = tuple(option for index, option in enumerate(options) if mask & (1 << index))
        capacity_used = sum(option.capacity_required for option in selected)
        if capacity_used > capacity_limit:
            continue
        value = sum(option.expected_value for option in selected)
        if value > best_value:
            best = selected
            best_value = value

    return AllocationResult(
        selected=best,
        capacity_limit=capacity_limit,
        capacity_used=sum(option.capacity_required for option in best),
        total_expected_value=best_value,
    )
