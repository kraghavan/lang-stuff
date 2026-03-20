# lang-stuff

Hands-on explorations of the LangChain ecosystem through real-world financial applications.

## 🎯 What's Inside

A learning journey through LangChain's toolkit, starting with complex agentic workflows and expanding to cover chains, observability, and visual prototyping.

### Current Focus: LangGraph (Agentic Workflows) ✅
- **📊 Earnings Analyzer** - Iterative SEC filing investigation with adaptive deep-dives ✅
- **💰 Loan Approval** - Risk-based decision pipeline with multi-path conditional routing ✅
- **🚨 Fraud Detection** - Pattern matching with adaptive investigation loops ✅

### Coming Soon
- **LangChain** - Simple chains and basic patterns
- **LangSmith** - Debugging, testing, and observability
- **LangFlow** - Visual workflow prototyping

## 🧭 The Ecosystem

| Tool | Purpose | Analogy | Status |
|------|---------|---------|--------|
| **LangChain** | Build applications/chains | The scriptwriter (sets up steps) | 📋 Planned |
| **LangGraph** | Orchestrate complex agentic flows | The director (handles loops & branches) | ✅ Complete |
| **LangSmith** | Observe, debug, and test | The editor (reviews and improves) | 📋 Planned |
| **LangFlow** | Visual drag-and-drop IDE | The sandbox (rapid prototyping) | 📋 Planned |

## 🚀 Quick Start

```bash
# Clone the repo
git clone git@github.com:kraghavan/lang-stuff.git
cd lang-stuff

# Start with LangGraph examples
cd langgraph/01-earnings-analyzer

# Install dependencies
pip install -r ../requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Run the earnings analyzer
python simple_version.py

# Or test the system first
python test_analyzer.py
```

## 📂 Repository Structure

```
lang-stuff/
├── langgraph/          # Complex multi-agent workflows (✅ Complete)
│   ├── requirements.txt
│   ├── 01-earnings-analyzer/
│   │   ├── sec_api.py
│   │   ├── simple_version.py
│   │   └── test_analyzer.py
│   ├── 02-loan-approval/
│   │   ├── loan_data.py
│   │   └── loan_analyzer.py
│   └── 03-fraud-detection/
│       ├── fraud_data.py
│       └── fraud_detector.py
├── langchain/          # Simple chains and basic patterns (📋 Coming)
├── langsmith/          # Debugging and observability (📋 Coming)  
├── langflow/           # Visual workflow prototypes (📋 Coming)
└── shared/             # Common utilities across all examples
```

## 🎓 Learning Path

### Phase 1: Master LangGraph ✅ (Complete)
Start with agentic workflows to understand when you need more than simple chains.

1. **Earnings Analyzer** ✅ → Iterative investigation loops and state management
2. **Loan Approval** ✅ → Multi-path routing and risk-based decisions
3. **Fraud Detection** ✅ → Pattern matching with conditional investigation

**What you'll learn:**
- State management across complex workflows
- Conditional routing (different paths based on data)
- Iterative loops (investigate until confident)
- When to use LangGraph vs simple chains

### Phase 2: Learn LangChain 📋
After understanding complex graphs, appreciate when simple chains are enough.

### Phase 3: Add Observability 📋  
Use LangSmith to debug and improve your workflows.

### Phase 4: Rapid Prototyping 📋
Use LangFlow to visualize and test ideas quickly.

## 💡 Why This Repo

Most tutorials show toy examples. This repo uses:
- **Real data**: SEC filings (18M+ documents), Lending Club patterns (2.2M+ loans), fraud datasets
- **Real problems**: Financial analysis, credit decisions, fraud prevention
- **Real patterns**: State management, conditional routing, iterative investigation
- **Complete code**: No TODOs, ready to run, includes tests

Perfect for learning when and why to use each tool in the LangChain ecosystem.

## 📊 Data Sources

- **SEC EDGAR API** - Free, unlimited company filings (no API key needed)
- **Lending Club Dataset** - Real P2P loan patterns and risk scoring
- **Fraud Detection Datasets** - Transaction patterns and anomaly detection

All examples work standalone with built-in test data.

## 🛠️ Tech Stack

- Python 3.10+
- LangChain 0.1.0+ / LangGraph 0.0.20+
- Anthropic Claude API (for LLM calls)
- SEC EDGAR API (free, no key needed)

## 📝 Prerequisites

```bash
# Python 3.10 or higher
python --version

# Install dependencies
cd langgraph
pip install -r requirements.txt

# Set up your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"
```

## 🎯 What Each Project Demonstrates

### 01-earnings-analyzer
**Pattern**: Iterative investigation with loop-back
```
fetch → extract → compare → detect_anomalies
                                    ↓
                          [anomalies found?]
                                    ↓
                            YES → investigate
                                    ↓
                          [fully explained?]
                                    ↓
                            NO → investigate (LOOP)
                                    ↓
                            YES → generate_report
```

**Key learning**: How to loop back to a node when more investigation is needed

### 02-loan-approval
**Pattern**: Multi-path conditional routing
```
fetch → extract → risk_assessment
                         ↓
                  [risk category?]
                  /      |      \
            low /    medium |   high \
               /            |         \
          approve      analyze      reject
```

**Key learning**: How to route to different nodes based on calculated risk scores

### 03-fraud-detection
**Pattern**: Pattern matching + selective investigation
```
fetch → extract_patterns → [suspicion score?]
                          /      |      \
                    low /   medium |   high \
                       /           |          \
                  approve    investigate    block
```

**Key learning**: Combining fast heuristics with selective deep investigation

## 🤝 Contributing

This is a learning repo, but suggestions welcome! Open an issue or PR.

## 📄 License

MIT

---

**Built while learning the LangChain ecosystem, one workflow at a time.**
