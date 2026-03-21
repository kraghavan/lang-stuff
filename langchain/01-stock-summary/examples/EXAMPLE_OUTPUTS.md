# Example Outputs — Stock Summary Generator

These are examples of what the completed application produces.

---

## Example 1: Apple (AAPL) — Stable Large-Cap

```
📈 Stock Summary Generator
========================================

Enter a stock ticker (e.g., AAPL, MSFT, TSLA): AAPL

📥 Fetching data for AAPL from SEC EDGAR...
✓ Company: APPLE INC (CIK: 0000320193)
✓ Retrieved financial data

🤖 Generating analysis with Claude...
✓ Analysis complete

════════════════════════════════════════════════════════
               AAPL — STOCK SUMMARY
════════════════════════════════════════════════════════

📊 Key Metrics:
  Revenue:          $391.0B (as of 2024-09-28)
  Net Income:       $101.2B (as of 2024-09-28)
  Total Assets:     $365.0B (as of 2024-09-28)
  Total Liabilities: $290.4B (as of 2024-09-28)
  Operating Income: $123.2B (as of 2024-09-28)

📈 Performance Assessment:
  Apple continues to deliver strong profitability with a net
  margin of approximately 25.9%, among the highest in the tech
  sector. Revenue shows moderate but consistent growth, driven
  by the expanding Services segment which now contributes over
  20% of total revenue. The company maintains a healthy balance
  sheet despite significant share buyback activity.

💡 Outlook:
  Stable. Apple's ecosystem moat and recurring services revenue
  provide strong defensive characteristics. Key catalysts include
  AI integration across product lines and continued growth in
  emerging markets.

════════════════════════════════════════════════════════
```

---

## Example 2: Tesla (TSLA) — High-Growth / Volatile

```
📈 Stock Summary Generator
========================================

Enter a stock ticker (e.g., AAPL, MSFT, TSLA): TSLA

📥 Fetching data for TSLA from SEC EDGAR...
✓ Company: TESLA INC (CIK: 0001318605)
✓ Retrieved financial data

🤖 Generating analysis with Claude...
✓ Analysis complete

════════════════════════════════════════════════════════
               TSLA — STOCK SUMMARY
════════════════════════════════════════════════════════

📊 Key Metrics:
  Revenue:          $96.8B (as of 2024-12-31)
  Net Income:       $7.1B (as of 2024-12-31)
  Total Assets:     $122.1B (as of 2024-12-31)
  Total Liabilities: $48.3B (as of 2024-12-31)
  Operating Income: $7.6B (as of 2024-12-31)

📈 Performance Assessment:
  Tesla demonstrates strong revenue growth but faces margin
  compression amid aggressive pricing strategies and increased
  competition in the EV market. Net margin of ~7.3% is below
  historical highs but reflects deliberate investment in
  manufacturing scale and AI/autonomy capabilities. The balance
  sheet remains conservative with low leverage.

💡 Outlook:
  Mixed. Near-term headwinds from pricing pressure and EV
  competition, offset by long-term optionality in autonomous
  driving, energy storage, and robotics. High variance outcome.

════════════════════════════════════════════════════════
```

---

## Example 3: JPMorgan Chase (JPM) — Financial Sector

```
📈 Stock Summary Generator
========================================

Enter a stock ticker (e.g., AAPL, MSFT, TSLA): JPM

📥 Fetching data for JPM from SEC EDGAR...
✓ Company: JPMORGAN CHASE & CO (CIK: 0000019617)
✓ Retrieved financial data

🤖 Generating analysis with Claude...
✓ Analysis complete

════════════════════════════════════════════════════════
               JPM — STOCK SUMMARY
════════════════════════════════════════════════════════

📊 Key Metrics:
  Revenue:          $177.6B (as of 2024-12-31)
  Net Income:       $58.5B (as of 2024-12-31)
  Total Assets:     $4.0T (as of 2024-12-31)
  Total Liabilities: $3.6T (as of 2024-12-31)
  Operating Income: Not available

📈 Performance Assessment:
  JPMorgan Chase delivered record profitability driven by
  strong net interest income in the higher rate environment
  and resilient investment banking activity. As the largest
  US bank by assets, the company benefits from scale advantages
  and diversified revenue streams across consumer banking,
  corporate & investment banking, and asset management.

💡 Outlook:
  Positive with caution. Elevated interest rates continue to
  support net interest margins, though potential rate cuts
  could moderate this tailwind. Credit quality remains strong
  but bears monitoring as the economic cycle matures.

════════════════════════════════════════════════════════
```

---

## Example 4: Invalid Ticker — Error Handling

```
📈 Stock Summary Generator
========================================

Enter a stock ticker (e.g., AAPL, MSFT, TSLA): ZZZZZ

📥 Fetching data for ZZZZZ from SEC EDGAR...
✗ Could not find CIK for ticker: ZZZZZ

✗ Analysis failed. Please try again.
```

---

## What to Notice

1. **Consistent format** — The prompt template ensures every summary has the same sections
2. **Real data** — Numbers come directly from SEC EDGAR filings
3. **Sector-aware** — Claude adapts analysis style based on the company type
4. **Graceful errors** — Invalid tickers are handled cleanly
5. **Data-driven** — The analysis references actual metrics, not generic statements
