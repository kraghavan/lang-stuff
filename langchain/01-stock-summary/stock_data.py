"""
Stock Data Fetcher — SEC EDGAR API Client

Fetches real company financial data from SEC EDGAR (free, no API key needed).
This module handles all data retrieval so the LangChain code can focus on analysis.

SEC EDGAR: https://www.sec.gov/search-filings/edgar-application-programming-interfaces

Usage:
    from stock_data import get_stock_data
    data = get_stock_data("AAPL")
"""

import os
import requests
from typing import Optional


# SEC requires a User-Agent header identifying who you are
SEC_USER_AGENT = os.getenv("SEC_API_USER_AGENT", "LangChainLearner student@example.com")
SEC_HEADERS = {"User-Agent": SEC_USER_AGENT}

# SEC EDGAR API endpoints
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

# Financial metrics we want to extract
# Each tuple is (display_name, list_of_xbrl_concept_names_to_try)
METRICS_TO_EXTRACT = [
    ("revenue", ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"]),
    ("net_income", ["NetIncomeLoss"]),
    ("total_assets", ["Assets"]),
    ("total_liabilities", ["Liabilities"]),
    ("operating_income", ["OperatingIncomeLoss"]),
]


def get_company_cik(ticker: str) -> Optional[str]:
    """
    Convert a stock ticker symbol to SEC CIK number.

    The SEC identifies companies by CIK (Central Index Key), not ticker.
    This function looks up the CIK from SEC's ticker mapping file.

    Args:
        ticker: Stock symbol (e.g., "AAPL", "MSFT", "TSLA")

    Returns:
        CIK as a zero-padded 10-digit string, or None if not found

    Example:
        >>> get_company_cik("AAPL")
        "0000320193"
    """
    try:
        response = requests.get(TICKERS_URL, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        tickers_data = response.json()

        # Search for matching ticker (case-insensitive)
        ticker_upper = ticker.upper()
        for entry in tickers_data.values():
            if entry.get("ticker", "").upper() == ticker_upper:
                cik = str(entry["cik_str"]).zfill(10)
                return cik

        print(f"✗ Could not find CIK for ticker: {ticker}")
        return None

    except requests.RequestException as e:
        print(f"❌ Error looking up CIK: {e}")
        return None


def get_financial_facts(cik: str) -> Optional[dict]:
    """
    Fetch company financial facts from SEC EDGAR XBRL API.

    This returns ALL financial data the company has ever reported
    in structured XBRL format.

    Args:
        cik: Zero-padded CIK number (e.g., "0000320193")

    Returns:
        Dictionary containing all financial facts, or None on error

    Example:
        >>> facts = get_financial_facts("0000320193")
        >>> list(facts["facts"]["us-gaap"].keys())[:3]
        ['AccountsPayableCurrent', 'AccountsReceivableNetCurrent', ...]
    """
    try:
        url = COMPANY_FACTS_URL.format(cik=cik)
        response = requests.get(url, headers=SEC_HEADERS, timeout=15)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        print(f"❌ Error fetching financial facts: {e}")
        return None


def extract_metric(facts: dict, concept_names: list[str]) -> Optional[dict]:
    """
    Extract the most recent value for a financial metric from SEC data.

    SEC financial data is organized by XBRL concept names under:
    facts -> "facts" -> "us-gaap" -> concept_name -> "units" -> "USD" -> [entries]

    Each entry looks like:
    {"val": 391035000000, "end": "2024-09-28", "form": "10-K", "fy": 2024, ...}

    We want the most recent 10-K or 10-Q entry.

    Args:
        facts: Raw SEC facts dictionary from get_financial_facts()
        concept_names: List of XBRL concept names to try (first match wins)

    Returns:
        {"value": 391035000000, "end_date": "2024-09-28", "form": "10-K"} or None
    """
    us_gaap = facts.get("facts", {}).get("us-gaap", {})

    for concept_name in concept_names:
        try:
            entries = us_gaap[concept_name]["units"]["USD"]

            # Filter for 10-K or 10-Q filings only
            filed_entries = [
                e for e in entries
                if e.get("form") in ("10-K", "10-Q")
            ]

            if not filed_entries:
                continue

            # Sort by end date (most recent first)
            filed_entries.sort(key=lambda e: e.get("end", ""), reverse=True)

            # Return the most recent entry
            latest = filed_entries[0]
            return {
                "value": latest["val"],
                "end_date": latest["end"],
                "form": latest["form"]
            }

        except (KeyError, IndexError):
            continue

    return None


def format_large_number(value: float) -> str:
    """
    Format large numbers for readability.

    Args:
        value: Number to format

    Returns:
        Formatted string (e.g., "$391.0B", "$14.9M", "$1.2T")
    """
    abs_value = abs(value)
    sign = "-" if value < 0 else ""

    if abs_value >= 1_000_000_000_000:
        return f"{sign}${abs_value / 1_000_000_000_000:.1f}T"
    elif abs_value >= 1_000_000_000:
        return f"{sign}${abs_value / 1_000_000_000:.1f}B"
    elif abs_value >= 1_000_000:
        return f"{sign}${abs_value / 1_000_000:.1f}M"
    elif abs_value >= 1_000:
        return f"{sign}${abs_value / 1_000:.1f}K"
    else:
        return f"{sign}${abs_value:.2f}"


def get_stock_data(ticker: str) -> Optional[dict]:
    """
    Get a structured financial summary for a company.

    This is the main entry point — combines CIK lookup, fact fetching,
    and metric extraction into one convenient function.

    Args:
        ticker: Stock symbol (e.g., "AAPL")

    Returns:
        {
            "ticker": "AAPL",
            "company_name": "APPLE INC",
            "cik": "0000320193",
            "metrics": {
                "revenue": {"value": 391035000000, "end_date": "2024-09-28", "formatted": "$391.0B"},
                "net_income": {"value": 101218000000, ...},
                ...
            }
        }
        or None on error
    """
    # Step 1: Get CIK from ticker
    cik = get_company_cik(ticker)
    if not cik:
        return None

    # Step 2: Get financial facts
    facts = get_financial_facts(cik)
    if not facts:
        return None

    # Step 3: Extract each metric
    metrics = {}
    for display_name, concept_names in METRICS_TO_EXTRACT:
        metric = extract_metric(facts, concept_names)
        if metric:
            metric["formatted"] = format_large_number(metric["value"])
        metrics[display_name] = metric

    # Step 4: Build result
    company_name = facts.get("entityName", ticker.upper())

    return {
        "ticker": ticker.upper(),
        "company_name": company_name,
        "cik": cik,
        "metrics": metrics
    }


# ═══════════════════════════════════════════════
# Test the module directly
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    print("📊 Testing Stock Data Fetcher")
    print("=" * 40)

    test_ticker = "AAPL"
    print(f"\nFetching data for {test_ticker}...")

    data = get_stock_data(test_ticker)

    if data:
        print(f"\n✓ Company: {data['company_name']} (CIK: {data['cik']})")
        print(f"\n📊 Financial Metrics:")
        for name, metric in data.get("metrics", {}).items():
            if metric:
                formatted = metric.get("formatted", f"${metric['value']:,.0f}")
                print(f"  {name:20s}: {formatted} (as of {metric['end_date']})")
            else:
                print(f"  {name:20s}: Not available")
    else:
        print("✗ Failed to fetch data. Check your internet connection and try again.")
