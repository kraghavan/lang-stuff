# 🔍 Observability & Debugging (LangSmith + Grafana)

Production monitoring and debugging for your LangGraph workflows. **No new workflows** — we instrument the examples you already built, then export metrics to Grafana.

## 🎯 Why You Need This

Your Prometheus/Grafana stack tells you *something is slow*. LangSmith tells you **why**:

```
Prometheus: "API p95 = 12.4s ❌"        ← What you know
LangSmith:  "compliance_agent calling    ← Why
             same LLM 4x with identical
             input (bug on line 156)"
```

| Need | Prometheus/Grafana | LangSmith |
|------|-------------------|-----------|
| CPU, memory, network | ✅ | ❌ |
| See LLM prompts/responses | ❌ | ✅ |
| Trace agent decisions | ❌ | ✅ |
| Debug infinite loops | ❌ | ✅ |
| Track AI costs ($) | ❌ | ✅ |
| Token usage | ❌ | ✅ |
| Evaluate accuracy | ❌ | ✅ |
| Unified dashboard | ✅ | ❌ → ✅ (via exporter) |

**You need BOTH** — Prometheus for infrastructure, LangSmith for AI. The Grafana integration bridges them into a single dashboard.

## 📁 Files

```
06-observability/
├── README.md                              # This file
├── requirements.txt                       # langsmith dependency
├── trace_helper.py                        # Terminal-based trace viewer
│
├── 01-setup/                              # Configure LangSmith
│   ├── README.md
│   └── test_connection.py
│
├── 02-trace-devops-agent/                 # Trace tool-calling loops
│   ├── README.md
│   └── add_tracing.py
│
├── 03-monitor-trading-team/               # Trace multi-agent negotiations
│   ├── README.md
│   └── add_tracing.py
│
├── 04-evaluate-fraud/                     # Test accuracy on 20 transactions
│   ├── README.md
│   └── run_evaluation.py
│
├── 05-production-monitoring/              # Cost & latency reports
│   ├── README.md
│   └── cost_tracker.py
│
└── grafana-integration/                   # LangSmith → Prometheus → Grafana
    ├── README.md
    ├── prometheus_exporter.py             # Daemon: polls LangSmith, serves /metrics
    ├── test_exporter.py                   # Verify exporter works
    ├── docker-compose.yml                 # One-command: exporter + Prometheus + Grafana
    ├── Dockerfile                         # Exporter container image
    ├── prometheus-docker.yml              # Prometheus config (Docker)
    ├── prometheus.yml.example             # Prometheus config (manual setup)
    ├── prometheus_alerts.yml              # Alert rules (cost, latency, errors)
    ├── grafana_dashboard.json             # Pre-built 10-panel dashboard
    ├── grafana-provisioning/
    │   └── datasources/prometheus.yml     # Auto-configure Grafana → Prometheus
    └── systemd/
        └── langsmith-exporter.service     # Run as Linux service (non-Docker)
```

## 🚀 Quick Start

### Step 1: Get LangSmith API Key (free)

```bash
# Go to https://smith.langchain.com → Settings → API Keys
# Free tier: 5,000 traces/month
```

### Step 2: Set Environment Variables

```bash
export LANGCHAIN_API_KEY="lsv2_pt_..."
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_PROJECT="langgraph-learning"
```

### Step 3: Test Connection

```bash
cd 01-setup
pip install langsmith
python test_connection.py
```

### Step 4: Run Traced Examples

```bash
# Trace the DevOps Agent
cd ../02-trace-devops-agent
python add_tracing.py

# Trace the Trading Team
cd ../03-monitor-trading-team
python add_tracing.py

# Evaluate Fraud Detection accuracy (no LangSmith key needed)
cd ../04-evaluate-fraud
python run_evaluation.py

# View cost report (needs LangSmith key + traces)
cd ../05-production-monitoring
python cost_tracker.py
```

### Step 5: Grafana Dashboard (Optional)

```bash
# One command spins up exporter + Prometheus + Grafana
cd ../grafana-integration
export LANGCHAIN_API_KEY="lsv2_pt_..."
docker compose up -d

# Access:
#   Grafana:    http://localhost:3000 (admin/admin)
#   Prometheus: http://localhost:9090
#   Exporter:   http://localhost:8001/metrics

# Import dashboard: Grafana → Dashboards → Import → Upload grafana_dashboard.json
```

---

## 📖 What Each Section Does

### 01 — Setup (10 min)
Configure LangSmith, verify API connection. No AI calls needed.

### 02 — Trace DevOps Agent (30 min)
See the full ReAct loop — every LLM decision, tool call, timing, and cost. Debug tool-calling issues like infinite loops or wrong tool selection.

### 03 — Monitor Trading Team (30 min)
See multi-agent negotiations — which agent blocked, what alternatives were tried, cost per agent. Find bottlenecks in the supervisor loop.

### 04 — Evaluate Fraud Detection (45 min)
Test accuracy on 20 transactions (10 legit, 10 fraud). Find false positives and false negatives. **No LangSmith key needed** — runs entirely offline.

### 05 — Production Monitoring (30 min)
Query LangSmith for cost and latency data across all examples. Export to CSV. Requires traces from running examples 02-03.

### Grafana Integration (30 min)
Bridge LangSmith into your existing Prometheus/Grafana stack. A Prometheus exporter polls LangSmith every 60s and serves `/metrics`. Docker Compose spins up the full stack in one command. Includes a pre-built 10-panel dashboard and alert rules.

---

## 🛠️ Terminal Trace Viewer

Don't want to open the web UI? Use `trace_helper.py`:

```bash
python trace_helper.py           # View latest trace
python trace_helper.py list 5    # List last 5 traces
python trace_helper.py export    # Export to JSON
```

---

## 🏗️ Architecture: The Full Stack

```
┌─────────────────────────────────────┐
│     LangGraph Applications          │
│  DevOps Agent, Trading Team, etc.   │
└──────────────┬──────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌────────────┐   ┌─────────────┐
│ LangSmith  │   │ Prometheus/ │
│  (cloud)   │   │ Grafana     │
└─────┬──────┘   └──────▲──────┘
      │                  │
      ▼                  │
┌────────────┐           │
│ Prometheus │───────────┘
│ Exporter   │  (bridges LangSmith → Prometheus)
│ :8001      │
└────────────┘
```

**Together they give you:**
- **LangSmith** — Deep AI traces (prompts, agent decisions, tool calls)
- **Prometheus** — Metrics storage and alerting
- **Grafana** — Unified dashboards (AI + infrastructure side by side)

---

## ✅ Completion Checklist

- [ ] LangSmith API key configured (`01-setup`)
- [ ] Traced the DevOps Agent and saw tool calls (`02`)
- [ ] Traced the Trading Team and saw negotiation rounds (`03`)
- [ ] Ran fraud evaluation and saw accuracy metrics (`04`)
- [ ] Viewed cost report (`05`)
- [ ] Used `trace_helper.py` to view traces from terminal
- [ ] (Optional) Launched Grafana stack with `docker compose up -d`
- [ ] (Optional) Imported `grafana_dashboard.json` and saw metrics

## 📚 Resources

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangSmith Free Tier](https://smith.langchain.com)
- [LangGraph + LangSmith](https://langchain-ai.github.io/langgraph/how-tos/monitoring/)
- [Prometheus Client Python](https://github.com/prometheus/client_python)
- [Grafana Dashboard Import](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/import-dashboards/)
