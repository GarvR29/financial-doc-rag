"""
Day 1: pull the raw materials for all four companies.

For each company this:
  1. Looks up its filing history and finds the latest 10-K
  2. Downloads that 10-K's raw HTML (prose track — chunked in Day 2)
  3. Downloads its XBRL company facts (structured track — calculation
     tool in Day 3)

Nothing is parsed or cleaned yet — that's deliberate. Day 1 is "get
everything onto disk in a raw, inspectable form" so later days can be
developed and re-run against local files instead of hitting the API
every time.
"""

import json
import os

from config import COMPANIES
from src.edgar_client import (
    get_submissions,
    get_company_facts,
    find_latest_10k,
    build_filing_url,
    download_filing,
)

RAW_DIR = "data/raw"


def main():
    os.makedirs(RAW_DIR, exist_ok=True)

    for ticker, info in COMPANIES.items():
        cik = info["cik"]
        print(f"\n--- {ticker} ({info['name']}) ---")

        submissions = get_submissions(cik)
        latest_10k = find_latest_10k(submissions)
        if not latest_10k:
            print(f"  No 10-K found for {ticker} — skipping")
            continue
        print(f"  Latest 10-K: filed {latest_10k['filingDate']}, "
              f"fiscal year end {latest_10k['reportDate']}")

        filing_url = build_filing_url(
            cik, latest_10k["accessionNumber"], latest_10k["primaryDocument"]
        )
        html = download_filing(filing_url)
        raw_path = os.path.join(RAW_DIR, f"{ticker}_10K_{latest_10k['reportDate']}.html")
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  Saved filing HTML -> {raw_path}")

        facts = get_company_facts(cik)
        facts_path = os.path.join(RAW_DIR, f"{ticker}_facts.json")
        with open(facts_path, "w", encoding="utf-8") as f:
            json.dump(facts, f)
        print(f"  Saved XBRL company facts -> {facts_path}")


if __name__ == "__main__":
    main()
