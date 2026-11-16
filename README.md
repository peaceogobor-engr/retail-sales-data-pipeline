# Retail Sales Data Pipeline

End-to-end ETL pipeline that ingests raw retail transaction data, models it
into a star schema (DuckDB), runs data-quality checks, and exports an
executive-ready analytics mart consumed by my
[executive-sales-dashboard](https://github.com/peaceogobor-engr/executive-sales-dashboard)
repo.

**What this demonstrates:** Python + SQL ETL design, dimensional modeling,
data validation, and production-style repo structure — the same patterns I
run daily in T-SQL / Azure Synapse environments.

## Architecture

raw CSV → staging (pandas) → transform (SQL, star schema) → data-quality
checks → analytics mart (CSV for BI layer)

## How to run

```bash
pip install -r requirements.txt
python scripts/01_extract.py   # download raw data (one time)
python scripts/03_load.py      # build warehouse + export mart
