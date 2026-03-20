"""
Financial News Analyzer — LangChain Sequential Pipeline

A multi-step pipeline that summarizes news, analyzes sentiment,
and generates an investment brief using sequential LCEL chains.

Architecture:
    Headlines → Summarize Chain → Sentiment Chain → Brief Chain → Report

Key Concepts:
    - Multiple PromptTemplates (one per step)
    - RunnablePassthrough.assign() for accumulating data
    - Sequential chain composition

Usage:
    python simple_version.py

Requires:
    - ANTHROPIC_API_KEY environment variable
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_anthropic import ChatAnthropic

# Local imports
from news_data import get_news, format_headlines

# Load environment variables
load_dotenv()

# ═══════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
MAX_TOKENS = 1024


# ═══════════════════════════════════════════════
# Shared LLM instance
# ═══════════════════════════════════════════════

def get_llm() -> ChatAnthropic:
    """Create a shared LLM instance for all chains."""
    return ChatAnthropic(
        model=MODEL,
        temperature=0,
        max_tokens=MAX_TOKENS
    )


# ═══════════════════════════════════════════════
# Step 1: Summarize Chain
#
# Takes raw headlines and condenses them into key themes.
# Input:  {"headlines": "1. [Reuters] NVIDIA reports...\n2. ..."}
# Output: String summary of key themes
# ═══════════════════════════════════════════════

def create_summarize_chain():
    """
    Create a chain that summarizes news headlines into key themes.

    Returns:
        LCEL chain (prompt | llm | parser)
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a financial news analyst who identifies key themes "
         "and trends from news headlines. Be concise and focus on "
         "what matters most for investors."),
        ("human", """Summarize these financial news headlines into 2-3 key themes.
Focus on:
- Major business developments
- Financial performance signals
- Market-moving events

Headlines:
{headlines}

Provide a concise thematic summary (2-3 short paragraphs).""")
    ])

    llm = get_llm()
    parser = StrOutputParser()

    return prompt | llm | parser


# ═══════════════════════════════════════════════
# Step 2: Sentiment Chain
#
# Takes the summary from Step 1 and rates market sentiment.
# Input:  {"summary": "NVIDIA continues to dominate..."}
# Output: Sentiment analysis string
#
# NOTE: The input variable is {summary}, NOT {headlines} —
# this chain receives the OUTPUT of the summarize chain.
# ═══════════════════════════════════════════════

def create_sentiment_chain():
    """
    Create a chain that analyzes sentiment from a news summary.

    Returns:
        LCEL chain (prompt | llm | parser)
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a market sentiment analyst. You assess news sentiment "
         "objectively using a structured framework. Be data-driven and "
         "avoid emotional language."),
        ("human", """Analyze the market sentiment of this financial news summary:

{summary}

Provide:
1. Overall sentiment: BULLISH, BEARISH, or NEUTRAL
2. Confidence: 0-100%
3. Key positive drivers (2-3 bullet points)
4. Key concerns (1-2 bullet points)

Format as plain text with clear labels.""")
    ])

    llm = get_llm()
    parser = StrOutputParser()

    return prompt | llm | parser


# ═══════════════════════════════════════════════
# Step 3: Investment Brief Chain
#
# Takes ALL accumulated data (ticker, summary, sentiment)
# and produces a professional investment brief.
#
# Input:  {"ticker": "NVDA", "company_name": "NVIDIA",
#          "summary": "...", "sentiment": "..."}
# Output: Professional investment brief string
# ═══════════════════════════════════════════════

def create_brief_chain():
    """
    Create a chain that generates an investment brief.

    Returns:
        LCEL chain (prompt | llm | parser)
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a senior investment strategist writing a morning brief "
         "for portfolio managers. Be concise, actionable, and professional. "
         "Always include a specific action recommendation."),
        ("human", """Generate a concise investment brief for {ticker} ({company_name}).

News Summary:
{summary}

Sentiment Analysis:
{sentiment}

Write a brief with these sections:
📰 News Summary (2-3 sentences)
📊 Sentiment Analysis (key points)
💼 Investment Brief (2-3 sentences with a specific action: BUY/HOLD/SELL with conditions)

Keep the total brief under 250 words.""")
    ])

    llm = get_llm()
    parser = StrOutputParser()

    return prompt | llm | parser


