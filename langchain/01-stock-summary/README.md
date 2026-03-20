# 📈 Stock Summary Generator

A LangChain-powered tool that fetches real stock data and generates professional analyst-style summaries using Claude.

## 🎯 What It Does

Takes a stock ticker and produces a structured financial summary:

1. Fetches real company financial data from SEC EDGAR (free, no API key)
2. Formats the data into a prompt template
3. Sends to Claude for intelligent analysis
4. Parses the response into a clean, structured summary

## 🌟 Why LangChain?

This is a **perfect LangChain use case** because:

- ✅ **Linear flow** - Fetch → Format → Analyze → Output (no loops needed)
- ✅ **Prompt templates** - Reusable prompt with variable injection
- ✅ **Output parsing** - Convert Claude's response into structured data
- ✅ **Single pass** - No need to revisit previous steps

**Why NOT LangGraph?**
- ❌ No conditional branching needed
- ❌ No loops or iteration
- ❌ No multi-agent coordination
- ❌ No shared mutable state

## 📁 Files in This Example

```
01-stock-summary/
├── README.md                # This file
├── LEARNING_GUIDE.md        # Step-by-step TODO tutorial
├── requirements.txt         # Python dependencies
├── simple_version.py        # Main implementation (has TODOs for learning)
├── stock_data.py            # Stock data fetcher (SEC EDGAR)
└── examples/
    └── EXAMPLE_OUTPUTS.md   # Sample outputs for reference
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd langchain/01-stock-summary
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### 3. Run It

```bash
python simple_version.py
```

You'll be prompted for a stock ticker:
```
📈 Stock Summary Generator
Enter a stock ticker (e.g., AAPL, MSFT, TSLA): AAPL
```

### Example Output

```
📈 Stock Summary Generator
Enter a stock ticker (e.g., AAPL, MSFT, TSLA): AAPL

📥 Fetching data for AAPL from SEC EDGAR...
✓ Company: APPLE INC (CIK: 0000320193)
✓ Retrieved financial data

🤖 Generating analysis with Claude...
✓ Analysis complete

════════════════════════════════════════════════════════
                 AAPL — STOCK SUMMARY
════════════════════════════════════════════════════════

Company: Apple Inc.
Sector: Technology — Consumer Electronics

📊 Key Metrics:
  Revenue (TTM):        $391.0B
  Net Income (TTM):     $101.2B
  Profit Margin:        25.9%

📈 Performance:
  Revenue Growth (YoY): +5.2%
  Income Growth (YoY):  +8.1%

💡 Analysis:
  Apple continues to demonstrate strong profitability
  with industry-leading margins. Revenue growth has
  moderated but remains positive, driven by services
  segment expansion offsetting slower hardware sales.

⚖️  Outlook: Stable
  The company's massive cash position and ecosystem
  lock-in provide strong defensive characteristics.

════════════════════════════════════════════════════════
```

## 🏗️ Architecture

### LangChain Flow (LCEL)

```
┌──────────────┐     ┌───────────────┐     ┌─────────────┐     ┌──────────────┐
│  Fetch Data  │ ──► │ Prompt        │ ──► │   Claude     │ ──► │ Output       │
│  (SEC EDGAR) │     │ Template      │     │   (LLM)      │     │ Parser       │
└──────────────┘     └───────────────┘     └─────────────┘     └──────────────┘
    stock_data.py        PromptTemplate       ChatAnthropic       StrOutputParser
```

In LCEL (LangChain Expression Language), this looks like:

```python
chain = prompt | llm | parser
result = chain.invoke({"ticker": "AAPL", "data": financial_data})
```

### How It Works Step-by-Step

```
1. User enters "AAPL"
       │
       ▼
2. stock_data.py calls SEC EDGAR API
   GET https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json
       │
       ▼
3. Raw financial data extracted
   {
     "revenue": [{"val": 391035000000, "end": "2024-09-28"}],
     "net_income": [{"val": 101218000000, "end": "2024-09-28"}],
     ...
   }
       │
       ▼
4. Data injected into prompt template
   "You are a financial analyst. Analyze AAPL with this data: ..."
       │
       ▼
5. Claude generates analysis
   "Apple Inc. continues to show strong fundamentals..."
       │
       ▼
6. Output parser formats the response
   Clean, structured summary displayed to user
