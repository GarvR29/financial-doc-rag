# -----------------------------------------------------------------------
# Company universe for this project.
#
# CIK = "Central Index Key" — the permanent ID the SEC assigns to every
# filer. Unlike a ticker (which can change, e.g. FB -> META), a CIK never
# changes. Every EDGAR API call is keyed by CIK, not ticker, so this is
# the first thing you need per company.
# -----------------------------------------------------------------------
COMPANIES = {
    "AAPL": {"name": "Apple Inc.", "cik": "0000320193", "sector": "Technology"},
    "XOM": {"name": "Exxon Mobil Corporation", "cik": "0000034088", "sector": "Energy"},
    "KO": {"name": "The Coca-Cola Company", "cik": "0000021344", "sector": "Consumer Goods"},
    "JPM": {"name": "JPMorgan Chase & Co.", "cik": "0000019617", "sector": "Financials"},
}

# SEC requires every request to carry a descriptive User-Agent identifying
# who's making it (name/app + contact email). Requests without one, or with
# a generic one, get blocked. Put your own details here before running
# anything that hits data.sec.gov.
USER_AGENT = "GarvRawat-PortfolioProject rawatgarv29@gmail.com"
