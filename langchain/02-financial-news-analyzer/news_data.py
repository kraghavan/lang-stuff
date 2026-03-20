"""
Financial News Data Provider — Sample Dataset

Provides curated financial news headlines for learning purposes.
In a production app, you'd replace this with a real news API
(e.g., NewsAPI, Alpha Vantage, Bloomberg).

Why sample data?
- No API key needed (free for everyone)
- Consistent results (same output for everyone following the tutorial)
- Curated to demonstrate different sentiment patterns

Usage:
    from news_data import get_news, format_headlines
    news = get_news("NVDA")
    formatted = format_headlines(news)
"""

from typing import Optional


# ═══════════════════════════════════════════════
# News Database
#
# Curated headlines for popular tickers.
# Each ticker has a mix of positive/negative headlines
# to produce realistic sentiment analysis.
#
# NVDA → Mostly positive (AI boom) → Expected: BULLISH
# TSLA → Mixed (deliveries up, margins down) → Expected: MIXED
# AAPL → Stable (steady growth) → Expected: SLIGHTLY BULLISH
# MSFT → Positive (cloud + AI) → Expected: BULLISH
# JPM → Mixed (rates changing) → Expected: NEUTRAL
# ═══════════════════════════════════════════════

NEWS_DATABASE = {
    "NVDA": {
        "company_name": "NVIDIA Corporation",
        "headlines": [
            {
                "title": "NVIDIA Reports Record Q4 Revenue of $22.1B, Beating Estimates by 12%",
                "source": "Reuters",
                "date": "2025-02-21"
            },
            {
                "title": "AI Chip Demand Surges as Enterprises Accelerate Infrastructure Spending",
                "source": "Bloomberg",
                "date": "2025-02-20"
            },
            {
                "title": "NVIDIA Announces Next-Gen Blackwell Ultra Architecture for AI Training",
                "source": "The Verge",
                "date": "2025-02-18"
            },
            {
                "title": "Major Cloud Providers Expand NVIDIA GPU Orders by 40% for 2025",
                "source": "CNBC",
                "date": "2025-02-17"
            },
            {
                "title": "Analysts Warn NVIDIA Valuation Stretched Despite Strong Fundamentals",
                "source": "Financial Times",
                "date": "2025-02-15"
            },
        ]
    },
    "TSLA": {
        "company_name": "Tesla Inc.",
        "headlines": [
            {
                "title": "Tesla Delivers Record 495,000 Vehicles in Q4, Beating Estimates",
                "source": "Reuters",
                "date": "2025-01-03"
            },
            {
                "title": "Tesla Gross Margins Decline to 17.6% Amid Aggressive Price Cuts",
                "source": "Bloomberg",
                "date": "2025-01-25"
            },
            {
                "title": "Tesla FSD v12 Shows Significant Improvement in Independent Testing",
                "source": "TechCrunch",
                "date": "2025-02-10"
            },
            {
                "title": "Chinese EV Makers BYD, NIO Gain Market Share at Tesla's Expense",
                "source": "Financial Times",
                "date": "2025-02-05"
            },
            {
                "title": "Tesla Energy Storage Business Grows 75% YoY, Emerging as Key Revenue Driver",
                "source": "CNBC",
                "date": "2025-02-12"
            },
        ]
    },
    "AAPL": {
        "company_name": "Apple Inc.",
        "headlines": [
            {
                "title": "Apple Services Revenue Hits Record $24.2B in Q1, Up 13% Year-Over-Year",
                "source": "CNBC",
                "date": "2025-01-30"
            },
            {
                "title": "iPhone 16 Sales Track In-Line With Expectations, No Major Surprise",
                "source": "Bloomberg",
                "date": "2025-02-01"
            },
            {
                "title": "Apple Intelligence Features Drive Modest Upgrade Cycle Acceleration",
                "source": "The Verge",
                "date": "2025-02-08"
            },
            {
                "title": "Apple Faces Continued Headwinds in China as Local Brands Gain Ground",
                "source": "Financial Times",
                "date": "2025-02-03"
            },
            {
                "title": "EU Digital Markets Act Forces Apple to Allow Alternative App Stores on iOS",
                "source": "Reuters",
                "date": "2025-01-28"
            },
        ]
    },
    "MSFT": {
        "company_name": "Microsoft Corporation",
        "headlines": [
            {
                "title": "Microsoft Azure Revenue Grows 29% as Enterprise Cloud Migration Accelerates",
                "source": "Reuters",
                "date": "2025-01-28"
            },
            {
                "title": "Microsoft Copilot Adoption Exceeds Expectations with 50M+ Enterprise Users",
                "source": "Bloomberg",
                "date": "2025-02-15"
            },
            {
                "title": "Microsoft Reports Q2 Revenue of $62B, Up 16% Year-Over-Year",
                "source": "CNBC",
                "date": "2025-01-28"
            },
            {
                "title": "OpenAI Partnership Gives Microsoft Unique Edge in Enterprise AI Market",
                "source": "The Information",
                "date": "2025-02-10"
            },
            {
                "title": "Microsoft Capital Expenditure Surges to $14B as AI Infrastructure Buildout Continues",
                "source": "Financial Times",
                "date": "2025-02-01"
            },
        ]
    },
    "JPM": {
        "company_name": "JPMorgan Chase & Co.",
        "headlines": [
            {
                "title": "JPMorgan Reports Record Annual Profit of $58.5B on Strong Net Interest Income",
                "source": "Reuters",
                "date": "2025-01-15"
            },
            {
                "title": "Federal Reserve Signals Potential Rate Cuts, Creating Headwinds for Bank NII",
                "source": "Bloomberg",
                "date": "2025-02-05"
            },
            {
                "title": "JPMorgan Investment Banking Fees Rise 18% as Deal Activity Recovers",
                "source": "CNBC",
                "date": "2025-01-15"
            },
            {
                "title": "Consumer Credit Quality Remains Strong Despite Economic Uncertainty Fears",
                "source": "Financial Times",
                "date": "2025-01-20"
            },
            {
                "title": "Jamie Dimon Warns of Geopolitical Risks and Persistent Inflation Threats",
                "source": "Bloomberg",
                "date": "2025-02-08"
            },
        ]
    },
}