```

## 📊 Data Source: SEC EDGAR

This example reuses the SEC EDGAR API from the langgraph examples:

- **Free** - No API key required
- **Real data** - Actual company financials from SEC filings
- **Rate limit** - 10 requests/second (be respectful)
- **User-Agent** - Required header (set via `SEC_API_USER_AGENT` env var)

### What We Fetch

| Data Point | SEC XBRL Concept | Description |
|-----------|-------------------|-------------|
| Revenue | `Revenues` or `RevenueFromContractWithCustomerExcludingAssessedTax` | Total sales |
| Net Income | `NetIncomeLoss` | Bottom line profit |
| Total Assets | `Assets` | Everything the company owns |
| Total Liabilities | `Liabilities` | Everything the company owes |
| Operating Income | `OperatingIncomeLoss` | Profit from core operations |

## 🛠️ Key LangChain Concepts You'll Learn

### 1. PromptTemplate

Templates let you create reusable prompts with variable placeholders:

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a senior financial analyst at a top investment bank."),
    ("human", """Analyze {ticker} based on this SEC filing data:

Revenue: {revenue}
Net Income: {net_income}
Total Assets: {total_assets}

Provide a concise stock summary.""")
])
```

**Why this matters**: Templates separate your prompt logic from your data, making it reusable and testable.

### 2. ChatAnthropic (LLM)

The bridge between LangChain and Claude:

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    temperature=0,        # Deterministic output for financial analysis
    max_tokens=1024       # Limit response length
)
```

**Why `temperature=0`?** Financial analysis should be consistent and factual, not creative.

### 3. StrOutputParser

Converts the LLM's message object into a plain string:

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
# Turns AIMessage(content="Analysis...") into just "Analysis..."
```

### 4. LCEL (The Pipe Operator)

LangChain Expression Language lets you compose chains with `|`:

```python
# This creates a complete chain
chain = prompt | llm | parser

# Same as manually doing:
# message = prompt.format_messages(ticker="AAPL", ...)
# response = llm.invoke(message)
# text = parser.parse(response)
```

**Why LCEL?** It's concise, composable, and supports streaming/batching for free.

## 🧪 Testing

### Good Test Cases

| Ticker | Why It's Good | Expected Behavior |
|--------|---------------|-------------------|
| AAPL | Large, stable, well-known | Clean summary, all metrics available |
| MSFT | Major tech company | Complete data, strong metrics |
| TSLA | Volatile, high-growth | More interesting analysis, growth metrics |
| JPM | Financial sector | Different metric focus (banking) |
| AMZN | Mixed business model | Revenue vs profit tension |

### Testing Incrementally

```bash
# Step 1: Test data fetching
python -c "from stock_data import get_stock_data; print(get_stock_data('AAPL'))"

# Step 2: Test the full chain
python simple_version.py
# Enter: AAPL

# Step 3: Try a complex company
python simple_version.py
# Enter: TSLA
```

## 🔧 Configuration

Edit `simple_version.py` to customize:

```python
# Change the model
MODEL = "claude-sonnet-4-5-20250929"  # or "claude-haiku-4-5-20251001" for speed

# Adjust response length
MAX_TOKENS = 1024

# Modify the analysis prompt
SYSTEM_PROMPT = "You are a senior financial analyst..."
```

## 💡 Learning Outcomes

After completing this example, you'll understand:

- ✅ How to create and use `ChatPromptTemplate`
- ✅ How to connect Claude via `ChatAnthropic`
- ✅ How to parse LLM output with `StrOutputParser`
- ✅ How to compose chains with LCEL (`prompt | llm | parser`)
- ✅ How to invoke chains with variable input
- ✅ How to fetch real financial data from SEC EDGAR
- ✅ When LangChain is the right tool (vs LangGraph)

## 🚧 Future Enhancements

- [ ] Add `JsonOutputParser` for machine-readable output
- [ ] Support multiple tickers in one run
- [ ] Add comparison mode (AAPL vs MSFT)
- [ ] Cache SEC data to reduce API calls
- [ ] Add streaming output (watch analysis appear in real-time)
- [ ] Export to PDF report

## 📚 Resources

- [LangChain PromptTemplate Docs](https://python.langchain.com/docs/concepts/prompt_templates/)
- [ChatAnthropic Integration](https://python.langchain.com/docs/integrations/chat/anthropic/)
- [LCEL Guide](https://python.langchain.com/docs/concepts/lcel/)
- [SEC EDGAR API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)

---

**Next up: [Financial News Analyzer](../02-financial-news-analyzer) — learn to chain multiple steps together →**
