# 📊 Earnings Analyzer

An intelligent SEC earnings report analyzer that iteratively investigates company financials and explains anomalies.

## 🎯 What It Does

Analyzes company earnings reports with adaptive deep-dive capabilities:

1. Fetches latest SEC filing (10-K or 10-Q)
2. Extracts key financial metrics (revenue, profit, EPS, etc.)
3. Compares to previous quarters/years
4. Detects anomalies (unusual changes)
5. **Iteratively investigates** anomalies until explained
6. Generates comprehensive analysis report

## 🌟 Why LangGraph?

This problem **requires** LangGraph (vs simple LangChain) because:

- ✅ **Conditional investigation** - Only dig deeper if anomalies detected
- ✅ **Iterative loops** - Keep searching for explanations until found
- ✅ **State management** - Track what we've found, what we're looking for
- ✅ **Dynamic depth** - Some companies need shallow analysis, others need deep dives

## 📁 Files in This Example

```
01-earnings-analyzer/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── simple_version.py           # Basic single-company analyzer
├── comparative_version.py      # Compare two companies (future)
├── sec_api.py                  # SEC EDGAR API utilities
├── examples/
│   ├── example_outputs.md      # Sample outputs
│   └── tesla_analysis.txt      # Real analysis example
└── data/
    └── (no files - fetches from SEC API in real-time)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
# Add to your ~/.bashrc or ~/.zshrc
export ANTHROPIC_API_KEY="your-key-here"

# Or set for current session
export ANTHROPIC_API_KEY="your-key-here"
```

### 3. Run the Analyzer

```bash
python simple_version.py
```

You'll be prompted to enter:
- Company ticker (e.g., TSLA, AAPL, MSFT)
- Period (e.g., Q4 2024, Q3 2024)

### Example Usage

```bash
$ python simple_version.py

🔍 SEC Earnings Analyzer
Enter company ticker: TSLA
Enter period (e.g., Q4 2024): Q4 2024

📥 Fetching Tesla's Q4 2024 filing from SEC...
✅ Found 10-K filing from 2024-01-29

📊 Extracting financial metrics...
✅ Extracted: Revenue, Net Income, Operating Expenses, R&D, SG&A

🔎 Comparing to historical data...
⚠️  Anomaly detected: Operating expenses increased 45% YoY

🕵️  Investigating anomaly...
📰 Searching for context...
✅ Found explanation: Major AI infrastructure investment

📝 Generating report...

=== TESLA Q4 2024 EARNINGS ANALYSIS ===

Key Metrics:
- Revenue: $96.8B (+19% YoY)
- Net Income: $14.9B (+115% YoY)
- Gross Margin: 18.2% (+1.5pp YoY)

Anomalies Detected:
⚠️  Operating Expenses: $8.5B (+45% YoY)

Investigation Results:
Tesla significantly increased spending on AI infrastructure
and Full Self-Driving development. This is a strategic
investment expected to yield returns in future quarters.

Conclusion:
Strong revenue growth with healthy profitability despite
increased R&D spending. OpEx increase is intentional and
aligned with long-term strategy.
```

## 🏗️ Architecture

### LangGraph Flow

```
┌─────────────┐
│ User Input  │
│ (Ticker +   │
│  Period)    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ fetch_filing    │ ◄─── Calls SEC EDGAR API
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ extract_metrics │ ◄─── Parses XBRL/financial data
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ compare_history │ ◄─── Gets previous quarters
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ detect_anomaly  │ ◄─── Statistical checks
│                 │
└────────┬────────┘
         │
         ├─────────► Anomaly found?
         │                │
         │ No             │ Yes
         │                ▼
         │         ┌─────────────────┐
         │         │ investigate     │ ◄─── Search news, context
         │         │                 │
         │         └────────┬────────┘
         │                  │
         │                  │ Explained?
         │                  │
         │         No       │        Yes
         │         ◄────────┘
         │         (loop back)
         │
         ▼
┌─────────────────┐
│ generate_report │ ◄─── Summarize findings
│                 │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │  END   │
    └────────┘
```

### State Structure

```python
class EarningsState(TypedDict):
    # Input
    ticker: str
    period: str
    
    # Data fetched
    filing: dict
    current_metrics: dict
    historical_metrics: list[dict]
    
    # Analysis
    anomalies: list[dict]
    investigation_results: list[dict]
    
    # Control flow
    investigation_depth: int
    max_depth: int
    
    # Output
    final_report: str
```

## 📊 Data Source: SEC EDGAR

### What is SEC EDGAR?

The SEC's Electronic Data Gathering, Analysis, and Retrieval system contains:
- **18+ million filings** from public companies
- **All public companies** must file here
- **Completely free** - no API key needed
- **Updated daily** with new filings

### Filings We Use

- **10-K**: Annual report (comprehensive)
- **10-Q**: Quarterly report
- **8-K**: Current events (earnings releases)

### Example API Calls

