# lang-stuff

Hands-on learning of the LangChain ecosystem through real-world examples. Built for **software engineers** who want to understand agentic AI patterns.

## 🔑 What You Need

| Requirement | Where to Get It | Used By |
|---|---|---|
| **Python 3.10+** | [python.org](https://www.python.org/downloads/) | Everything |
| **Anthropic API Key** | [console.anthropic.com](https://console.anthropic.com/) | LangChain (most examples), LangGraph (examples 03-05) |
| **LangSmith API Key** (optional) | [smith.langchain.com](https://smith.langchain.com) (free: 5,000 traces/month) | Observability module (06) |
| **Docker** (optional) | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) | Grafana integration only |

```bash
# Set your Anthropic key (required for most examples)
export ANTHROPIC_API_KEY="sk-ant-..."

# Set LangSmith key (optional — only for observability)
export LANGCHAIN_API_KEY="lsv2_pt_..."
export LANGCHAIN_TRACING_V2=true
```

> **Note:** LangGraph examples 01 (CI/CD Tracker) and 02 (Fraud Detection with `--no-llm`) run without any API key.

## 📂 What's Inside

```
lang-stuff/
├── langchain/         ← Simple chains and patterns (4 examples)
├── langgraph/         ← Complex agentic workflows (5 examples + observability)
└── langsmith/         ← Points to langgraph/06-observability
```

## 🎓 Learning Path

### Phase 1: LangChain — Learn the Basics

Simple linear chains. No loops, no branching.

| # | Example | What You Learn | API Key? |
|---|---------|---------------|----------|
| 01 | [Stock Summary](langchain/01-stock-summary) | PromptTemplate, ChatAnthropic, LCEL (`prompt \| llm \| parser`) | Yes |
| 02 | [News Analyzer](langchain/02-financial-news-analyzer) | Sequential chains, `RunnablePassthrough.assign()` | Yes |
| 03 | [SEC Filing Q&A](langchain/03-sec-filing-qa) | RAG — embeddings, vectors, retrieval | Yes |
| 04 | [Portfolio Report](langchain/04-portfolio-report-generator) | Structured output (Pydantic), `chain.batch()` | Yes |

```bash
cd langchain/01-stock-summary
pip install -r requirements.txt
python simple_version.py   # Enter: AAPL
```

### Phase 2: LangGraph — Add Loops, Branches, Agents

Complex workflows that need state, conditionals, tool calling, and multi-agent coordination.

| # | Example | Pattern | API Key? |
|---|---------|---------|----------|
| 01 | [CI/CD Tracker](langgraph/01-ci-cd-tracker) | Linear state management | **No** |
| 02 | [Fraud Detection](langgraph/02-fraud-detection) | Conditional routing | Optional (`--no-llm`) |
| 03 | [DevOps Agent](langgraph/03-devops-agent) | ReAct / tool calling (deep agents) | Yes |
| 04 | [Migration Approval](langgraph/04-migration-approval) | Human-in-the-loop (HITL) | Yes |
| 05 | [Trading Team](langgraph/05-trading-team) | Multi-agent with veto + negotiation | Yes |

```bash
cd langgraph/01-ci-cd-tracker
pip install -r ../requirements.txt
python main.py             # No API key needed!
```

### Phase 3: Observability — Debug and Monitor

Add LangSmith tracing to your LangGraph workflows. Track costs, latency, accuracy.

| # | Example | What You Learn | API Key? |
|---|---------|---------------|----------|
| 01 | [Setup](langgraph/06-observability/01-setup) | Configure LangSmith | LangSmith |
| 02 | [Trace DevOps Agent](langgraph/06-observability/02-trace-devops-agent) | Trace tool-calling loops | Both |
| 03 | [Monitor Trading Team](langgraph/06-observability/03-monitor-trading-team) | Trace multi-agent negotiations | Both |
| 04 | [Evaluate Fraud](langgraph/06-observability/04-evaluate-fraud) | Test accuracy on 20 transactions | **No** |
| 05 | [Production Monitoring](langgraph/06-observability/05-production-monitoring) | Cost & latency reports | LangSmith |
| — | [Grafana Integration](langgraph/06-observability/grafana-integration) | LangSmith → Prometheus → Grafana | LangSmith + Docker |

## 🧪 Smoke Tests

Each module has a smoke test script to verify everything works:

```bash
cd langchain && ./smoke_test.sh     # 8 tests
cd langgraph && ./smoke_test.sh     # 12 tests
```

## 🧭 When to Use What

| Tool | Use When | Analogy |
|------|----------|---------|
| **LangChain** | Simple A → B → C flow, no loops | Scriptwriter |
| **LangGraph** | Loops, branches, agents, multi-agent | Director |
| **LangSmith** | Debugging, cost tracking, accuracy testing | Editor |

## 🛠️ Tech Stack

- Python 3.10+
- LangChain / LangGraph / LangSmith
- Anthropic Claude (via `langchain-anthropic`)
- SEC EDGAR API (free, no key needed)
- HuggingFace Embeddings (local, no key needed)
- FAISS (in-memory vector store)
- Prometheus + Grafana (optional, via Docker)

## 📄 License

MIT

---

**Start with [LangChain Example 01](langchain/01-stock-summary) or [LangGraph Example 01](langgraph/01-ci-cd-tracker) →**
