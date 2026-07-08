"""
report.py
---------
Demonstrates the "data presentation types" requirement from the job spec:
table, crosstab, and chart-ready outputs, all queried from the warehouse
using the different query structures (simple, combined, merged) referenced
in the spec.
"""

import sqlite3
import pandas as pd

DB_PATH = "output/warehouse.db"


def simple_query_table(conn) -> pd.DataFrame:
    """SIMPLE QUERY -> TABLE presentation: a straightforward record list."""
    query = """
        SELECT category, street_name, outcome_category, reported_month
        FROM staging_crime_reports
        ORDER BY category, street_name
    """
    return pd.read_sql(query, conn)


def combined_query_summary(conn) -> pd.DataFrame:
    """
    COMBINED QUERY -> summary table: aggregates two derived metrics
    (volume and outcome rate) combined into a single result set.
    """
    query = """
        WITH volume AS (
            SELECT category, COUNT(*) AS total_incidents
            FROM staging_crime_reports
            GROUP BY category
        ),
        outcomes AS (
            SELECT category, COUNT(*) AS incidents_with_outcome
            FROM staging_crime_reports
            WHERE outcome_category IS NOT NULL
            GROUP BY category
        )
        SELECT
            v.category,
            v.total_incidents,
            COALESCE(o.incidents_with_outcome, 0) AS incidents_with_outcome,
            ROUND(100.0 * COALESCE(o.incidents_with_outcome, 0) / v.total_incidents, 1) AS outcome_rate_pct
        FROM volume v
        LEFT JOIN outcomes o ON v.category = o.category
        ORDER BY v.total_incidents DESC
    """
    return pd.read_sql(query, conn)


def crosstab_report(conn) -> pd.DataFrame:
    """
    MERGED QUERY -> CROSSTAB presentation: category x location pivoted
    into a matrix, typical of a performance dashboard crosstab.
    """
    df = pd.read_sql(
        "SELECT category, street_name FROM staging_crime_reports", conn
    )
    crosstab = pd.crosstab(df["street_name"], df["category"])
    return crosstab


def chart_ready_data(conn) -> pd.DataFrame:
    """CHART-ready output: simple two-column aggregate suited to a bar chart."""
    query = """
        SELECT category, COUNT(*) AS incident_count
        FROM staging_crime_reports
        GROUP BY category
        ORDER BY incident_count DESC
    """
    return pd.read_sql(query, conn)


def run_reports():
    conn = sqlite3.connect(DB_PATH)

    print("\n--- TABLE: Simple query, raw record list ---")
    print(simple_query_table(conn).to_string(index=False))

    print("\n--- TABLE: Combined query, incident volume & outcome rate ---")
    print(combined_query_summary(conn).to_string(index=False))

    print("\n--- CROSSTAB: Category by location (merged query) ---")
    print(crosstab_report(conn))

    print("\n--- CHART-READY DATA: incidents by category ---")
    chart_df = chart_ready_data(conn)
    print(chart_df.to_string(index=False))
    chart_df.to_csv("output/chart_ready_incidents_by_category.csv", index=False)
    print("\n(Saved chart_ready_incidents_by_category.csv - ready to plot in Power BI/Excel)")

    conn.close()


if __name__ == "__main__":
    run_reports()
