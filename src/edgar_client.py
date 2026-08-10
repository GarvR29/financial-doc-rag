"""
Thin client around the two SEC EDGAR data APIs this project uses:

1. Submissions API  (data.sec.gov/submissions/CIK##########.json)
   -> A company's filing HISTORY: every form it has ever filed, with
      dates and the info needed to construct a download URL. We use
      this to find "the most recent 10-K."

2. Company Facts API  (data.sec.gov/api/xbrl/companyfacts/CIK##########.json)
   -> Every XBRL-tagged NUMBER the company has ever reported (revenue,
      net income, total assets, ...), pre-structured as JSON. This is
      what feeds the Day 3 calculation tool later — no table-parsing
      needed for these figures.

Both are free, need no API key, but require a descriptive User-Agent
header and respect a 10 requests/second rate limit — hence the
rate-limiting wrapper below.
"""

import time
import requests

from config import USER_AGENT

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{accession_no_dashes}/{document}"

_last_request_time = 0.0
_MIN_INTERVAL = 0.11  # ~9 req/sec, safely under SEC's 10 req/sec cap


def _rate_limited_get(url: str) -> requests.Response:
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)

    response = requests.get(url, headers={"User-Agent": USER_AGENT})
    _last_request_time = time.time()
    response.raise_for_status()
    return response


def get_submissions(cik: str) -> dict:
    """Fetch a company's full filing history."""
    url = SUBMISSIONS_URL.format(cik=cik.zfill(10))
    return _rate_limited_get(url).json()


def get_company_facts(cik: str) -> dict:
    """Fetch every XBRL-tagged financial fact the company has reported."""
    url = FACTS_URL.format(cik=cik.zfill(10))
    return _rate_limited_get(url).json()


def find_latest_10k(submissions: dict) -> dict | None:
    """
    Scan a submissions payload for the most recent 10-K.

    The API returns parallel arrays under filings.recent (form[i],
    accessionNumber[i], filingDate[i], ... all line up by index) rather
    than a list of objects — an EDGAR quirk worth knowing before you
    try to iterate it any other way.
    """
    recent = submissions["filings"]["recent"]
    for i, form in enumerate(recent["form"]):
        if form == "10-K":
            return {
                "accessionNumber": recent["accessionNumber"][i],
                "filingDate": recent["filingDate"][i],
                "reportDate": recent["reportDate"][i],
                "primaryDocument": recent["primaryDocument"][i],
            }
    return None


def build_filing_url(cik: str, accession_number: str, primary_document: str) -> str:
    """
    Construct the direct URL to a filing's primary document.

    EDGAR's archive path needs the CIK WITHOUT leading zeros, and the
    accession number WITHOUT its dashes, e.g. "0000320193-24-000123"
    becomes "000032019324000123" in the URL path.
    """
    cik_no_zeros = str(int(cik))
    accession_no_dashes = accession_number.replace("-", "")
    return ARCHIVES_URL.format(
        cik_no_zeros=cik_no_zeros,
        accession_no_dashes=accession_no_dashes,
        document=primary_document,
    )


def download_filing(url: str) -> str:
    """Download the raw HTML of a filing document."""
    return _rate_limited_get(url).text
