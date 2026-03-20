# 📰 Financial News Analyzer

A multi-step LangChain pipeline that fetches financial news, summarizes it, analyzes sentiment, and generates an investment brief — all using sequential chains.

## 🎯 What It Does

Processes financial news through a multi-step AI pipeline:

1. **Fetch** — Gets recent news headlines for a company (simulated dataset)
2. **Summarize** — Condenses multiple headlines into key themes
3. **Sentiment** — Analyzes overall market sentiment (bullish/bearish/neutral)
4. **Brief** — Generates a concise investment brief combining all insights

## 🌟 Why LangChain?

This is a great LangChain example because:

- ✅ **Sequential processing** — Each step feeds into the next
- ✅ **Multiple prompts** — Different prompts for different tasks
- ✅ **Chain composition** — Combine multiple chains into one pipeline
- ✅ **RunnableSequence** — Learn how to pipe outputs between steps

**Why NOT LangGraph?**
- ❌ No conditional branching — every article goes through the same pipeline
- ❌ No loops — we process once, not iteratively
- ❌ No shared mutable state — each step just passes data forward

## 📁 Files in This Example

```
02-financial-news-analyzer/
├── README.md                # This file
├── LEARNING_GUIDE.md        # Step-by-step TODO tutorial
├── requirements.txt         # Python dependencies
├── simple_version.py        # Main implementation (has TODOs)
├── news_data.py             # News data provider (sample dataset)
└── examples/
    └── EXAMPLE_OUTPUTS.md   # Sample outputs for reference
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd langchain/02-financial-news-analyzer
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

### Example Output

```
📰 Financial News Analyzer
========================================

Enter a stock ticker (e.g., AAPL, TSLA, NVDA): NVDA

📥 Loading news for NVDA...
✓ Found 5 recent headlines

🔗 Running analysis pipeline...

  Step 1/3: Summarizing headlines...
  ✓ Summary complete

  Step 2/3: Analyzing sentiment...
  ✓ Sentiment: BULLISH (confidence: 85%)

  Step 3/3: Generating investment brief...
  ✓ Brief complete

════════════════════════════════════════════════════════
           NVDA — INVESTMENT BRIEF
════════════════════════════════════════════════════════

📰 News Summary:
  NVIDIA continues to dominate the AI chip market with
  record data center revenue. Key themes include expanding
  partnerships with major cloud providers, new GPU
  architecture announcements, and growing demand for AI
  training infrastructure.

📊 Sentiment Analysis:
  Overall: BULLISH (85% confidence)
  Key Drivers:
  • Strong earnings beat (+22% above estimates)
  • Data center revenue growth (+154% YoY)
  • New product cycle beginning (Blackwell architecture)
  Concerns:
  • Elevated valuation multiples
  • Export restriction risks to China market

💼 Investment Brief:
  NVIDIA's dominance in AI accelerators positions it as
  the primary beneficiary of enterprise AI adoption. The
  news flow is overwhelmingly positive with multiple
  catalysts. However, current valuation prices in
  significant future growth. Suitable for growth-oriented
  portfolios with tolerance for volatility.

  Action: HOLD for existing positions, selective ADD on
  pullbacks below $120.

════════════════════════════════════════════════════════
```

## 🏗️ Architecture

### Sequential Chain Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  News Data   │ ──► │  Summarize   │ ──► │  Sentiment   │ ──► │  Investment  │
│  (headlines) │     │  Chain       │     │  Chain       │     │  Brief Chain │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
  news_data.py        Prompt + LLM         Prompt + LLM         Prompt + LLM
                      "Condense these       "Rate sentiment      "Generate brief
                       headlines..."         of this summary..."  from all data..."
```

### How the Pipeline Flows

```
Headlines (list[str])
    │
    ▼
┌─────────────────────────────────────────┐
│ STEP 1: Summarize                       │
│                                         │
│ Input:  5 news headlines                │
│ Prompt: "Summarize these financial      │
│          headlines into key themes..."  │
│ Output: 2-3 paragraph summary           │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ STEP 2: Sentiment Analysis              │
│                                         │
│ Input:  Summary from Step 1             │
│ Prompt: "Analyze the sentiment of this  │
│          financial summary. Rate as     │
│          BULLISH/BEARISH/NEUTRAL..."    │
│ Output: Sentiment + confidence + drivers│
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│ STEP 3: Investment Brief                │
│                                         │
│ Input:  Summary + Sentiment from above  │
│ Prompt: "Generate a concise investment  │
│          brief combining the summary    │
│          and sentiment analysis..."     │
│ Output: Professional investment brief   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
            Final Report
```

### LCEL Implementation

```python
# Each step is its own mini-chain
summarize_chain = summarize_prompt | llm | StrOutputParser()
sentiment_chain = sentiment_prompt | llm | StrOutputParser()
brief_chain     = brief_prompt     | llm | StrOutputParser()

# Combined into a pipeline using RunnablePassthrough
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

pipeline = (
    RunnablePassthrough.assign(summary=summarize_chain)
    | RunnablePassthrough.assign(sentiment=sentiment_chain)
    | brief_chain
)
```

## 📰 News Data

This example uses a **sample dataset** of financial news headlines. In a production app, you'd replace this with a real news API.

