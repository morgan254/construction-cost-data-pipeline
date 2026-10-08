# Construction Cost Data Platform

A beginner-friendly, fully fictional construction cost warehouse. It ingests CSV files into DuckDB, transforms them with dbt, checks data quality and reconciliations, and exports Power BI-ready tables.

## What you will build

```text
data/source/*.csv + BOQ workbook -> Python ingestion -> DuckDB raw schema -> dbt staging and marts -> CSV exports -> Power BI
```

The sample project is **PRJ-001 (Riverside Community Clinic)**. All people, companies, and amounts are fictional. Amounts are in KES.

## Requirements

- Python 3.10 or newer
- Power BI Desktop for the optional dashboard (Windows)

The pipeline uses DuckDB and dbt-duckdb. No server or cloud account is needed. The BOQ is supplied as an Excel workbook; the other source files are CSVs.

## Quick start (PowerShell)

From this project folder:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts\run_pipeline.py
```

If `py` is unavailable, install Python and use `python -m venv .venv`. The first pipeline run creates `warehouse\construction_cost.duckdb` and exports dashboard tables to `exports\`. It validates the source data and stops with a clear error if required fields, identifiers, references, or reconciliations fail.

## Project map

- `data/source/`: fictional projects, work packages, BOQ (Excel), purchases, valuations, payments, and variations (CSV).
- `src/ingest.py`: creates raw tables and loads the CSV sources into DuckDB.
- `models/staging/`: standardized, typed dbt views over raw tables.
- `models/marts/`: reporting tables for project/work package costs, supplier spend, variation impact, and valuation/payment reconciliation.
- `scripts/run_pipeline.py`: validates inputs, ingests, runs dbt, validates outputs, and exports CSVs.
- `exports/`: generated, Power BI-ready CSV files.

## Learn in stages

1. Open the CSV files and README data dictionary. Identify keys, dates, units, and measures.
2. Run the pipeline and inspect the raw tables in DuckDB.
3. Read one staging model and compare it with its source CSV.
4. Follow the mart model joins and calculations; compare totals with the source records.
5. Connect Power BI to the exported tables and build the views below.
6. After the local process is clear and repeatable, extend it with scheduling/orchestration (Airflow is a later milestone).

## Power BI dashboard

In Power BI Desktop, use **Get data → Text/CSV** and select the files under `exports/`. Load all exports and relate them using `project_id`, `work_package_id`, or `supplier_id` where relevant. Suggested pages:

1. **Project overview:** budget, actual cost, committed cost, certified, paid, remaining budget, and cost variance cards; actual vs budget by month if you later add a date dimension.
2. **Work packages:** budget vs actual vs committed by package, with a variance chart.
3. **Suppliers:** committed and actual purchase amounts by supplier.
4. **Variations:** approved variation value and variation percentage by work package.
5. **Valuations & payments:** certified amount versus paid amount, outstanding certified amount, and payment lag.

Use `exports/mart_project_cost_summary.csv` for headline cards and `exports/mart_work_package_costs.csv` for package comparisons. The other exports support supplier, variation, and payment views. Re-run `python scripts\run_pipeline.py` after changing the source data, then refresh Power BI.

## Useful commands

```powershell
dbt debug --project-dir . --profiles-dir .
dbt run --project-dir . --profiles-dir .
dbt test --project-dir . --profiles-dir .
```

## Extending the project

Good next steps: add incremental loads, a date dimension, invoice-level actual costs, schema-versioned source files, unit tests for business calculations, and finally a scheduler. Keep the first pipeline understandable before adding services.
