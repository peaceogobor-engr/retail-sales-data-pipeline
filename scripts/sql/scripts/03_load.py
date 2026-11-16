"""
Load: stage raw CSV in DuckDB, run the SQL transform, validate, export marts.

Usage:
    python scripts/01_extract.py     # once
    python scripts/03_load.py        # build warehouse + export dashboard mart
"""

from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "raw" / "superstore.csv"
DB_FILE = ROOT / "warehouse" / "superstore.duckdb"
SQL_FILE = ROOT / "sql" / "02_transform.sql"
MART_FILE = ROOT / "data" / "processed" / "sales_mart.csv"


def load() -> None:
    (ROOT / "warehouse").mkdir(parents=True, exist_ok=True)
    MART_FILE.parent.mkdir(parents=True, exist_ok=True)

    # --- Stage: pandas handles encoding + mixed date formats ---
    df = pd.read_csv(RAW_FILE, encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], dayfirst=True, errors="coerce")
    df = df.rename(columns={"Order Date": "order_date", "Ship Date": "ship_date"})
    print(f"Staged {len(df):,} raw rows")

    con = duckdb.connect(str(DB_FILE))
    con.register("stg_superstore", df)

    # --- Transform: all business logic lives in versioned SQL ---
    statements = [
        s.strip() for s in SQL_FILE.read_text().split(";") if s.strip()
    ]
    for stmt in statements:
        result = con.execute(stmt)
        if stmt.lstrip().upper().startswith("SELECT"):
            print(result.fetchdf().to_string(index=False), "\n")

    # --- Export the executive mart consumed by the dashboard repo ---
    mart = con.execute("""
        SELECT
            d.year_month,
            g.region,
            p.category,
            c.segment,
            ROUND(SUM(f.sales), 2)   AS sales,
            ROUND(SUM(f.profit), 2)  AS profit,
            SUM(f.quantity)          AS units,
            COUNT(DISTINCT f.order_id) AS orders
        FROM fact_sales f
        JOIN dim_date d      USING (order_date)
        JOIN dim_product p   USING (product_id)
        JOIN dim_customer c  USING (customer_id)
        JOIN dim_geography g ON f.state = g.state
        GROUP BY 1, 2, 3, 4
        ORDER BY 1, 2
    """).fetchdf()
    mart.to_csv(MART_FILE, index=False)
    print(f"Exported {len(mart):,} mart rows -> {MART_FILE}")
    print(f"Warehouse ready: {DB_FILE}")

    con.close()


if __name__ == "__main__":
    load()
