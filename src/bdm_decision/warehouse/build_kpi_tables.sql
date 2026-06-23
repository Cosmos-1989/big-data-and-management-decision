-- Week 03: build KPI tables for the course sample data.
-- Target engine: DuckDB. Paths are relative to the project root.

CREATE OR REPLACE VIEW customers AS
SELECT *
FROM read_csv_auto('data/sample/customers.csv', header = true);

CREATE OR REPLACE VIEW products AS
SELECT *
FROM read_csv_auto('data/sample/products.csv', header = true);

CREATE OR REPLACE VIEW orders AS
SELECT *
FROM read_csv_auto('data/sample/orders.csv', header = true);

CREATE OR REPLACE VIEW inventory AS
SELECT *
FROM read_csv_auto('data/sample/inventory.csv', header = true);

CREATE OR REPLACE VIEW order_enriched AS
SELECT
  o.order_id,
  o.customer_id,
  c.customer_name,
  c.region,
  c.segment,
  o.product_id,
  p.product_name,
  p.category,
  o.order_date,
  strftime(o.order_date, '%Y-%m') AS month,
  o.quantity,
  o.promised_date,
  o.actual_date,
  o.channel,
  o.priority,
  o.quantity * p.unit_price AS revenue,
  o.quantity * (p.unit_price - p.unit_cost) AS gross_profit,
  CASE
    WHEN o.actual_date <= o.promised_date THEN 1
    ELSE 0
  END AS on_time_flag,
  greatest(date_diff('day', o.promised_date, o.actual_date), 0) AS delay_days
FROM orders AS o
JOIN customers AS c
  ON o.customer_id = c.customer_id
JOIN products AS p
  ON o.product_id = p.product_id
WHERE o.actual_date IS NOT NULL;

CREATE OR REPLACE VIEW kpi_by_region AS
SELECT
  region,
  count(*) AS delivered_orders,
  sum(revenue) AS revenue,
  sum(gross_profit) AS gross_profit,
  sum(gross_profit) / nullif(sum(revenue), 0) AS gross_margin,
  sum(on_time_flag) * 1.0 / nullif(count(*), 0) AS on_time_delivery_rate,
  avg(delay_days) AS average_delay_days
FROM order_enriched
GROUP BY region
ORDER BY revenue DESC;

CREATE OR REPLACE VIEW kpi_by_month AS
SELECT
  month,
  count(*) AS delivered_orders,
  sum(revenue) AS revenue,
  sum(gross_profit) AS gross_profit,
  sum(gross_profit) / nullif(sum(revenue), 0) AS gross_margin,
  sum(on_time_flag) * 1.0 / nullif(count(*), 0) AS on_time_delivery_rate,
  avg(delay_days) AS average_delay_days
FROM order_enriched
GROUP BY month
ORDER BY month;

CREATE OR REPLACE VIEW customer_order_window AS
SELECT
  customer_id,
  order_id,
  order_date,
  revenue,
  sum(revenue) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS customer_recent_revenue,
  row_number() OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
  ) AS customer_order_sequence
FROM order_enriched
ORDER BY customer_id, order_date, order_id;

