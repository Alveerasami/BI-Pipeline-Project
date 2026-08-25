"""
transform.py
------------
TRANSFORM stage of the ETL pipeline.

Takes the raw extracted JSON and:
  1. Flattens nested API fields into a clean tabular structure
  2. Runs data quality checks (gap analysis) and logs issues found
  3. Returns a clean pandas DataFrame ready for loading
"""

import json
import pandas as pd


def flatten_records(records: list) -> pd.DataFrame:
    """Flatten the nested API JSON structure into a flat table."""
    rows = []
    for r in records:
        loc = r.get("location") or {}
        street = loc.get("street") or {}
        outcome = r.get("outcome_status") or {}
        rows.append({
            "record_id": r.get("id"),
            "persistent_id": r.get("persistent_id"),
            "category": r.get("category"),
            "street_name": street.get("name"),
            "latitude": loc.get("latitude"),
            "longitude": loc.get("longitude"),
            "outcome_category": outcome.get("category"),
            "outcome_date": outcome.get("date"),
            "reported_month": r.get("month"),
        })
    return pd.DataFrame(rows)


def run_data_quality_checks(df: pd.DataFrame) -> dict:
    """
    Gap analysis / data quality checks - 
    Returns a summary dict that gets logged and can feed a data quality
    report used to flag issues back to source system owners.
    """
    issues = {}

    issues["missing_location"] = int(df["latitude"].isna().sum())
    issues["missing_outcome"] = int(df["outcome_category"].isna().sum())
    issues["duplicate_persistent_ids"] = int(
        df[df["persistent_id"] != ""]["persistent_id"].duplicated().sum()
    )
    issues["missing_category"] = int(df["category"].isna().sum())
    issues["total_records_in"] = len(df)

    return issues


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Apply cleaning rules based on the quality checks above."""
    clean_df = df.copy()

    # De-duplicate on persistent_id where present (keep first occurrence)
    has_pid = clean_df["persistent_id"] != ""
    deduped = pd.concat([
        clean_df[has_pid].drop_duplicates(subset="persistent_id", keep="first"),
        clean_df[~has_pid],
    ])

    # Standardise category text (BI reports often need consistent casing/labels)
    deduped["category"] = deduped["category"].str.replace("-", " ").str.title()

    # Flag records missing geolocation rather than silently dropping them -
    # in a real service, unresolved location data would often still need
    # reporting on (e.g. for statutory returns) even if it can't be mapped.
    deduped["has_location"] = deduped["latitude"].notna()

    return deduped.reset_index(drop=True)


def transform(raw_path: str) -> tuple[pd.DataFrame, dict]:
    with open(raw_path, "r") as f:
        records = json.load(f)

    df = flatten_records(records)
    quality_report = run_data_quality_checks(df)
    clean_df = clean(df)

    return clean_df, quality_report


if __name__ == "__main__":
    df, quality = transform("data/raw_extract.json")
    print("Data quality summary:")
    print(json.dumps(quality, indent=2))
    print(f"\nCleaned {len(df)} rows (from {quality['total_records_in']} raw records)")
