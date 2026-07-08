"""
load.py
-------
LOAD stage of the ETL pipeline.

Loads the cleaned data into a local warehouse database.

NOTE ON DATABASE CHOICE:
This demo uses SQLite purely so the whole pipeline can be run end-to-end
on any machine with no setup (no server, no credentials). The production
target for this pattern is SQL Server, and the /sql folder contains the
equivalent T-SQL schema, CTE transform logic, and stored procedure that
would run there - see sql/01_schema.sql onwards.
"""

import sqlite3
import pandas as pd

DB_PATH = "output/warehouse.db"


def load_to_staging(df: pd.DataFrame, db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    df.to_sql("staging_crime_reports", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Loaded {len(df)} rows into staging_crime_reports ({db_path})")


if __name__ == "__main__":
    from transform import transform

    df, quality = transform("data/raw_extract.json")
    load_to_staging(df)
