"""Week 10 process mining case: order-to-cash event log analysis."""

from __future__ import annotations

from bdm_decision.process_mining.event_log import (
    activity_frequencies,
    average_throughput,
    bottleneck_transition,
    conformance_issues,
    directly_follows_graph,
    load_event_log,
    summarize_cases,
    summarize_variants,
)


def render_process_mining_report_markdown() -> str:
    """Render a concise Markdown report for the week-10 process mining case."""

    events = load_event_log()
    cases = summarize_cases(events)
    variants = summarize_variants(cases)
    transitions = directly_follows_graph(events)
    bottleneck = bottleneck_transition(transitions)
    frequencies = activity_frequencies(events)
    issues = conformance_issues(cases)
    rework_cases = [case.case_id for case in cases if case.has_rework]

    lines = [
        "# Week 10 Process Mining Report",
        "",
        "## Event-log summary",
        "",
        f"- events: {len(events)}",
        f"- cases: {len(cases)}",
        f"- variants: {len(variants)}",
        f"- average throughput hours: {average_throughput(cases):.2f}",
        f"- rework cases: {', '.join(rework_cases)}",
        "",
        "## Top variants",
        "",
        "| variant | cases | share | average_throughput | trace |",
        "|---|---:|---:|---:|---|",
    ]
    for variant in variants:
        trace = " > ".join(variant.trace)
        lines.append(
            f"| {variant.variant_id} | {variant.case_count} | {variant.share:.2%} | "
            f"{variant.average_throughput_hours:.2f} | {trace} |"
        )

    lines.extend(
        [
            "",
            "## Directly-follows graph",
            "",
            "| edge | count | average_elapsed_hours |",
            "|---|---:|---:|",
        ]
    )
    for transition in transitions[:8]:
        lines.append(
            f"| {transition.source} > {transition.target} | {transition.count} | "
            f"{transition.average_elapsed_hours:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Bottleneck and conformance",
            "",
            (
                f"- slowest average edge: {bottleneck.source} > {bottleneck.target} "
                f"({bottleneck.average_elapsed_hours:.2f} hours)"
            ),
            f"- conformance issues: {len(issues)}",
            "",
            "| case | issue |",
            "|---|---|",
        ]
    )
    for issue in issues:
        lines.append(f"| {issue.case_id} | {issue.issue} |")

    lines.extend(
        [
            "",
            "## Activity frequencies",
            "",
            "| activity | count |",
            "|---|---:|",
        ]
    )
    for activity, count in frequencies.most_common():
        lines.append(f"| {activity} | {count} |")

    lines.extend(
        [
            "",
            "## Management note",
            "",
            (
                "The process evidence points to payment delay, rework, and conformance "
                "exceptions as practical improvement targets.  Before redesigning the "
                "workflow, the team should validate timestamp quality, clarify allowed "
                "skip paths, and connect event-log findings back to order value and "
                "customer impact."
            ),
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    print(render_process_mining_report_markdown())

