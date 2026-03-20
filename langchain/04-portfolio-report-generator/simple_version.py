"""
Portfolio Report Generator — Structured Output + Batch Processing

Analyzes an entire stock portfolio using Claude with Pydantic models
for structured output and batch processing for efficiency.

Architecture:
    CSV → Fetch Data → Analyze (batch, structured) → Generate Report

Key Concepts:
    - Pydantic output models (typed LLM responses)
    - llm.with_structured_output(Model)
    - chain.batch() for concurrent processing
    - Report generation from structured data

Usage:
    python simple_version.py

Requires:
    - ANTHROPIC_API_KEY environment variable
    - data/sample_portfolio.csv
"""

import os
import sys
import csv
from typing import Optional
from dotenv import load_dotenv

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

# Local imports
from portfolio_models import HoldingAnalysis, PortfolioSummary

# Load environment variables
load_dotenv()

# ═══════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
PORTFOLIO_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_portfolio.csv")
MAX_CONCURRENCY = 3  # How many API calls to make at once


# ═══════════════════════════════════════════════
# Sample Financial Data (built-in)
#
# Simulated financial data for common tickers.
# In a real app, you'd fetch this from SEC EDGAR (see Example 01).
# ═══════════════════════════════════════════════

SAMPLE_FINANCIAL_DATA = {
    "AAPL": {
        "company_name": "Apple Inc.",
        "data": (
            "Revenue: $391.0B (+2% YoY)\n"
            "Net Income: $101.2B (+4% YoY)\n"
            "Gross Margin: 46.2% (up from 44.1%)\n"
            "Services Revenue: $96.0B (+13% YoY)\n"
            "Cash Position: $140.6B\n"
            "Sector: Technology — Consumer Electronics"
        )
    },
    "MSFT": {
        "company_name": "Microsoft Corporation",
        "data": (
            "Revenue: $245.1B (+16% YoY)\n"
            "Net Income: $88.1B (+22% YoY)\n"
            "Azure Revenue Growth: +29% YoY\n"
            "Operating Margin: 44.6%\n"
            "Cash Position: $80.5B\n"
            "Sector: Technology — Software & Cloud"
        )
    },
    "TSLA": {
        "company_name": "Tesla Inc.",
        "data": (
            "Revenue: $96.8B (+19% YoY)\n"
            "Net Income: $7.1B (-23% YoY)\n"
            "Gross Margin: 17.6% (down from 25.6%)\n"
            "Deliveries: 1.81M vehicles (+12% YoY)\n"
            "Energy Storage: +75% YoY growth\n"
            "Sector: Automotive — Electric Vehicles"
        )
    },
    "NVDA": {
        "company_name": "NVIDIA Corporation",
        "data": (
            "Revenue: $130.5B (+114% YoY)\n"
            "Net Income: $72.9B (+145% YoY)\n"
            "Data Center Revenue: $115.2B (+154% YoY)\n"
            "Gross Margin: 73.0%\n"
            "Cash Position: $43.2B\n"
            "Sector: Technology — Semiconductors"
        )
    },
    "JPM": {
        "company_name": "JPMorgan Chase & Co.",
        "data": (
            "Revenue: $177.6B (+12% YoY)\n"
            "Net Income: $58.5B (+25% YoY)\n"
            "Net Interest Income: $91.4B\n"
            "Return on Equity: 17%\n"
            "Total Assets: $4.0T\n"
            "Sector: Financials — Banking"
        )
    },
    "AMZN": {
        "company_name": "Amazon.com Inc.",
        "data": (
            "Revenue: $638.0B (+12% YoY)\n"
            "Net Income: $59.2B (+95% YoY)\n"
            "AWS Revenue: $107.6B (+19% YoY)\n"
            "Operating Margin: 11.3% (up from 6.4%)\n"
            "Cash Position: $78.7B\n"
            "Sector: Technology — E-Commerce & Cloud"
        )
    },
    "GOOGL": {
        "company_name": "Alphabet Inc.",
        "data": (
            "Revenue: $350.0B (+14% YoY)\n"
            "Net Income: $100.7B (+36% YoY)\n"
            "Cloud Revenue: $43.1B (+26% YoY)\n"
            "Search Revenue: $198.1B (+12% YoY)\n"
            "Cash Position: $93.2B\n"
            "Sector: Technology — Internet Services"
        )
    },
}


