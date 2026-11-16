-- Transform: staging -> star schema (fact + dimensions)
-- Executed by scripts/03_load.py against DuckDB.

-- ---------- Dimensions ----------

CREATE OR REPLACE TABLE dim_customer AS
SELECT DISTINCT
    "Customer ID"   AS customer_id,
    "Customer Name" AS customer_name,
    "Segment"       AS segment
FROM stg_superstore;

CREATE OR REPLACE TABLE dim_product AS
SELECT DISTINCT
    "Product ID"   AS product_id,
    "Product Name" AS product_name,
    "Category"     AS category,
    "Sub-Category" AS sub_category
FROM stg_superstore;

CREATE OR REPLACE TABLE dim_geography AS
SELECT DISTINCT
    "City"    AS city,
    "State"   AS state,
    "Region"  AS region,
    "Country" AS country
FROM stg_superstore;

CREATE OR REPLACE TABLE dim_date AS
SELECT DISTINCT
    order_date,
    EXTRACT(year  FROM order_date)  AS year,
    EXTRACT(month FROM order_date)  AS month,
    STRFTIME(order_date, '%Y-%m')   AS year_month,
    EXTRACT(quarter FROM order_date) AS quarter
FROM stg_superstore;

-- ---------- Fact ----------

CREATE OR REPLACE TABLE fact_sales AS
SELECT
    "Order ID"                       AS order_id,
    "Row ID"                         AS order_line_id,
    order_date,
    ship_date,
    ship_date - order_date           AS days_to_ship,
    "Ship Mode"                      AS ship_mode,
    "Customer ID"                    AS customer_id,
    "Product ID"                     AS product_id,
    "State"                          AS state,
    "Sales"                          AS sales,
    "Quantity"                       AS quantity,
    "Discount"                       AS discount,
    "Profit"                         AS profit,
    CASE WHEN "Sales" > 0
         THEN ROUND("Profit" / "Sales", 4) END AS profit_margin
FROM stg_superstore;

-- ---------- Data quality checks ----------

-- Grain check: one row per order line
SELECT
    COUNT(*)                    AS row_count,
    COUNT(DISTINCT order_line_id) AS distinct_lines
FROM fact_sales;

-- Referential integrity: every fact row resolves to a customer
SELECT COUNT(*) AS orphan_customers
FROM fact_sales f
LEFT JOIN dim_customer c USING (customer_id)
WHERE c.customer_id IS NULL;
