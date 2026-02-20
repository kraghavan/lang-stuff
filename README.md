# lang-stuff

Hands-on explorations of the LangChain ecosystem through real-world financial applications.

## 🎯 What's Inside

A learning journey through LangChain's toolkit, starting with complex agentic workflows and expanding to cover chains, observability, and visual prototyping.

### Current Focus: LangGraph (Agentic Workflows)
- **📊 Earnings Analyzer** - Iterative SEC filing investigation with adaptive deep-dives
- **💰 Loan Approval** - Multi-stage decision pipeline with conditional routing
- **🚨 Fraud Detection** - Risk-adaptive investigation system

### Coming Soon
- **LangChain** - Simple chains and basic patterns
- **LangSmith** - Debugging, testing, and observability
- **LangFlow** - Visual workflow prototyping

## 🧭 The Ecosystem

| Tool | Purpose | Analogy | Status |
|------|---------|---------|--------|
| **LangChain** | Build applications/chains | The scriptwriter (sets up steps) | 📋 Planned |
| **LangGraph** | Orchestrate complex agentic flows | The director (handles loops & branches) | ✅ Active |
| **LangSmith** | Observe, debug, and test | The editor (reviews and improves) | 📋 Planned |
| **LangFlow** | Visual drag-and-drop IDE | The sandbox (rapid prototyping) | 📋 Planned |

## 🚀 Quick Start

```bash
# Clone the repo
git clone git@github.com:kraghavan/lang-stuff.git
cd lang-stuff

# Set up the directory structure (first time only)
bash setup_repo.sh

# Start with LangGraph examples
cd langgraph/01-earnings-analyzer
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Run the simple version
python simple_version.py
```

## 📂 Repository Structure

```
lang-stuff/
├── langgraph/          # Complex multi-agent workflows (✅ Current)
│   ├── 01-earnings-analyzer/
│   ├── 02-loan-approval/
│   └── 03-fraud-detection/
├── langchain/          # Simple chains and basic patterns (📋 Coming)
├── langsmith/          # Debugging and observability (📋 Coming)  
├── langflow/           # Visual workflow prototypes (📋 Coming)
└── shared/             # Common utilities across all examples
```

## 🎓 Learning Path

### Phase 1: Master LangGraph ✅ (You are here)
Start with agentic workflows to understand when you need more than simple chains.

1. **Earnings Analyzer** → Learn iterative investigation and state management
2. **Loan Approval** → Learn multi-stage gates and conditional routing
3. **Fraud Detection** → Learn adaptive depth and risk-based decisions

### Phase 2: Learn LangChain 📋
After understanding complex graphs, appreciate when simple chains are enough.

### Phase 3: Add Observability 📋  
Use LangSmith to debug and improve your workflows.

### Phase 4: Rapid Prototyping 📋
Use LangFlow to visualize and test ideas quickly.

## 💡 Why This Repo

Most tutorials show toy examples. This repo uses:
- **Real data**: SEC filings (18M+ documents), Lending Club (2.2M+ loans), fraud datasets
- **Real problems**: Financial analysis, credit decisions, fraud prevention
- **Real patterns**: State management, conditional routing, human-in-the-loop

Perfect for learning when and why to use each tool in the LangChain ecosystem.

## 📊 Data Sources

- **SEC EDGAR API** - Free, unlimited company filings (no API key needed)
- **Lending Club Dataset** - Real P2P loan data from Kaggle
- **Fraud Detection Datasets** - Anonymized transaction data from Kaggle

All examples include instructions for accessing data.

## 🛠️ Tech Stack

- Python 3.10+
- LangChain / LangGraph
- Anthropic Claude API (for LLM calls)
- Pandas (data processing)
- SEC EDGAR API (free, no key needed)

## 📝 Prerequisites

```bash
# Python 3.10 or higher
python --version

# Install dependencies for each example
pip install -r requirements.txt

# Set up your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"
```

## 🤝 Contributing

This is a learning repo, but suggestions welcome! Open an issue or PR.

## 📄 License

MIT

---

**Built while learning the LangChain ecosystem, one workflow at a time.**

