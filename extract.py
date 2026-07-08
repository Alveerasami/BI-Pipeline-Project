"""
extract.py
----------
EXTRACT stage of the ETL pipeline.

Pulls street-level crime data from the UK Police public API (data.police.uk) -
a free, no-auth-required public sector open data API, chosen so this project
demonstrates real API extraction rather than a toy example.

If no network connection is available (e.g. running this in an offline
environment), the script automatically falls back to a bundled sample
response with an identical schema, so the rest of the pipeline can still
be run and demonstrated end-to-end.

Usage:
    python extract.py --lat 52.629729 --lng -1.131592 --date 2026-05
"""

import argparse
import json
import os
import sys
from datetime import datetime

import requests

API_URL = "https://data.police.uk/api/crimes-street/all-crime"
SAMPLE_FALLBACK = os.path.join(os.path.dirname(__file__), "data", "sample_api_response.json")
RAW_OUTPUT = os.path.join(os.path.dirname(__file__), "data", "raw_extract.json")


def fetch_from_api(lat: float, lng: float, date: str) -> list:
    """Call the public API and return the JSON payload."""
    params = {"lat": lat, "lng": lng, "date": date}
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_from_sample() -> list:
    """Offline fallback so the pipeline is fully runnable without network access."""
    with open(SAMPLE_FALLBACK, "r") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Extract crime data from the UK Police API")
    parser.add_argument("--lat", type=float, default=52.629729)
    parser.add_argument("--lng", type=float, default=-1.131592)
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y-%m"))
    parser.add_argument("--offline", action="store_true", help="Force use of bundled sample data")
    args = parser.parse_args()

    if args.offline:
        print("Running in offline mode - using bundled sample data.")
        records = fetch_from_sample()
    else:
        try:
            print(f"Calling API for lat={args.lat}, lng={args.lng}, date={args.date} ...")
            records = fetch_from_api(args.lat, args.lng, args.date)
            print(f"Retrieved {len(records)} records from live API.")
        except requests.exceptions.RequestException as e:
            print(f"API call failed ({e}). Falling back to bundled sample data for demo purposes.")
            records = fetch_from_sample()

    with open(RAW_OUTPUT, "w") as f:
        json.dump(records, f, indent=2)

    print(f"Extracted {len(records)} raw records -> {RAW_OUTPUT}")
    return records


if __name__ == "__main__":
    main()
