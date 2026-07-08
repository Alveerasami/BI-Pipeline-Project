"""
run_pipeline.py
----------------
Orchestrates the full ETL pipeline: Extract -> Transform -> Load,
then runs the reporting queries and prints a data quality summary,
exactly mirroring the flow described in the job spec:

  "implement and maintain data pipelines allowing data to be pulled from
   systems using a combination of SQL and APIs to a centralised warehouse
   using Extract Transformation and Load (ETL) processes"
"""

import json
import extract
import transform as transform_module
import load
from report import run_reports


def main():
    print("=" * 60)
    print("STEP 1: EXTRACT")
    print("=" * 60)
    records = extract.fetch_from_sample()  # offline mode for reproducible demo runs
    with open(extract.RAW_OUTPUT, "w") as f:
        json.dump(records, f, indent=2)
    print(f"Extracted {len(records)} raw records -> {extract.RAW_OUTPUT}")

    print("\n" + "=" * 60)
    print("STEP 2: TRANSFORM")
    print("=" * 60)
    df, quality_report = transform_module.transform("data/raw_extract.json")
    print("Data quality summary (gap analysis):")
    print(json.dumps(quality_report, indent=2))

    print("\n" + "=" * 60)
    print("STEP 3: LOAD")
    print("=" * 60)
    load.load_to_staging(df)

    print("\n" + "=" * 60)
    print("STEP 4: REPORT")
    print("=" * 60)
    run_reports()

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
