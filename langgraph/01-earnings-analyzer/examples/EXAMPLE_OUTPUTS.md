# Example Outputs

This file shows what you can expect from the Earnings Analyzer.

## Example 1: Simple Analysis (No Anomalies)

**Input:**
```
Ticker: AAPL
Period: Q3 2024
```

**Output:**
```
🔍 SEC Earnings Analyzer
===============================================

📊 APPLE INC. - Q3 2024 ANALYSIS

Filing Information:
- Form Type: 10-Q
- Filing Date: 2024-08-03
- Fiscal Period: Q3 2024

Financial Metrics:
┌──────────────────────┬───────────┬───────────┬──────────┐
│ Metric               │ Current   │ Previous  │ Change   │
├──────────────────────┼───────────┼───────────┼──────────┤
│ Revenue              │ $85.8B    │ $81.8B    │ +4.9%    │
│ Net Income           │ $21.4B    │ $19.9B    │ +7.5%    │
│ Operating Expenses   │ $14.3B    │ $13.4B    │ +6.7%    │
│ Gross Margin         │ 45.6%     │ 44.3%     │ +1.3pp   │
└──────────────────────┴───────────┴───────────┴──────────┘

Anomaly Detection:
✓ No significant anomalies detected
✓ All metrics within expected ranges
✓ Healthy quarter-over-quarter growth

Summary:
Apple delivered a solid Q3 with steady growth across all
major metrics. Revenue and net income increased in line
with historical trends. No unusual patterns requiring
further investigation.
```

---

## Example 2: Complex Analysis (With Investigation)

**Input:**
```
Ticker: TSLA
Period: Q4 2024
```

**Output:**
```
🔍 SEC Earnings Analyzer
===============================================

📊 TESLA INC. - Q4 2024 ANALYSIS

Filing Information:
- Form Type: 10-K
- Filing Date: 2024-01-29
- Fiscal Period: Q4 2024 (Full Year)

Financial Metrics:
┌──────────────────────┬───────────┬───────────┬──────────┐
│ Metric               │ Current   │ Previous  │ Change   │
├──────────────────────┼───────────┼───────────┼──────────┤
│ Revenue              │ $96.8B    │ $81.5B    │ +18.8%   │
│ Net Income           │ $14.9B    │ $6.9B     │ +115.9%  │
│ Operating Expenses   │ $8.5B     │ $5.9B     │ +44.1%   │
│ R&D Spending         │ $3.8B     │ $2.6B     │ +46.2%   │
└──────────────────────┴───────────┴───────────┴──────────┘

⚠️  Anomaly Detection:
┌─────────────────────┬──────────┬────────────────────┐
│ Metric              │ Change   │ Severity           │
├─────────────────────┼──────────┼────────────────────┤
│ Net Income          │ +115.9%  │ High (Positive)    │
│ Operating Expenses  │ +44.1%   │ Medium (Concern)   │
│ R&D Spending        │ +46.2%   │ Medium (Concern)   │
└─────────────────────┴──────────┴────────────────────┘

🕵️  Investigation Results:

Anomaly #1: Net Income (+115.9%)
────────────────────────────────
Investigation Depth: 2

Step 1: Initial Analysis
→ Checked gross margin trends
→ Found: Margins improved from 16.7% to 18.2%
→ Reason: Economies of scale in manufacturing

Step 2: Deep Dive
→ Searched earnings call transcript
→ Found: "Record production volumes with improved efficiency"
→ Additional context: Lower battery costs, optimized supply chain

✓ Explanation: Net income surge driven by:
  - Higher production volumes (+35%)
  - Improved manufacturing efficiency
  - Lower per-unit costs at scale
  
Status: ✓ EXPLAINED


Anomaly #2: Operating Expenses (+44.1%)
────────────────────────────────────────
Investigation Depth: 2

Step 1: Initial Analysis
→ Breakdown: R&D (+46%), SG&A (+42%)
→ Concern: OpEx growing faster than revenue

Step 2: Strategic Context
→ Searched 10-K "Management Discussion"
→ Found: "Accelerating AI and autonomy investments"
→ Key quote: "We are significantly increasing our AI compute 
   infrastructure to support FSD and Optimus development"

✓ Explanation: OpEx increase is intentional:
  - AI infrastructure buildout ($2.1B)
  - FSD development acceleration
  - Optimus humanoid robot R&D
  - Strategic investment for future growth
  
Status: ✓ EXPLAINED


Final Assessment:
═══════════════════════════════════════════════════

Overall Rating: STRONG QUARTER ⭐⭐⭐⭐

Key Takeaways:
1. Revenue growth remains healthy at 19% YoY
2. Profitability improved significantly through efficiency gains
3. Increased OpEx is strategic, not operational concern
4. Company is investing heavily in future capabilities (AI, FSD)

Risks to Monitor:
- High R&D spending may pressure margins in short term
- AI infrastructure costs could continue to rise
- Need to see ROI on FSD/autonomy investments

Recommendation:
Strong operational performance with intentional strategic
investments. The OpEx increase is well-explained and aligned
with long-term growth strategy. Net income surge demonstrates
operational excellence and economies of scale.
```

---

## Example 3: Comparative Analysis (Future Feature)

**Input:**
```
Compare: TSLA vs RIVN
Period: Q4 2024
```

**Output:**
```
🔍 SEC Earnings Analyzer - COMPARATIVE MODE
===============================================

📊 TESLA vs RIVIAN - Q4 2024

Side-by-Side Metrics:
┌────────────────┬───────────┬───────────┬─────────────┐
│ Metric         │ Tesla     │ Rivian    │ Difference  │
├────────────────┼───────────┼───────────┼─────────────┤
│ Revenue        │ $96.8B    │ $4.4B     │ 22x         │
│ Gross Margin   │ 18.2%     │ -38.7%    │ +56.9pp     │
│ Net Income     │ $14.9B    │ -$1.5B    │ $16.4B      │
│ R&D % Revenue  │ 3.9%      │ 18.2%     │ -14.3pp     │
└────────────────┴───────────┴───────────┴─────────────┘

Key Insights:
• Tesla: Profitable at scale, investing in AI
• Rivian: Still in growth phase, negative margins
• Different lifecycle stages - not directly comparable
```

---

## Example 4: Error Handling

**Input:**
```
Ticker: INVALID
Period: Q4 2024
```

**Output:**
```
❌ Error: Company not found

Could not find SEC filing for ticker "INVALID"

Troubleshooting:
1. Check if ticker symbol is correct (e.g., TSLA not TESLA)
2. Ensure company is publicly traded in US
3. Verify company files with SEC (private companies don't)

Need help? Try these valid tickers:
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Google)
- TSLA (Tesla)
- NVDA (Nvidia)
```

---

## Tips for Best Results

1. **Use major public companies** - Better data availability
2. **Recent quarters work best** - More context available
3. **Check filing dates** - Some companies have different fiscal years
4. **Be patient** - Deep investigations may take 30-60 seconds

## What Makes a Good Test Case?

**Easy (Good for first run):**
- AAPL, MSFT, GOOGL - Stable, predictable
- Usually no major anomalies
- Good for testing basic flow

**Medium (Interesting):**
- TSLA, NVDA, AMD - More volatile
- Often have anomalies to investigate
- Good for testing investigation loops

**Advanced (Complex):**
- Startups post-IPO (RIVN, LCID)
- Recent acquisitions/restructuring
- Companies with unusual quarters
- Good for testing edge cases