"""Event-log analysis utilities for week 10 process mining examples."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_EVENT_LOG = (
    Path(__file__).resolve().parents[3] / "data" / "sample" / "order_to_cash_event_log.csv"
)


@dataclass(frozen=True)
class EventRecord:
    """One timestamped event in a process instance."""

    case_id: str
    event_id: str
    activity: str
    timestamp: datetime
    resource: str
    order_value: float
    region: str


@dataclass(frozen=True)
class CaseSummary:
    """Trace-level summary for one process instance."""

    case_id: str
    trace: tuple[str, ...]
    start_time: datetime
    end_time: datetime
    throughput_hours: float
    event_count: int
    has_rework: bool
    region: str
    order_value: float


@dataclass(frozen=True)
class VariantSummary:
    """A distinct activity sequence and its frequency."""

    variant_id: str
    trace: tuple[str, ...]
    case_count: int
    share: float
    average_throughput_hours: float


@dataclass(frozen=True)
class TransitionSummary:
    """Directly-follows edge summary."""

    source: str
    target: str
    count: int
    average_elapsed_hours: float


@dataclass(frozen=True)
class ConformanceIssue:
    """Simple conformance warning for one case."""

    case_id: str
    issue: str


def load_event_log(path: str | Path = DEFAULT_EVENT_LOG) -> list[EventRecord]:
    """Load the week-10 event log sample."""

    events: list[EventRecord] = []
    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            events.append(
                EventRecord(
                    case_id=row["case_id"],
                    event_id=row["event_id"],
                    activity=row["activity"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    resource=row["resource"],
                    order_value=float(row["order_value"]),
                    region=row["region"],
                )
            )
    return sorted(events, key=lambda event: (event.case_id, event.timestamp, event.event_id))


def group_events_by_case(events: Iterable[EventRecord]) -> dict[str, list[EventRecord]]:
    """Group events by case id and sort each trace chronologically."""

    grouped: dict[str, list[EventRecord]] = defaultdict(list)
    for event in events:
        grouped[event.case_id].append(event)
    return {
        case_id: sorted(case_events, key=lambda event: (event.timestamp, event.event_id))
        for case_id, case_events in grouped.items()
    }


def summarize_cases(events: Sequence[EventRecord]) -> list[CaseSummary]:
    """Compute trace, throughput time, and rework flags for each case."""

    summaries: list[CaseSummary] = []
    for case_id, case_events in sorted(group_events_by_case(events).items()):
        trace = tuple(event.activity for event in case_events)
        start = case_events[0].timestamp
        end = case_events[-1].timestamp
        summaries.append(
            CaseSummary(
                case_id=case_id,
                trace=trace,
                start_time=start,
                end_time=end,
                throughput_hours=(end - start).total_seconds() / 3600,
                event_count=len(case_events),
                has_rework=any("rework" in activity for activity in trace)
                or len(set(trace)) < len(trace),
                region=case_events[0].region,
                order_value=case_events[0].order_value,
            )
        )
    return summaries


def summarize_variants(case_summaries: Sequence[CaseSummary]) -> list[VariantSummary]:
    """Summarize distinct trace variants."""

    by_trace: dict[tuple[str, ...], list[CaseSummary]] = defaultdict(list)
    for summary in case_summaries:
        by_trace[summary.trace].append(summary)

    total_cases = len(case_summaries)
    variants = []
    for index, (trace, cases) in enumerate(
        sorted(by_trace.items(), key=lambda item: (-len(item[1]), item[0])),
        start=1,
    ):
        variants.append(
            VariantSummary(
                variant_id=f"V{index:02d}",
                trace=trace,
                case_count=len(cases),
                share=len(cases) / total_cases,
                average_throughput_hours=sum(case.throughput_hours for case in cases)
                / len(cases),
            )
        )
    return variants


def directly_follows_graph(events: Sequence[EventRecord]) -> list[TransitionSummary]:
    """Compute directly-follows edge counts and average elapsed times."""

    elapsed_by_edge: dict[tuple[str, str], list[float]] = defaultdict(list)
    for case_events in group_events_by_case(events).values():
        for current, following in zip(case_events, case_events[1:]):
            edge = (current.activity, following.activity)
            elapsed_by_edge[edge].append(
                (following.timestamp - current.timestamp).total_seconds() / 3600
            )

    return [
        TransitionSummary(
            source=source,
            target=target,
            count=len(values),
            average_elapsed_hours=sum(values) / len(values),
        )
        for (source, target), values in sorted(
            elapsed_by_edge.items(),
            key=lambda item: (-len(item[1]), item[0]),
        )
    ]


def bottleneck_transition(transitions: Sequence[TransitionSummary]) -> TransitionSummary:
    """Return the edge with the largest average elapsed time."""

    if not transitions:
        raise ValueError("at least one transition is required")
    return max(transitions, key=lambda transition: transition.average_elapsed_hours)


def activity_frequencies(events: Iterable[EventRecord]) -> Counter[str]:
    """Count events by activity."""

    return Counter(event.activity for event in events)


def conformance_issues(
    case_summaries: Sequence[CaseSummary],
    expected_order: Sequence[str] = (
        "order_received",
        "credit_check",
        "pick_items",
        "quality_check",
        "pack_order",
        "ship_order",
        "invoice_sent",
        "payment_received",
    ),
) -> list[ConformanceIssue]:
    """Detect missing expected activities and reversed activity order."""

    order_index = {activity: index for index, activity in enumerate(expected_order)}
    issues: list[ConformanceIssue] = []
    for summary in case_summaries:
        trace = summary.trace
        for activity in expected_order:
            if activity not in trace:
                issues.append(ConformanceIssue(summary.case_id, f"missing {activity}"))
        seen_positions = [
            order_index[activity] for activity in trace if activity in order_index
        ]
        if seen_positions != sorted(seen_positions):
            issues.append(ConformanceIssue(summary.case_id, "activity order violation"))
    return issues


def average_throughput(case_summaries: Sequence[CaseSummary]) -> float:
    """Average case throughput in hours."""

    if not case_summaries:
        raise ValueError("at least one case summary is required")
    return sum(case.throughput_hours for case in case_summaries) / len(case_summaries)