def get_news(ticker: str) -> Optional[dict]:
    """
    Get sample news headlines for a given ticker.

    Args:
        ticker: Stock symbol (e.g., "NVDA", "AAPL", "TSLA")

    Returns:
        {
            "ticker": "NVDA",
            "company_name": "NVIDIA Corporation",
            "headlines": [
                {"title": "...", "source": "Reuters", "date": "2025-02-21"},
                ...
            ]
        }
        or None if ticker not in database
    """
    ticker = ticker.upper()
    if ticker not in NEWS_DATABASE:
        print(f"✗ No news data available for {ticker}")
        print(f"  Available tickers: {', '.join(NEWS_DATABASE.keys())}")
        return None

    data = NEWS_DATABASE[ticker]
    return {
        "ticker": ticker,
        "company_name": data["company_name"],
        "headlines": data["headlines"]
    }


def format_headlines(news: dict) -> str:
    """
    Format news headlines into a prompt-ready string.

    Takes the output of get_news() and formats it as a numbered list
    with source and date context.

    Args:
        news: Dictionary from get_news()

    Returns:
        Formatted string like:
        "1. [Reuters, 2025-02-21] NVIDIA Reports Record Q4 Revenue..."

    Example:
        >>> news = get_news("NVDA")
        >>> print(format_headlines(news))
        1. [Reuters, 2025-02-21] NVIDIA Reports Record Q4 Revenue of $22.1B
        ...
    """
    lines = []
    for i, headline in enumerate(news["headlines"], 1):
        lines.append(f"{i}. [{headline['source']}, {headline['date']}] {headline['title']}")
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# Test the module directly
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    print("📰 Testing News Data Provider")
    print("=" * 40)

    for ticker in ["NVDA", "AAPL", "TSLA"]:
        print(f"\n--- {ticker} ---")
        news = get_news(ticker)
        if news:
            print(f"Company: {news['company_name']}")
            print(f"Headlines: {len(news['headlines'])}")
            formatted = format_headlines(news)
            print(formatted)
        else:
            print("No data available")
