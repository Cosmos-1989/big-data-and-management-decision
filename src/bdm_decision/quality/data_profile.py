"""Data profiling utilities."""

from __future__ import annotations

from dataclasses import dataclass

from bdm_decision.quality.checks import is_missing


@dataclass(frozen=True)
class ColumnProfile:
    column: str
    row_count: int
    missing_count: int
    distinct_count: int
    min_value: str | None
    max_value: str | None

    @property
    def missing_rate(self) -> float:
        return self.missing_count / self.row_count if self.row_count else 0.0


def profile_table(rows: list[dict[str, str]]) -> list[ColumnProfile]:
    if not rows:
        return []
    columns = list(rows[0].keys())
    profiles: list[ColumnProfile] = []
    for column in columns:
        values = [row.get(column, "") for row in rows]
        non_missing = [value for value in values if not is_missing(value)]
        profiles.append(
            ColumnProfile(
                column=column,
                row_count=len(rows),
                missing_count=len(values) - len(non_missing),
                distinct_count=len(set(non_missing)),
                min_value=min(non_missing) if non_missing else None,
                max_value=max(non_missing) if non_missing else None,
            )
        )
    return profiles


def render_profile_markdown(profiles: list[ColumnProfile]) -> str:
    header = "| column | rows | missing | missing_rate | distinct | min | max |\n"
    separator = "|---|---:|---:|---:|---:|---|---|\n"
    rows = []
    for profile in profiles:
        rows.append(
            "| "
            + " | ".join(
                [
                    profile.column,
                    str(profile.row_count),
                    str(profile.missing_count),
                    f"{profile.missing_rate:.3f}",
                    str(profile.distinct_count),
                    str(profile.min_value or ""),
                    str(profile.max_value or ""),
                ]
            )
            + " |\n"
        )
    return header + separator + "".join(rows)
