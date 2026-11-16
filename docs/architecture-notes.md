# Architecture & Design Decisions

## Overview

This pipeline moves retail transaction data from a raw CSV extract to a
star-schema analytics warehouse, with validation gates between each stage.

## Design Decisions

### 1. Star schema (fact + dimensions) instead of a flat table
The BI layer (see my executive-sales-dashboard repo) stays thin: every
business question becomes a simple aggregation over `fact_sales` joined to
small, conformed dimensions. This mirrors how I model Power BI semantic
models in production — one source of truth, reusable across reports.

### 2. Business logic lives in versioned SQL, not embedded Python
`sql/02_transform.sql` contains all transformation logic. Benefits:
reviewable in pull requests, portable to Synapse/Fabric/SQL Server with
minimal changes, and testable independently of the orchestration code.
Python is used only for what it's best at: file handling and orchestration.

### 3. Validation is part of the load, not an afterthought
The load script runs grain checks (one row per order line) and referential
integrity checks (every sale resolves to a known customer) on every run.
If either fails, the mart is not exported — silent bad data never reaches
an executive dashboard.

### 4. Date parsing at the staging boundary
The raw extract mixes date formats, so parsing happens once, in pandas, at
ingest — the SQL layer only ever sees clean, typed dates.

### 5. Raw data is git-ignored
`data/raw/` and the DuckDB warehouse file are excluded from version control.
The pipeline regenerates them deterministically from the source, keeping the
repo lightweight and avoiding stale-data drift.

## If this were production

- Orchestration: Azure Data Factory / Synapse Pipelines on a schedule
- Warehouse: Azure Synapse dedicated pool or Microsoft Fabric
- Quality gates: Great Expectations suite wired into CI
- Incremental loads: watermark on order_date instead of full refresh
