"""Minimal dependency-free HTML dashboard utilities for week 05."""

from __future__ import annotations

from html import escape

from bdm_decision.cases.week05_statistics_dashboard import (
    DailyOperation,
    dashboard_kpis,
    load_daily_operations,
)


def _scale(value: float, low: float, high: float, size: int) -> float:
    if high == low:
        return size / 2
    return (value - low) / (high - low) * size


def _line_chart_svg(rows: list[DailyOperation], field: str, width: int = 720, height: int = 180) -> str:
    padding_left = 44
    padding_bottom = 28
    plot_width = width - padding_left - 20
    plot_height = height - 30 - padding_bottom
    values = [float(getattr(row, field)) for row in rows]
    low, high = min(values), max(values)
    if low == high:
        low -= 1
        high += 1
    points = []
    for index, row in enumerate(rows):
        x = padding_left + index / max(len(rows) - 1, 1) * plot_width
        y = 20 + plot_height - _scale(float(getattr(row, field)), low, high, plot_height)
        points.append((x, y, row.date, float(getattr(row, field))))
    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in points)
    circles = "\n".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3"><title>{escape(date)}: {value:.2f}</title></circle>'
        for x, y, date, value in points
    )
    return f"""
<svg viewBox="0 0 {width} {height}" role="img" aria-label="{escape(field)} trend">
  <line x1="{padding_left}" y1="{20 + plot_height}" x2="{width - 20}" y2="{20 + plot_height}" />
  <line x1="{padding_left}" y1="20" x2="{padding_left}" y2="{20 + plot_height}" />
  <polyline points="{polyline}" />
  {circles}
  <text x="{padding_left}" y="{height - 6}">{escape(rows[0].date)}</text>
  <text x="{width - 112}" y="{height - 6}">{escape(rows[-1].date)}</text>
  <text x="4" y="24">{high:.0f}</text>
  <text x="4" y="{20 + plot_height}">{low:.0f}</text>
</svg>
"""


def render_dashboard_html(rows: list[DailyOperation] | None = None) -> str:
    rows = rows or load_daily_operations()
    kpis = dashboard_kpis(rows)
    cards = [
        ("Total revenue", f"{kpis['total_revenue']:,.0f}"),
        ("On-time rate", f"{kpis['on_time_rate']:.1%}"),
        ("Avg delay days", f"{kpis['average_delay_days']:.2f}"),
        ("Latest backlog", f"{int(kpis['latest_backlog_orders'])}"),
        ("Quality issues", f"{int(kpis['quality_issue_count'])}"),
    ]
    card_html = "\n".join(
        f'<section class="metric"><span>{escape(label)}</span><strong>{escape(value)}</strong></section>'
        for label, value in cards
    )
    rows_html = "\n".join(
        "<tr>"
        f"<td>{escape(row.date)}</td>"
        f"<td>{row.revenue:,.0f}</td>"
        f"<td>{row.on_time_orders}/{row.delivered_orders}</td>"
        f"<td>{row.average_delay_days:.1f}</td>"
        f"<td>{row.backlog_orders}</td>"
        f"<td>{row.quality_issue_count}</td>"
        "</tr>"
        for row in rows
    )
    revenue_chart = _line_chart_svg(rows, "revenue")
    backlog_chart = _line_chart_svg(rows, "backlog_orders")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>Week 05 Operating Dashboard</title>
  <style>
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #1f2933;
      background: #f5f7fa;
    }}
    main {{
      max-width: 980px;
      margin: 0 auto;
      padding: 28px;
    }}
    h1, h2 {{
      font-weight: 500;
      margin: 0 0 14px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
      margin: 18px 0 22px;
    }}
    .metric {{
      background: #fff;
      border: 1px solid #d9e2ec;
      border-radius: 6px;
      padding: 14px;
    }}
    .metric span {{
      display: block;
      color: #52616f;
      font-size: 13px;
    }}
    .metric strong {{
      display: block;
      margin-top: 8px;
      font-size: 24px;
      font-weight: 500;
    }}
    .panel {{
      background: #fff;
      border: 1px solid #d9e2ec;
      border-radius: 6px;
      padding: 18px;
      margin-bottom: 16px;
    }}
    svg {{
      width: 100%;
      height: auto;
    }}
    svg line {{
      stroke: #9fb3c8;
      stroke-width: 1;
    }}
    svg polyline {{
      fill: none;
      stroke: #1f6f8b;
      stroke-width: 2.4;
    }}
    svg circle {{
      fill: #b05a2a;
    }}
    svg text {{
      fill: #52616f;
      font-size: 12px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      border-bottom: 1px solid #e4e7eb;
      padding: 8px;
      text-align: right;
    }}
    th:first-child, td:first-child {{
      text-align: left;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Week 05 Operating Dashboard</h1>
    <p>描述统计、趋势、异常与经营沟通样例。</p>
    <section class="metrics">{card_html}</section>
    <section class="panel">
      <h2>Revenue trend</h2>
      {revenue_chart}
    </section>
    <section class="panel">
      <h2>Backlog trend</h2>
      {backlog_chart}
    </section>
    <section class="panel">
      <h2>Daily records</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th><th>Revenue</th><th>On-time</th><th>Delay</th><th>Backlog</th><th>Quality issues</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    print(render_dashboard_html())


if __name__ == "__main__":
    main()