# ═══════════════════════════════════════════════
# Full Pipeline
#
# Composes all 3 chains using RunnablePassthrough.assign().
#
# RunnablePassthrough.assign() is the key concept here:
# - It runs a chain and ADDS the result to the existing data
# - Original fields are preserved (ticker, company_name, headlines)
# - New fields accumulate at each step (summary, sentiment)
#
# Data flow:
#   Input:    {"ticker": "NVDA", "company_name": "...", "headlines": "..."}
#   Step 1:   + {"summary": "Key themes: AI demand..."}
#   Step 2:   + {"sentiment": "BULLISH (85%)..."}
#   Step 3:   → final brief string (not a dict, just the output)
# ═══════════════════════════════════════════════

def create_analysis_pipeline():
    """
    Compose the full 3-step analysis pipeline using LCEL.

    Returns:
        Complete pipeline runnable
    """
    summarize = create_summarize_chain()
    sentiment = create_sentiment_chain()
    brief = create_brief_chain()

    pipeline = (
        # Step 1: Run summarize chain, store result as "summary"
        # Input:  {"ticker": "NVDA", "company_name": "...", "headlines": "..."}
        # Output: {"ticker": "NVDA", ..., "headlines": "...", "summary": "Key themes..."}
        RunnablePassthrough.assign(summary=summarize)

        # Step 2: Run sentiment chain (uses "summary" from step 1), store as "sentiment"
        # Input:  {..., "summary": "Key themes..."}
        # Output: {..., "summary": "...", "sentiment": "BULLISH (85%)..."}
        | RunnablePassthrough.assign(sentiment=sentiment)

        # Step 3: Run brief chain (uses all accumulated fields), return final string
        # Input:  {"ticker": "NVDA", "company_name": "...", "summary": "...", "sentiment": "..."}
        # Output: "NVIDIA's dominance in AI accelerators..." (just a string)
        | brief
    )

    return pipeline


# ═══════════════════════════════════════════════
# Main Analysis Function
# ═══════════════════════════════════════════════

def analyze_news(ticker: str) -> Optional[str]:
    """
    Load news and run the complete analysis pipeline.

    Args:
        ticker: Stock symbol (e.g., "NVDA", "AAPL", "TSLA")

    Returns:
        Investment brief string, or None on error
    """
    # Step 1: Load news data
    print(f"\n📥 Loading news for {ticker}...")
    news = get_news(ticker)
    if not news:
        return None

    print(f"✓ Found {len(news['headlines'])} recent headlines")

    # Step 2: Format headlines for the prompt
    formatted = format_headlines(news)

    # Step 3: Create and run the pipeline
    print("\n🔗 Running analysis pipeline...")
    pipeline = create_analysis_pipeline()

    print("  Step 1/3: Summarizing headlines...")
    # We invoke the full pipeline — each step prints internally
    result = pipeline.invoke({
        "ticker": ticker,
        "company_name": news["company_name"],
        "headlines": formatted
    })

    print("  ✓ All steps complete")
    return result


# ═══════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════

def main():
    """Interactive financial news analyzer."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set.")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    print("\n📰 Financial News Analyzer")
    print("=" * 40)

    ticker = input("\nEnter a stock ticker (e.g., AAPL, TSLA, NVDA): ").strip().upper()

    if not ticker:
        print("✗ No ticker entered. Exiting.")
        sys.exit(1)

    result = analyze_news(ticker)

    if result:
        print("\n")
        print("═" * 56)
        print(f"{'':>12}{ticker} — INVESTMENT BRIEF")
        print("═" * 56)
        print(result)
        print("═" * 56)
    else:
        print("\n✗ Analysis failed. Please try again.")


if __name__ == "__main__":
    main()