# ═══════════════════════════════════════════════
# Load Portfolio from CSV
# ═══════════════════════════════════════════════

def load_portfolio(file_path: str = PORTFOLIO_PATH) -> Optional[list[dict]]:
    """
    Load portfolio holdings from a CSV file.

    CSV format:
        ticker,shares,cost_basis
        AAPL,100,150.00
        MSFT,50,280.00

    Args:
        file_path: Path to the portfolio CSV

    Returns:
        List of holding dicts, or None on error
    """
    try:
        holdings = []
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                holdings.append({
                    "ticker": row["ticker"].strip().upper(),
                    "shares": int(row["shares"]),
                    "cost_basis": float(row["cost_basis"])
                })

        tickers = ", ".join(h["ticker"] for h in holdings)
        print(f"✓ Loaded {len(holdings)} holdings: {tickers}")
        return holdings

    except FileNotFoundError:
        print(f"❌ Portfolio file not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error loading portfolio: {e}")
        return None


# ═══════════════════════════════════════════════
# Enrich Holdings with Financial Data
# ═══════════════════════════════════════════════

def enrich_holdings(holdings: list[dict]) -> list[dict]:
    """
    Add financial data to each holding from the built-in dataset.

    In a real app, you'd call the SEC EDGAR API here (see Example 01).

    Args:
        holdings: List of holding dicts from load_portfolio()

    Returns:
        Holdings with added "financial_data" and "company_name" fields
    """
    print("\n📥 Fetching financial data...")
    enriched = []
    for h in holdings:
        ticker = h["ticker"]
        if ticker in SAMPLE_FINANCIAL_DATA:
            info = SAMPLE_FINANCIAL_DATA[ticker]
            h["company_name"] = info["company_name"]
            h["financial_data"] = info["data"]
            print(f"  ✓ {ticker}: {info['company_name']}")
        else:
            h["company_name"] = ticker
            h["financial_data"] = "No detailed financial data available"
            print(f"  ⚠ {ticker}: No data available (will use general knowledge)")
        enriched.append(h)

    return enriched


# ═══════════════════════════════════════════════
# Structured Analysis Chain
#
# The key difference from previous examples:
#
#   Before:  chain = prompt | llm | StrOutputParser()
#            → Returns a string
#
#   Now:     chain = prompt | llm.with_structured_output(HoldingAnalysis)
#            → Returns a typed Pydantic object
#
# with_structured_output() tells Claude to return data matching
# the Pydantic schema exactly. No regex parsing needed.
# ═══════════════════════════════════════════════

def create_analysis_chain():
    """
    Create a chain that returns structured HoldingAnalysis objects.

    Returns:
        LCEL chain: dict → HoldingAnalysis
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a senior portfolio analyst at an investment firm. "
         "Analyze individual stock holdings based on their financial data. "
         "Be objective, data-driven, and concise. Your analysis will be "
         "used in a client portfolio report."),
        ("human", """Analyze this portfolio holding:

Ticker: {ticker}
Company: {company_name}
Position: {shares} shares at ${cost_basis}/share cost basis

Current Financial Data:
{financial_data}

