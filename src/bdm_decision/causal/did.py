"""Difference-in-differences utilities for management intervention analysis."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


DEFAULT_DID_PANEL = (
    Path(__file__).resolve().parents[3] / "data" / "sample" / "coupon_retention_panel.csv"
)


@dataclass(frozen=True)
class PanelRecord:
    """One unit-period observation for a two-period DID design."""

    unit_id: str
    group: str
    period: str
    retention_rate: float


@dataclass(frozen=True)
class DiDEstimate:
    """Two-period difference-in-differences estimate."""

    treated_pre: float
    treated_post: float
    control_pre: float
    control_post: float
    treated_change: float
    control_change: float
    did: float


def load_panel_records(path: str | Path = DEFAULT_DID_PANEL) -> list[PanelRecord]:
    """Load the week-08 two-period panel sample."""

    records: list[PanelRecord] = []
    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(
                PanelRecord(
                    unit_id=row["unit_id"],
                    group=row["group"],
                    period=row["period"],
                    retention_rate=float(row["retention_rate"]),
                )
            )
    return records


def average_outcomes_by_group_period(
    records: Sequence[PanelRecord],
    outcome: str = "retention_rate",
) -> dict[tuple[str, str], float]:
    """Return mean outcome for each group-period cell."""

    result: dict[tuple[str, str], float] = {}
    keys = sorted({(record.group, record.period) for record in records})
    for key in keys:
        group, period = key
        values = [
            float(getattr(record, outcome))
            for record in records
            if record.group == group and record.period == period
        ]
        if not values:
            raise ValueError(f"empty group-period cell: {key}")
        result[key] = sum(values) / len(values)
    return result


def difference_in_differences(
    records: Sequence[PanelRecord],
    outcome: str = "retention_rate",
    treated_group: str = "treated",
    control_group: str = "control",
    pre_period: str = "pre",
    post_period: str = "post",
) -> DiDEstimate:
    """Estimate the two-period DID contrast."""

    means = average_outcomes_by_group_period(records, outcome=outcome)
    treated_pre = means[(treated_group, pre_period)]
    treated_post = means[(treated_group, post_period)]
    control_pre = means[(control_group, pre_period)]
    control_post = means[(control_group, post_period)]
    treated_change = treated_post - treated_pre
    control_change = control_post - control_pre
    return DiDEstimate(
        treated_pre=treated_pre,
        treated_post=treated_post,
        control_pre=control_pre,
        control_post=control_post,
        treated_change=treated_change,
        control_change=control_change,
        did=treated_change - control_change,
    )
