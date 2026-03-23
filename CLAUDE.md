# Claude Code Instructions for lang-stuff

## Project Overview

**lang-stuff** is an educational repository for learning the LangChain ecosystem (LangChain, LangGraph, LangSmith) through real-world examples targeting software engineers.

- **Purpose**: Hands-on learning with complete, runnable examples
- **Target Audience**: Software engineers learning agentic AI patterns
- **Primary LLM**: Anthropic Claude (via langchain-anthropic)
- **All code is complete** — no TODOs, no stubs, ready to run

## Directory Structure

```
lang-stuff/
├── langchain/                          # Simple chains (4 examples)
│   ├── 01-stock-summary/              # LCEL basics (prompt | llm | parser)
│   ├── 02-financial-news-analyzer/    # Sequential chains (RunnablePassthrough)
│   ├── 03-sec-filing-qa/             # RAG (embeddings, vectors, retrieval)
│   ├── 04-portfolio-report-generator/ # Structured output (Pydantic) + batch
│   └── smoke_test.sh                  # 8 tests
│
├── langgraph/                          # Complex agentic workflows (5 examples + observability)
│   ├── 01-ci-cd-tracker/             # Linear state management (no LLM needed)
│   ├── 02-fraud-detection/           # Conditional routing (--no-llm available)
│   ├── 03-devops-agent/              # ReAct / tool calling (deep agents)
│   ├── 04-migration-approval/        # Human-in-the-loop (HITL)
│   ├── 05-trading-team/             # Multi-agent with veto + negotiation
│   ├── 06-observability/            # LangSmith tracing + Grafana integration
│   └── smoke_test.sh                 # 12 tests
│
├── langsmith/                          # Points to langgraph/06-observability
└── langflow/                           # Planned
```

## API Keys Required

```bash
# Required for most examples
ANTHROPIC_API_KEY=sk-ant-...

# Optional — only for observability (06)
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_TRACING_V2=true

# Optional — for SEC EDGAR examples
SEC_API_USER_AGENT=Your Name <your@email.com>
```

**No API key needed** for: langgraph/01 (CI/CD Tracker), langgraph/02 with `--no-llm`, observability/04 (fraud evaluation).

## Key Conventions

### Code Style
- **Python 3.10+** required
- Use **type hints** everywhere (`TypedDict`, `Literal`, `Optional`)
- **Docstrings** for all functions (Google style)
- Descriptive variable names over comments
- Keep functions focused (single responsibility)

### File Organization
- Each example is **self-contained** — no cross-example imports
- `main.py` — primary entry point for each example
- `test_*.py` — test script (runs without API key where possible)
- `README.md` — one per example (overview + walkthrough + challenges)
- Data modules alongside main code (e.g., `fraud_data.py`, `market_data.py`)

### LangGraph Patterns
```python
# State: TypedDict shared across all nodes
class MyState(TypedDict):
    input: str
    data: dict
    results: list

# Nodes: Functions that transform state
def my_node(state: MyState) -> MyState:
    state["results"] = process(state["data"])
    return state

# Routing: Functions that return edge names
def route_logic(state: MyState) -> Literal["path_a", "path_b"]:
    if state["score"] > 0.7:
        return "path_a"
    return "path_b"
```

### LangChain Patterns
```python
# LCEL: prompt | llm | parser
chain = ChatPromptTemplate.from_messages([...]) | ChatAnthropic(...) | StrOutputParser()
result = chain.invoke({"ticker": "AAPL", "data": "..."})

# Sequential: RunnablePassthrough.assign() accumulates data
pipeline = (
    RunnablePassthrough.assign(summary=summarize_chain)
    | RunnablePassthrough.assign(sentiment=sentiment_chain)
    | brief_chain
)
```

## Smoke Tests

Each module has a smoke test to verify everything works:

```bash
cd langchain && ./smoke_test.sh      # 8 tests
cd langgraph && ./smoke_test.sh      # 12 tests
./smoke_test.sh 01 03                # Run specific examples only
```

## When Adding New Code

1. **Read existing code first** — match the patterns in current examples
2. **Keep examples self-contained** — no cross-imports between examples
3. **Include a README.md** — overview, architecture, walkthrough, challenges, checklist
4. **Include a test script** — `test_*.py` that runs offline where possible
5. **Add to smoke_test.sh** — every new example gets a smoke test entry
6. **All code must be complete** — no TODOs, no `pass` stubs, runnable out of the box

## AI Assistant Guidelines

### When Asked to Code
- **Match existing style** — follow patterns in current examples
- **All code complete** — students clone and run, nothing left to implement
- **Explain in README** — walkthrough how the code works + challenges to try
- **Test it** — run the smoke tests before declaring done

### What NOT to Do
- ❌ Don't leave TODO stubs or `pass` statements
- ❌ Don't create separate LEARNING_GUIDE.md files (use README.md)
- ❌ Don't add dependencies without discussing first
- ❌ Don't over-engineer — keep examples focused on the pattern they teach
- ❌ Don't create cross-example imports

## Resources

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangChain Docs](https://python.langchain.com/)
- [LangSmith Docs](https://docs.smith.langchain.com/)
- [Anthropic API](https://docs.anthropic.com/)
- [SEC EDGAR API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)

---

**Last Updated**: 2026-03-22
**Primary Maintainer**: Karthika Raghavan
