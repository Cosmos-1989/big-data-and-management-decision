#!/usr/bin/env python3
"""独立核对第三、四讲中容易混淆的查询语义与数学算例。"""
from __future__ import annotations

import json
import sqlite3
from fractions import Fraction


def run_checks() -> dict:
    checks = []
    details = {}

    def record(name: str, data: dict) -> None:
        checks.append({"id": name, "passed": True})
        details[name] = data

    def mean(values):
        return sum(values, Fraction(0)) / len(values)

    def covariance(xs, ys):
        xm, ym = mean(xs), mean(ys)
        return mean([(x - xm) * (y - ym) for x, y in zip(xs, ys)])

    db = sqlite3.connect(":memory:")
    try:
        # 逐条保存到期承诺，保留尚未交付订单 C。
        db.execute("CREATE TABLE commitments (id TEXT, due TEXT, delivered TEXT)")
        db.executemany(
            "INSERT INTO commitments VALUES (?, ?, ?)",
            [("A", "2026-09-02", "2026-09-02"),
             ("B", "2026-09-04", "2026-09-06"),
             ("C", "2026-09-06", None),
             ("D", "2026-09-07", "2026-09-07")],
        )
        rows = db.execute(
            "SELECT id, delivered <= due FROM commitments ORDER BY id"
        ).fetchall()
        assert rows == [("A", 1), ("B", 0), ("C", None), ("D", 1)]
        counts = db.execute(
            "SELECT COUNT(*), COUNT(delivered), SUM(delivered <= due), "
            "AVG(delivered <= due), AVG(CASE WHEN delivered <= due THEN 1 ELSE 0 END) "
            "FROM commitments WHERE due >= '2026-09-01' AND due < '2026-09-08'"
        ).fetchone()
        assert counts[:3] == (4, 3, 2)
        assert counts[3] == 2 / 3 and counts[4] == 1 / 2
        assert db.execute("SELECT id FROM commitments WHERE delivered > due").fetchall() == [("B",)]
        assert db.execute("SELECT COUNT(*) FROM commitments WHERE delivered = NULL").fetchone()[0] == 0
        assert db.execute("SELECT id FROM commitments WHERE delivered IS NULL").fetchall() == [("C",)]
        record("due-cohort-and-sql-null", {
            "comparison_values": rows, "all_due": counts[0], "delivered": counts[1],
            "on_time": counts[2], "due_otd": "1/2", "delivered_otd": "2/3",
            "where_late_only": ["B"], "unrecorded_delivery": ["C"],
        })

        # 订单连接多个事件会复制订单金额；先汇总事件或使用 EXISTS 可保留订单粒度。
        db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, amount INTEGER)")
        db.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, order_id INTEGER)")
        db.executemany("INSERT INTO orders VALUES (?, ?)", [(1, 100), (2, 200)])
        db.executemany("INSERT INTO events VALUES (?, ?)", [(11, 1), (12, 1), (21, 2)])
        source = db.execute("SELECT COUNT(*), SUM(amount) FROM orders").fetchone()
        joined = db.execute(
            "SELECT COUNT(*), SUM(o.amount) FROM orders o JOIN events e ON o.id=e.order_id"
        ).fetchone()
        aggregated = db.execute(
            "WITH grouped_events AS (SELECT order_id, COUNT(*) AS n FROM events GROUP BY order_id) "
            "SELECT COUNT(*), SUM(o.amount) FROM orders o JOIN grouped_events e ON o.id=e.order_id"
        ).fetchone()
        selected = db.execute(
            "SELECT COUNT(*), SUM(o.amount) FROM orders o "
            "WHERE EXISTS (SELECT 1 FROM events e WHERE e.order_id=o.id)"
        ).fetchone()
        assert source == aggregated == selected == (2, 300)
        assert joined == (3, 400)
        record("join-fanout", {"source": source, "joined": joined,
                               "event_preaggregation": aggregated, "exists_filter": selected})

        # 同一条记录的“近三行”与“当前日及前两日”可能包含不同的历史。
        db.execute("CREATE TABLE sales (id INTEGER PRIMARY KEY, day TEXT, amount INTEGER)")
        db.executemany("INSERT INTO sales VALUES (?, ?, ?)",
                       [(1, "2026-01-01", 10), (2, "2026-01-02", 20),
                        (3, "2026-01-20", 30), (4, "2026-01-21", 40)])
        windows = db.execute(
            "SELECT id, SUM(amount) OVER (ORDER BY day, id ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), "
            "SUM(amount) OVER (ORDER BY julianday(day) RANGE BETWEEN 2 PRECEDING AND CURRENT ROW) "
            "FROM sales ORDER BY day, id"
        ).fetchall()
        assert windows[-1] == (4, 90, 70)
        record("row-and-calendar-windows", {"all_rows": windows, "last_three_rows": 90,
                                             "current_and_previous_two_days": 70})
    finally:
        db.close()

    populations = [[1] * 90 + [0] * 10, [1] * 720 + [0] * 180]
    pooled = mean(populations[0] + populations[1])
    average_groups = mean([mean(x) for x in populations])
    assert pooled == Fraction(81, 100) and average_groups == Fraction(85, 100)
    record("pooled-yield", {"pooled": str(pooled), "unweighted_group_average": str(average_groups),
                             "group_sizes": list(map(len, populations))})

    # 每小时等长枚举，九小时为 10 件，最后一小时为 30 件。
    hourly_inventory = [10] * 9 + [30]
    time_average = mean(hourly_inventory)
    snapshot_average = mean([10, 30])
    assert time_average == 12 and snapshot_average == 20
    record("time-weighted-wip", {"hourly_levels": hourly_inventory,
                                  "time_average": str(time_average), "snapshot_average": str(snapshot_average)})

    full_durations = [2] * 80 + [12] * 20
    observed_durations = [2] * 80 + [12] * 5
    observed_mean = mean(observed_durations)
    true_mean = mean(full_durations)
    records = [1] * 85 + [0] * 15
    cov = covariance(list(map(Fraction, full_durations)), list(map(Fraction, records)))
    assert observed_mean == Fraction(44, 17) and true_mean == 4
    assert observed_mean - true_mean == cov / mean(records) == Fraction(-24, 17)
    lower_population = observed_durations + [0] * 15
    upper_population = observed_durations + [20] * 15
    lower, upper = mean(lower_population), mean(upper_population)
    assert lower == Fraction(11, 5) and upper == Fraction(26, 5)
    refined_lower = mean(observed_durations + [12] * 5 + [0] * 10)
    refined_upper = mean(observed_durations + [12] * 5 + [20] * 10)
    assert refined_lower == Fraction(14, 5) and refined_upper == Fraction(24, 5)
    record("missing-outcomes", {"n_observed": len(observed_durations), "N": len(full_durations),
        "observed_mean": str(observed_mean), "full_mean": str(true_mean), "covariance": str(cov),
        "mean_bias": str(observed_mean - true_mean), "original_bounds": [str(lower), str(upper)],
        "bounds_after_five_12day_records": [str(refined_lower), str(refined_upper)]})

    # X、U 的全部等概率组合确保独立；直接计算总体协方差而非随机抽样回归。
    independent_pairs = [(Fraction(x), Fraction(u)) for x in (-2, 2) for u in (-1, 1)]
    xs = [x for x, u in independent_pairs]
    us = [u for x, u in independent_pairs]
    ws = [x + u for x, u in independent_pairs]
    ys = [3 + 2 * x for x, u in independent_pairs]
    assert covariance(xs, us) == 0 and mean(us) == 0
    slope = covariance(ws, ys) / covariance(ws, ws)
    reliability = covariance(xs, xs) / (covariance(xs, xs) + covariance(us, us))
    assert reliability == Fraction(4, 5) and slope == Fraction(8, 5)
    assert slope == 2 * reliability
    record("classical-measurement-error", {"equal_probability_pairs": [[str(x), str(u)] for x, u in independent_pairs],
        "true_slope": "2", "observed_population_slope": str(slope), "attenuation_factor": str(reliability)})

    ratio_details = []
    for n, d, dn, dd in [(900, 1000, 0, -100), (9, 10, 1, -1), (9, 10, -1, 1), (9, 10, 0, 0)]:
        n, d, dn, dd = map(Fraction, (n, d, dn, dd))
        assert d > 0 and abs(dd) < d
        actual_difference = (n + dn) / (d + dd) - n / d
        algebraic_difference = (d * dn - n * dd) / (d * (d + dd))
        bound = (d * abs(dn) + abs(n) * abs(dd)) / (d * (d - abs(dd)))
        assert actual_difference == algebraic_difference and abs(actual_difference) <= bound
        ratio_details.append({"true": str(n / d), "reported": str((n + dn) / (d + dd)),
                              "difference": str(actual_difference), "bound": str(bound)})
    assert ratio_details[0] == {"true": "9/10", "reported": "1", "difference": "1/10", "bound": "1/10"}
    record("ratio-error", {"examples": ratio_details})

    choices = []
    for probability in [Fraction(1, 100), Fraction(1, 50), Fraction(3, 100)]:
        losses = {"release": probability * 100, "hold": Fraction(2)}
        minimum = min(losses.values())
        optimal = [name for name, value in losses.items() if value == minimum]
        choices.append({"probability": str(probability),
                        "expected_losses": {k: str(v) for k, v in losses.items()}, "optimal": optimal})
    assert choices[0]["optimal"] == ["release"]
    assert choices[1]["optimal"] == ["release", "hold"]
    assert choices[2]["optimal"] == ["hold"]
    assert Fraction(2, 100) == Fraction(1, 50)
    assert Fraction(4, 100) * 80 == Fraction(16, 5) > 2
    record("publication-loss-threshold", {"threshold": "1/50", "choices": choices,
        "exercise_release_loss": "16/5", "exercise_hold_loss": "2", "exercise_optimal": "hold"})

    # 区间端点分别可取；严格优于要求较低估计界仍高于另一对象的较高估计界。
    a, b = Fraction(90, 100), Fraction(88, 100)
    ea, eb = Fraction(2, 100), Fraction(1, 100)
    assert a - ea == Fraction(88, 100) and b + eb == Fraction(89, 100)
    assert a - Fraction(1, 100) == b + eb  # 等号只能保证不小于。
    assert a - Fraction(9, 1000) > b + eb
    assert a - ea == b  # B 的误差缩为零，仍只能得到等号。
    record("strict-ranking-under-error-bounds", {"initial_intervals": [["22/25", "23/25"], ["87/100", "89/100"]],
        "shrink_A_requirement": "epsilon_A < 1/100", "shrink_B_alone": "strict ranking impossible"})

    # 新增阅读版例子：分层记录率不同，按完整总体组权重还原。
    full_mar = [("A", Fraction(2), True)] * 50 + [("B", Fraction(6), True)] * 25 + [("B", Fraction(6), False)] * 25
    observed_mar = [y for group, y, observed in full_mar if observed]
    group_means = {group: mean([y for g, y, observed in full_mar if observed and g == group]) for group in ("A", "B")}
    standardized = sum(Fraction(sum(g == group for g, y, observed in full_mar), len(full_mar)) * group_means[group] for group in group_means)
    assert mean(observed_mar) == Fraction(10, 3) and standardized == mean([y for g, y, observed in full_mar]) == 4
    record("mar-population-weights", {"recorded_mean": str(mean(observed_mar)), "standardized_mean": str(standardized), "full_mean": "4"})

    alarm_table = [(True, True)] * 90 + [(True, False)] * 10 + [(False, True)] * 495 + [(False, False)] * 9405
    alerts = [fault for fault, alarm in alarm_table if alarm]
    posterior = Fraction(sum(alerts), len(alerts))
    assert len(alarm_table) == 10000 and len(alerts) == 585 and posterior == Fraction(2, 13)
    record("alert-base-rate", {"batch_count": len(alarm_table), "alerts": len(alerts), "true_alerts": sum(alerts), "error_given_alert": str(posterior)})

    production = [(Fraction(1), True)] * 90 + [(Fraction(1), False)] * 10 + [(Fraction(2), True)] * 50 + [(Fraction(2), False)] * 50
    piece_quality = Fraction(sum(good for ideal_time, good in production), len(production))
    time_quality = sum(time for time, good in production if good) / sum(time for time, good in production)
    assert piece_quality == Fraction(7, 10) and time_quality == Fraction(19, 30)
    record("heterogeneous-oee-quality-weight", {"piece_quality": str(piece_quality), "ideal_time_quality": str(time_quality)})

    return {"passed": True, "checks": checks, "details": details}


if __name__ == "__main__":
    print(json.dumps(run_checks(), ensure_ascii=False, indent=2))
