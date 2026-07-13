# Performance & BI Mini-Pipeline: Public Sector Incident Reporting

A small, self-contained ETL and BI reporting project built to demonstrate
 my core skills for a Performance & BI Analyst role: pulling data from a
public API and SQL warehouse, cleaning it, running data quality/gap
analysis, and producing management-ready reports.

**Data source:** [data.police.uk](https://data.police.uk/) - the UK Police
public open data API (free, no auth key required), used here as a
stand-in for a real service's case/incident management system.

## What this demonstrates

| Job requirement | Where it's shown |
|---|---|
| ETL pipelines pulling data via SQL and APIs to a centralised warehouse | `extract.py`, `transform.py`, `load.py`, `sql/01_schema.sql` |
| Reports meeting statutory/regulatory and performance monitoring needs | `report.py`, `sql/04_reports.sql` |
| Gap analysis and data quality issues | `transform.py` (`run_data_quality_checks`), `Reporting.DataQualityLog` in `sql/03_stored_procedure.sql` |
| Reports catalogue and data relationships | `reports_catalogue.md` |
| Data presentation types: table, crosstab, chart | `report.py` and `sql/04_reports.sql` |
| Query structures: simple, combined, merged | `report.py` and `sql/04_reports.sql` |
| Data Warehouse principles | Staging vs Reporting schema separation in `sql/01_schema.sql` |
| SQL: T-SQL, stored procedures, CTEs | `sql/02_transform_cte.sql`, `sql/03_stored_procedure.sql` |
| Python | Full ETL pipeline (`extract.py`, `transform.py`, `load.py`, `report.py`) |

## Architecture

```
UK Police API  ──extract.py──>  data/raw_extract.json
                                       │
                                transform.py (clean + data quality checks)
                                       │
                                  load.py
                                       │
                                       v
                          output/warehouse.db (SQLite demo)
                                       │
                                 report.py
                                       │
                                       v
                    Table / Combined summary / Crosstab / Chart data


Production target (SQL Server):
  Staging.CrimeReports  --[usp_LoadCrimeReports: CTE clean + MERGE]-->  Reporting.CrimeReports
                                                                                │
                                                                     04_reports.sql outputs
```

> **Why SQLite for the demo?** So the whole pipeline runs end-to-end with
> zero setup (no server, no credentials) for anyone reviewing this project.
> The `/sql` folder contains the equivalent **T-SQL** for a real SQL Server
> deployment - schema, CTE transform logic, a MERGE-based stored procedure,
> and PIVOT-based crosstab reporting - which is the production pattern this
> demo is modelling.

## Project structure

```
bi-pipeline-project/
├── extract.py                  # EXTRACT: pulls from the public API (with offline fallback)
├── transform.py                 # TRANSFORM: cleans data, runs data quality/gap analysis
├── load.py                      # LOAD: writes to the warehouse
├── report.py                    # Reporting queries: table, combined, crosstab, chart
├── run_pipeline.py               # Orchestrates the full pipeline end-to-end
├── reports_catalogue.md          # Catalogue of available reports and data relationships
├── data/
│   ├── sample_api_response.json  # Offline fallback dataset (same schema as live API)
│   └── raw_extract.json          # Output of the extract step
├── output/
│   ├── warehouse.db              # SQLite demo warehouse
│   └── chart_ready_incidents_by_category.csv
└── sql/
    ├── 01_schema.sql             # T-SQL: Staging + Reporting schema (SQL Server)
    ├── 02_transform_cte.sql      # T-SQL: exploratory CTE transform logic
    ├── 03_stored_procedure.sql   # T-SQL: production stored procedure (CTE + MERGE)
    └── 04_reports.sql            # T-SQL: table/combined/crosstab/chart reporting queries
```

## Running it

```bash
pip install -r requirements.txt
python run_pipeline.py
```

This runs the full pipeline offline (using the bundled sample dataset) and
prints the data quality summary and all four report types to the console,
plus writes a chart-ready CSV to `output/`.

To pull live data instead of the offline sample:

```bash
python extract.py --lat 52.629729 --lng -1.131592 --date 2026-05
python -c "from transform import transform; from load import load_to_staging; df, q = transform('data/raw_extract.json'); load_to_staging(df)"
python report.py
```

## Notes on the T-SQL scripts

The `/sql` scripts are written for SQL Server and are not run as part of
`run_pipeline.py` (which uses SQLite for portability). They're included to
show the intended production implementation - deploy them to a SQL Server
instance, point `load.py` at that server instead of SQLite (e.g. via
`pyodbc`), and schedule `Reporting.usp_LoadCrimeReports` to run after each
extract via SQL Agent.
