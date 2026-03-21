# 📊 LangSmith → Grafana Integration

Export LangSmith AI metrics to Prometheus and visualize in Grafana alongside your infrastructure metrics.

## What You Get

A unified Grafana dashboard showing AI performance next to infrastructure health:

```
┌─────────────────────────────────────────────────┐
│    Grafana: LangGraph AI Performance            │
├─────────────────────────────────────────────────┤
│ Cost: $0.47/hr    Requests: 150/min             │
│ p95 Latency: 3.2s Success Rate: 97%            │
├─────────────────────────────────────────────────┤
│ Cost by Example ▁▂▃▅▇ (Trading Team highest)   │
│ Latency p50/p95/p99 ─── ─── ───                │
│ LLM Calls by Model ▓▓▓ claude-sonnet           │
│ Agent Activity ▓▓▓ market ▓▓ risk ▓ compliance │
│ Negotiation Rounds ▁▂▃ (p95: 1.5 rounds)       │
└─────────────────────────────────────────────────┘
```

## Architecture

```
LangSmith (cloud)
    ↓ (exporter polls API every 60s)
Prometheus Exporter (localhost:8001/metrics)
    ↓ (Prometheus scrapes every 60s)
Prometheus (localhost:9090)
    ↓ (Grafana queries PromQL)
Grafana (localhost:3000)
```

## 📁 Files

```
grafana-integration/
├── README.md                          # This file
├── prometheus_exporter.py             # Main exporter daemon
├── test_exporter.py                   # Verify exporter works
├── prometheus.yml.example             # Prometheus config (manual setup)
├── prometheus-docker.yml              # Prometheus config (Docker setup)
├── prometheus_alerts.yml              # Alert rules
├── grafana_dashboard.json             # Pre-built Grafana dashboard (10 panels)
├── Dockerfile                         # Exporter container
├── docker-compose.yml                 # Full stack: exporter + Prometheus + Grafana
├── grafana-provisioning/
│   └── datasources/prometheus.yml     # Auto-configure Grafana → Prometheus
└── systemd/
    └── langsmith-exporter.service     # Run as system service (non-Docker)
```

## Prerequisites

- **Docker Desktop** installed and running ([Install Docker](https://docs.docker.com/get-docker/))
- **LANGCHAIN_API_KEY** from [smith.langchain.com](https://smith.langchain.com) (free tier)
- Some LangSmith traces to visualize (run examples 02-05 with `LANGCHAIN_TRACING_V2=true` first)

## 🚀 Quick Start (Docker — Recommended)

One command spins up everything:

```bash
cd langgraph/06-observability/grafana-integration

# Set your LangSmith API key
export LANGCHAIN_API_KEY="lsv2_pt_..."

# Start the stack
docker compose up -d

# Access:
#   Grafana:    http://localhost:3000 (admin/admin)
#   Prometheus: http://localhost:9090
#   Exporter:   http://localhost:8001/metrics
```

Then import the dashboard:
1. Go to `http://localhost:3000`
2. Dashboards → Import → Upload `grafana_dashboard.json`
3. Select "Prometheus" as the data source

To stop:
```bash
docker compose down
```

## 🔧 Manual Setup (Without Docker)

If you already have Prometheus/Grafana running:

```bash
# 1. Install dependencies
pip install prometheus-client langsmith

# 2. Start the exporter
python prometheus_exporter.py
# Metrics at: http://localhost:8001/metrics

# 3. Add to your prometheus.yml (see prometheus.yml.example)
# 4. Reload Prometheus: curl -X POST http://localhost:9090/-/reload
# 5. Import grafana_dashboard.json in Grafana
```

## 📈 Metrics Exported

| Metric | Type | Description |
|--------|------|-------------|
| `langsmith_run_cost_usd` | Counter | Cumulative cost by example |
| `langsmith_requests_total` | Counter | Request count by example/status |
| `langsmith_latency_seconds` | Histogram | Latency distribution (p50/p95/p99) |
| `langsmith_llm_calls_total` | Counter | LLM calls by model |
| `langsmith_tokens_total` | Counter | Token usage (input/output) |
| `langsmith_agent_calls_total` | Counter | Agent-specific call counts |
| `langsmith_negotiation_rounds` | Histogram | Trading Team negotiation rounds |
| `langsmith_errors_total` | Counter | Error count by example |

## 🚨 Alerts

Pre-configured in `prometheus_alerts.yml`:

| Alert | Condition |
|-------|-----------|
| HighAICostDaily | Total cost > $100 |
| HighAILatency | p95 > 10s |
| HighAIErrorRate | Error rate > 5% |
| ExcessiveNegotiations | p95 negotiation rounds > 2 |

## 🧪 Testing

```bash
# Start exporter
python prometheus_exporter.py &

# Run a LangGraph example to generate traces
cd ../../05-trading-team && python main.py "Should we buy UNH?"

# Wait 60s for the exporter to poll, then test
cd ../06-observability/grafana-integration
python test_exporter.py
```

## Useful PromQL Queries

```promql
# Total cost
sum(langsmith_run_cost_usd)

# Request rate by example
sum(rate(langsmith_requests_total[5m])) by (example) * 60

# p95 latency
histogram_quantile(0.95, rate(langsmith_latency_seconds_bucket[5m]))

# Error rate
sum(rate(langsmith_requests_total{status!="success"}[5m]))
/ sum(rate(langsmith_requests_total[5m]))

# Most expensive example
topk(3, sum(langsmith_run_cost_usd) by (example))
```
