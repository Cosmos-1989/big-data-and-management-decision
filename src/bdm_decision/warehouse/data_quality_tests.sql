-- Week 04: data quality tests for the sample order data.
-- Target engine: DuckDB. Each query returns failing records.

CREATE OR REPLACE VIEW customers AS
SELECT *
FROM read_csv_auto('data/sample/customers.csv', header = true);

CREATE OR REPLACE VIEW products AS
SELECT *
FROM read_csv_auto('data/sample/products.csv', header = true);

CREATE OR REPLACE VIEW orders_quality_issues AS
SELECT *
FROM read_csv_auto('data/sample/orders_quality_issues.csv', header = true);

-- Duplicate business key.
SELECT
  'unique_order_id' AS check_id,
  order_id,
  count(*) AS row_count
FROM orders_quality_issues
GROUP BY order_id
HAVING count(*) > 1;

-- Required fields.
SELECT
  'required_customer_id' AS check_id,
  order_id,
  customer_id
FROM orders_quality_issues
WHERE customer_id IS NULL OR customer_id = '';

-- Customer relationship.
SELECT
  'relationship_customer_id' AS check_id,
  o.order_id,
  o.customer_id
FROM orders_quality_issues AS o
LEFT JOIN customers AS c
  ON o.customer_id = c.customer_id
WHERE o.customer_id IS NOT NULL
  AND o.customer_id <> ''
  AND c.customer_id IS NULL;

-- Product relationship.
SELECT
  'relationship_product_id' AS check_id,
  o.order_id,
  o.product_id
FROM orders_quality_issues AS o
LEFT JOIN products AS p
  ON o.product_id = p.product_id
WHERE o.product_id IS NOT NULL
  AND o.product_id <> ''
  AND p.product_id IS NULL;

-- Accepted values.
SELECT
  'accepted_values_channel' AS check_id,
  order_id,
  channel
FROM orders_quality_issues
WHERE channel NOT IN ('Direct', 'Partner', 'Online');

SELECT
  'accepted_values_priority' AS check_id,
  order_id,
  priority
FROM orders_quality_issues
WHERE priority NOT IN ('High', 'Normal');

-- Positive quantity and date order.
SELECT
  'positive_quantity' AS check_id,
  order_id,
  quantity
FROM orders_quality_issues
WHERE quantity <= 0;

SELECT
  'promised_date_after_order_date' AS check_id,
  order_id,
  order_date,
  promised_date
FROM orders_quality_issues
WHERE promised_date < order_date;