Provide your structured analysis.""")
    ])

    llm = ChatAnthropic(model=MODEL, temperature=0)

    # with_structured_output returns Pydantic objects, not strings.
    # Claude sees the Pydantic schema and returns data matching it exactly.
    structured_llm = llm.with_structured_output(HoldingAnalysis)

    chain = prompt | structured_llm
    return chain


# ═══════════════════════════════════════════════
# Batch Process Holdings
#
# chain.batch() processes multiple inputs concurrently.
# Much faster than sequential chain.invoke() calls.
#
#   Slow: for h in holdings: chain.invoke(h)  # 5 sequential API calls
#   Fast: chain.batch(holdings)               # up to 3 concurrent calls
# ═══════════════════════════════════════════════

def analyze_all_holdings(holdings: list[dict]) -> Optional[list[HoldingAnalysis]]:
    """
    Analyze all holdings using batch processing.

    Args:
        holdings: Enriched holding dicts (with financial_data)

    Returns:
        List of HoldingAnalysis Pydantic objects
    """
    chain = create_analysis_chain()

    # Prepare inputs for batch processing
    inputs = [
        {
            "ticker": h["ticker"],
            "company_name": h["company_name"],
            "shares": h["shares"],
            "cost_basis": h["cost_basis"],
            "financial_data": h["financial_data"]
        }
        for h in holdings
    ]

    print(f"\n🤖 Analyzing {len(inputs)} holdings (batch processing)...")

    try:
        # Batch process — LangChain handles concurrency
        results = chain.batch(inputs, config={"max_concurrency": MAX_CONCURRENCY})
        print(f"✓ Analyzed {len(results)}/{len(inputs)} holdings")
        return results
    except Exception as e:
        print(f"❌ Error during batch analysis: {e}")
        return None


# ═══════════════════════════════════════════════
# Generate Portfolio Report
#
# Because analyses are Pydantic objects (not raw text), we can:
# - Sort by risk level or star rating
# - Filter for specific recommendations
# - Calculate aggregate statistics
# - Format consistently and programmatically
# ═══════════════════════════════════════════════

def generate_report(analyses: list[HoldingAnalysis], holdings: list[dict]) -> str:
    """
    Generate a formatted portfolio report from structured analyses.

    Args:
        analyses: List of HoldingAnalysis Pydantic objects
        holdings: Original holding data for cost basis info

    Returns:
        Formatted report string
    """
    lines = []

    # Header
    lines.append("═" * 60)
    lines.append("                    PORTFOLIO REPORT")
    lines.append("═" * 60)

    # Portfolio Summary
    lines.append("\n📊 Portfolio Summary")
    lines.append("─" * 40)
    lines.append(f"  Total Holdings:  {len(analyses)}")

    # Count by risk level
    risk_counts = {}
    for a in analyses:
        risk_counts[a.risk_level] = risk_counts.get(a.risk_level, 0) + 1
    risk_str = ", ".join(f"{v} {k}" for k, v in sorted(risk_counts.items()))
    lines.append(f"  Risk Breakdown:  {risk_str}")

    # Average star rating
    avg_stars = sum(a.star_rating for a in analyses) / max(len(analyses), 1)
    lines.append(f"  Avg Rating:      {'⭐' * round(avg_stars)} ({avg_stars:.1f}/5)")

    # Individual Holdings
    lines.append("\n📈 Holdings Analysis")
    lines.append("─" * 40)
    for analysis in analyses:
        stars = "⭐" * analysis.star_rating
        lines.append(f"\n  {analysis.ticker} — {analysis.company_name}")
        lines.append(f"  ├─ Outlook: {analysis.outlook} {stars}")
        lines.append(f"  ├─ Risk: {analysis.risk_level}")
        lines.append(f"  ├─ Action: {analysis.recommendation}")
        lines.append(f"  ├─ Strengths: {', '.join(analysis.key_strengths)}")
        lines.append(f"  ├─ Risks: {', '.join(analysis.key_risks)}")
        lines.append(f"  └─ {analysis.summary}")

    # Action Items
    lines.append("\n⚠️  Action Items")
    lines.append("─" * 40)

    high_risk = [a for a in analyses if a.risk_level == "HIGH"]
    if high_risk:
        lines.append(f"  • Review high-risk positions: {', '.join(a.ticker for a in high_risk)}")

    sells = [a for a in analyses if a.recommendation in ("SELL", "TRIM")]
    if sells:
        for a in sells:
            lines.append(f"  • {a.recommendation} {a.ticker}: {a.summary.split('.')[0]}")

    buys = [a for a in analyses if a.recommendation == "BUY"]
    if buys:
        lines.append(f"  • Consider adding to: {', '.join(a.ticker for a in buys)}")

    holds = [a for a in analyses if a.recommendation == "HOLD"]
    if holds:
        lines.append(f"  • Maintain positions: {', '.join(a.ticker for a in holds)}")

    lines.append("\n" + "═" * 60)

    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════

def main():
    """Load portfolio, analyze holdings, generate report."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set.")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    print("\n💼 Portfolio Report Generator")
    print("=" * 40)

    # Step 1: Load portfolio
    print(f"\n📂 Loading portfolio from {os.path.basename(PORTFOLIO_PATH)}...")
    holdings = load_portfolio()
    if not holdings:
        sys.exit(1)

    # Step 2: Enrich with financial data
    holdings = enrich_holdings(holdings)

    # Step 3: Analyze all holdings (batch)
    analyses = analyze_all_holdings(holdings)
    if not analyses:
        sys.exit(1)

    # Step 4: Generate report
    report = generate_report(analyses, holdings)
    print("\n")
    print(report)


if __name__ == "__main__":
    main()
