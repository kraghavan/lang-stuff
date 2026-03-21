"""
Stock Summary Generator — LangChain Simple Version

Generates professional financial summaries using real SEC data and Claude.
This is your first LangChain project: learn prompts, LLMs, parsers, and LCEL.

Architecture:
    Fetch Data (SEC EDGAR) → Prompt Template → Claude (LLM) → Output Parser → Summary

Usage:
    python simple_version.py

Requires:
    - ANTHROPIC_API_KEY environment variable
    - Internet connection (for SEC EDGAR API)
"""

import os
import sys
from dotenv import load_dotenv

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

# Local imports
from stock_data import get_stock_data, format_large_number

# Load environment variables from .env file (if it exists)
load_dotenv()

# ═══════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
MAX_TOKENS = 1024


# ═══════════════════════════════════════════════
# Prompt Template
#
# Templates let you create reusable prompts with variable placeholders.
# The same template works for any ticker — you just swap the variables.
# ═══════════════════════════════════════════════

def create_analysis_prompt() -> ChatPromptTemplate:
    """
    Create a prompt template for stock analysis.

    The template includes:
    - A system message setting Claude as a financial analyst
    - A human message with placeholders: {ticker}, {company_name}, {financial_data}
    - Instructions for what sections to include in the analysis

    Returns:
        ChatPromptTemplate ready for use in an LCEL chain
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a senior financial analyst at a top investment bank. "
         "You provide concise, data-driven stock summaries based on SEC filing data. "
         "Always reference specific numbers from the data provided. "
         "Be objective and professional."),
        ("human", """Analyze {ticker} ({company_name}) based on this SEC filing data:

{financial_data}

Provide a concise stock summary with these sections:
1. 📊 Key Metrics — list each metric with its value
2. 📈 Performance Assessment — 2-3 sentences on financial health and trends
3. 💡 Outlook — 1-2 sentences on forward-looking view (Stable/Positive/Mixed/Negative)

Keep the total response under 200 words. Use plain text, no markdown headers.""")
    ])
    return prompt


# ═══════════════════════════════════════════════
# LLM Setup
#
# ChatAnthropic connects LangChain to Claude.
# temperature=0 for consistent, factual financial analysis.
# ═══════════════════════════════════════════════

def create_llm() -> ChatAnthropic:
    """
    Create and configure the Claude LLM for financial analysis.

    Returns:
        Configured ChatAnthropic instance
    """
    llm = ChatAnthropic(
        model=MODEL,
        temperature=0,        # Deterministic for financial analysis
        max_tokens=MAX_TOKENS
    )
    return llm


# ═══════════════════════════════════════════════
# LCEL Chain
#
# LangChain Expression Language (LCEL) uses the pipe operator (|)
# to compose chains: prompt | llm | parser
#
# Each component transforms data and passes it to the next:
#   Input dict → prompt.invoke() → Messages → llm.invoke() → AIMessage → parser.invoke() → str
# ═══════════════════════════════════════════════

def create_summary_chain():
    """
    Build the complete analysis chain using LCEL.

    Chain: prompt → LLM → output parser

    Returns:
        A runnable chain that takes {ticker, company_name, financial_data}
        and returns a string analysis.
    """
    prompt = create_analysis_prompt()
    llm = create_llm()
    parser = StrOutputParser()

    # The pipe operator connects each component:
    # 1. prompt formats input dict → messages
    # 2. llm sends messages to Claude → AIMessage response
    # 3. parser extracts AIMessage.content → plain string
    chain = prompt | llm | parser
    return chain


# ═══════════════════════════════════════════════
# Main Analysis Function
# ═══════════════════════════════════════════════

def format_metrics_for_prompt(metrics: dict) -> str:
    """
    Format financial metrics into a readable string for the prompt.

    Args:
        metrics: Dictionary of metric_name → {value, end_date, formatted}

    Returns:
        Formatted string like:
        "Revenue: $391.0B (as of 2024-09-28)
         Net Income: $101.2B (as of 2024-09-28)
         ..."
    """
    lines = []
    for name, data in metrics.items():
        if data:
            formatted = data.get("formatted", format_large_number(data["value"]))
            lines.append(f"{name.replace('_', ' ').title()}: {formatted} (as of {data['end_date']})")
        else:
            lines.append(f"{name.replace('_', ' ').title()}: Not available")
    return "\n".join(lines)


def analyze_stock(ticker: str) -> str:
    """
    Fetch real stock data and generate an AI-powered analysis.

    Args:
        ticker: Stock symbol (e.g., "AAPL", "MSFT", "TSLA")

    Returns:
        Formatted stock summary string, or None on error
    """
    # Step 1: Fetch data from SEC EDGAR
    print(f"\n📥 Fetching data for {ticker} from SEC EDGAR...")
    data = get_stock_data(ticker)

    if not data:
        print(f"✗ Could not fetch data for {ticker}")
        return None

    print(f"✓ Company: {data['company_name']} (CIK: {data['cik']})")

    # Step 2: Format metrics for the prompt
    formatted_data = format_metrics_for_prompt(data["metrics"])
    print("✓ Retrieved financial data")

    # Step 3: Run the LCEL chain
    print("\n🤖 Generating analysis with Claude...")
    chain = create_summary_chain()

    result = chain.invoke({
        "ticker": ticker,
        "company_name": data["company_name"],
        "financial_data": formatted_data
    })

    print("✓ Analysis complete")
    return result


# ═══════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════

def main():
    """Interactive stock summary generator."""
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set.")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    print("\n📈 Stock Summary Generator")
    print("=" * 40)

    # Get user input
    ticker = input("\nEnter a stock ticker (e.g., AAPL, MSFT, TSLA): ").strip().upper()

    if not ticker:
        print("✗ No ticker entered. Exiting.")
        sys.exit(1)

    # Run analysis
    result = analyze_stock(ticker)

    if result:
        print("\n")
        print("═" * 56)
        print(f"{'':>15}{ticker} — STOCK SUMMARY")
        print("═" * 56)
        print(result)
        print("═" * 56)
    else:
        print("\n✗ Analysis failed. Please try again.")


if __name__ == "__main__":
    main()