```python
# Get company information
https://data.sec.gov/submissions/CIK0000789019.json  # Microsoft

# Get financial statements
https://data.sec.gov/api/xbrl/companyfacts/CIK0000789019.json
```

## 🛠️ Key Components

### 1. SEC API Client (`sec_api.py`)

```python
class SECClient:
    def get_company_cik(ticker: str) -> str:
        """Convert ticker to CIK number"""
    
    def get_latest_filing(cik: str, form_type: str) -> dict:
        """Fetch most recent 10-K or 10-Q"""
    
    def extract_financials(filing_url: str) -> dict:
        """Parse XBRL data into metrics"""
```

### 2. LangGraph Nodes

Each node is a function that processes state:

```python
def fetch_filing(state: EarningsState) -> EarningsState:
    """Fetch filing from SEC EDGAR"""
    cik = get_company_cik(state["ticker"])
    filing = get_latest_filing(cik, "10-Q")
    state["filing"] = filing
    return state

def detect_anomaly(state: EarningsState) -> EarningsState:
    """Compare metrics and flag unusual changes"""
    for metric, value in state["current_metrics"].items():
        historical = get_historical_value(metric)
        pct_change = calculate_change(value, historical)
        
        if abs(pct_change) > 25:  # 25% threshold
            state["anomalies"].append({
                "metric": metric,
                "change": pct_change,
                "current": value,
                "previous": historical
            })
    return state
```

### 3. Conditional Routing

```python
def should_investigate(state: EarningsState) -> str:
    """Decide whether to investigate further"""
    if len(state["anomalies"]) == 0:
        return "finish"
    
    if state["investigation_depth"] >= state["max_depth"]:
        return "finish"
    
    # Check if we have unexplained anomalies
    unexplained = [a for a in state["anomalies"] 
                   if not a.get("explained")]
    
    if len(unexplained) > 0:
        return "investigate"
    
    return "finish"
```

## 📈 Example Outputs

### Simple Case (No Anomalies)

```
Apple Q3 2024 Analysis

Metrics:
- Revenue: $85.8B (+5% YoY) ✓
- Net Income: $21.4B (+8% YoY) ✓
- Gross Margin: 45.6% (+0.2pp) ✓

No significant anomalies detected.
Steady performance across all metrics.
```

### Complex Case (With Investigation)

```
Tesla Q4 2024 Analysis

Metrics:
- Revenue: $96.8B (+19% YoY) ✓
- Net Income: $14.9B (+115% YoY) ✓✓
- Operating Expenses: $8.5B (+45% YoY) ⚠️

Anomaly Investigation:

1. Operating Expenses (+45%)
   Investigation depth: 1
   → Searched Q4 earnings call transcript
   → Found: "Accelerating AI compute investment"
   → Explanation: Strategic AI infrastructure spend
   ✓ Explained

2. Net Income (+115%)
   Investigation depth: 1
   → Checked gross margin trends
   → Found: Improved manufacturing efficiency
   → Explanation: Higher volumes + better margins
   ✓ Explained

Conclusion:
Strong quarter with intentional OpEx increase for AI.
Net income surge driven by operational improvements.
```

## 🧪 Testing

Run tests to verify components:

```bash
# Test SEC API connection
python -c "from sec_api import SECClient; print(SECClient().get_company_cik('AAPL'))"

# Test with a simple company
python simple_version.py
# Enter: AAPL
# Enter: Q4 2024
```

## 🔧 Configuration

Edit `simple_version.py` to customize:

```python
# Anomaly detection threshold
ANOMALY_THRESHOLD = 25  # percent change

# Investigation depth
MAX_INVESTIGATION_DEPTH = 3

# Metrics to track
TRACKED_METRICS = [
    "revenue",
    "net_income", 
    "operating_expenses",
    "gross_margin"
]
```

## 🚧 Future Enhancements

- [ ] `comparative_version.py` - Compare two companies
- [ ] Sector analysis - Compare to industry peers
- [ ] Time series trends - Multi-quarter analysis
- [ ] Alert system - Notify on unusual patterns
- [ ] PDF report generation
- [ ] Visualization dashboard
- [ ] Historical data caching

## 📚 Resources

**SEC EDGAR:**
- [SEC EDGAR API Docs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [Understanding Financial Statements](https://www.sec.gov/reportspubs/investor-publications/investorpubsbegfinstmtguidehtml.html)

**LangGraph:**
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)

**Company Research:**
- [Yahoo Finance](https://finance.yahoo.com/)
- [Seeking Alpha](https://seekingalpha.com/)
- [Company SEC Filings](https://www.sec.gov/edgar/searchedgar/companysearch.html)

## 💡 Learning Outcomes

After completing this example, you'll understand:

✅ When to use LangGraph vs LangChain
✅ How to design stateful workflows
✅ Implementing conditional routing
✅ Building iterative investigation loops
✅ Working with SEC EDGAR API
✅ Parsing financial data (XBRL)
✅ Creating explainable AI systems

---

**Ready to analyze some earnings? Let's go! 🚀**

```bash
python simple_version.py
```