### Sample Headlines (Built-in)

The `news_data.py` file includes curated headlines for popular tickers:

| Ticker | Theme | Headlines |
|--------|-------|-----------|
| AAPL | Product + Services | iPhone sales, services growth, AI features |
| TSLA | EV + Autonomy | Delivery numbers, FSD updates, competition |
| NVDA | AI + Data Center | Chip demand, partnerships, new architectures |
| MSFT | Cloud + AI | Azure growth, Copilot adoption, OpenAI |
| JPM | Banking + Economy | Interest rates, credit quality, deal flow |

### Why Sample Data?

- **Free** — No news API key needed
- **Consistent** — Same results for everyone following the tutorial
- **Focused** — Headlines curated to demonstrate different sentiment patterns
- **Extensible** — Easy to add your own headlines or swap in a real API

## 🛠️ Key LangChain Concepts You'll Learn

### 1. Multiple Prompt Templates

Different tasks need different prompts:

```python
# Summarization prompt
summarize_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a financial news analyst."),
    ("human", "Summarize these headlines:\n{headlines}")
])

# Sentiment prompt (different task, different instructions)
sentiment_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a market sentiment analyst."),
    ("human", "Analyze the sentiment of this summary:\n{summary}")
])
```

### 2. RunnablePassthrough

Passes data through unchanged while adding new fields:

```python
from langchain_core.runnables import RunnablePassthrough

# This runs summarize_chain and adds its output as "summary"
# while keeping all existing input fields intact
step1 = RunnablePassthrough.assign(summary=summarize_chain)
```

**Why this matters**: Each step needs data from previous steps. `RunnablePassthrough.assign()` lets you accumulate results as you go.

### 3. RunnableParallel

Run multiple chains simultaneously:

```python
from langchain_core.runnables import RunnableParallel

# Run summarize and sentiment analysis at the same time
parallel_step = RunnableParallel(
    summary=summarize_chain,
    sentiment=sentiment_chain
)
```

### 4. Chain Composition

Combine mini-chains into a larger pipeline:

```python
# Each step is a small chain
step1 = summarize_prompt | llm | parser
step2 = sentiment_prompt | llm | parser
step3 = brief_prompt | llm | parser

# Compose into a pipeline
full_pipeline = (
    RunnablePassthrough.assign(summary=step1)
    | RunnablePassthrough.assign(sentiment=step2)
    | step3
)
```

## 🧪 Testing

### Test Cases

| Ticker | Expected Sentiment | Why |
|--------|-------------------|-----|
| NVDA | Bullish | Strong AI demand, record revenue |
| AAPL | Neutral/Slightly Bullish | Stable but mature growth |
| TSLA | Mixed/Volatile | Positive delivery + negative margin pressure |

### Testing Incrementally

```bash
# Step 1: Test news data loading
python -c "from news_data import get_news; print(get_news('NVDA'))"

# Step 2: Test summarize step alone
python simple_version.py
# Enter: AAPL

# Step 3: Compare different tickers
# Run with NVDA (bullish) vs TSLA (mixed) and compare
```

## 🔧 Configuration

```python
# Change the model
MODEL = "claude-sonnet-4-5-20250929"

# Adjust sentiment thresholds
# In the sentiment prompt, you can modify what counts as
# "bullish" vs "bearish" by changing the prompt instructions

# Add more tickers
# Edit news_data.py to add headlines for new companies
```

## 💡 Learning Outcomes

After completing this example, you'll understand:

- ✅ How to create **multiple prompt templates** for different tasks
- ✅ How to use **RunnablePassthrough.assign()** to accumulate results
- ✅ How to compose **multi-step pipelines** with LCEL
- ✅ How to pass data between chain steps
- ✅ The difference between **sequential** and **parallel** chain execution
- ✅ How to debug multi-step chains by testing each step independently

## 🔗 Comparison: This vs Example 01

| Feature | 01-Stock Summary | 02-News Analyzer |
|---------|-----------------|------------------|
| Chain steps | 1 (single prompt) | 3 (sequential) |
| Prompts | 1 template | 3 templates |
| Data flow | Direct (input → output) | Accumulated (each step adds) |
| LCEL | `prompt \| llm \| parser` | `assign(summary=...) \| assign(sentiment=...) \| brief` |
| Key concept | Basic LCEL | RunnablePassthrough, chain composition |

## 🚧 Future Enhancements

- [ ] Real news API integration (e.g., NewsAPI, Alpha Vantage)
- [ ] Streaming output (watch each step happen in real-time)
- [ ] Compare sentiment across multiple tickers
- [ ] Historical sentiment tracking
- [ ] Add `RunnableParallel` to run summarize + sentiment simultaneously
- [ ] Export to email-ready format

## 📚 Resources

- [LCEL Chaining Guide](https://python.langchain.com/docs/how_to/sequence/)
- [RunnablePassthrough](https://python.langchain.com/docs/how_to/passthrough/)
- [RunnableParallel](https://python.langchain.com/docs/how_to/parallel/)
- [ChatAnthropic](https://python.langchain.com/docs/integrations/chat/anthropic/)

---

**Next up: [SEC Filing Q&A](../03-sec-filing-qa) — learn Retrieval-Augmented Generation (RAG) →**
