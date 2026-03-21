# LangSmith → Grafana Integration - Implementation Guide

**Goal:** Export LangSmith AI metrics to Prometheus, visualize in Grafana alongside infrastructure metrics.

---

## 🎯 What This Achieves

**Unified Dashboard:**
```
┌─────────────────────────────────────────────────┐
│    Grafana: Trading Team API Monitoring         │
├─────────────────────────────────────────────────┤
│ Infrastructure (existing Prometheus)            │
│ • CPU: 45%                                      │
│ • Memory: 2.1GB                                 │
│ • Request Rate: 150/min                         │
├─────────────────────────────────────────────────┤
│ AI Performance (NEW - from LangSmith)           │
│ • Total Cost/hour: $0.47                        │
│ • Avg LLM Latency: 1.2s                         │
│ • Market Agent calls: 45/min                    │
│ • Negotiation success: 94%                      │
└─────────────────────────────────────────────────┘
```

**Why this matters:**
- Correlate infrastructure events with AI behavior
- Track AI costs in real-time
- Alert on expensive operations
- Unified observability stack

---

## 🏗️ Architecture

```
LangSmith (cloud)
    ↓ (Python script queries API every 60s)
Prometheus Exporter (localhost:8001/metrics)
    ↓ (Prometheus scrapes every 60s)
Prometheus (localhost:9090)
    ↓ (Grafana queries PromQL)
Grafana (localhost:3000)
```

---

## 📁 File Structure to Create

```
langgraph/06-observability/
└── grafana-integration/
    ├── README.md                      # This file
    ├── prometheus_exporter.py         # Main exporter daemon
    ├── prometheus.yml.example         # Prometheus config snippet
    ├── grafana_dashboard.json         # Grafana dashboard definition
    ├── prometheus_alerts.yml          # Alert rules
    ├── systemd/
    │   └── langsmith-exporter.service # Systemd service file
    ├── test_exporter.py               # Test script
    └── setup.sh                       # Automated setup script
```

---

## 📝 Implementation Files

### **1. prometheus_exporter.py** (Main Exporter)

**Purpose:** Daemon that polls LangSmith API every 60s, exposes Prometheus metrics at :8001/metrics

**Key metrics exported:**
- `langsmith_total_cost_usd` - Total cost per example
- `langsmith_requests_total` - Request count by example/status
- `langsmith_latency_seconds` - Latency histogram
- `langsmith_llm_calls_total` - LLM calls by model
- `langsmith_tokens_total` - Token usage (input/output)
- `langsmith_agent_calls_total` - Agent-specific calls
- `langsmith_negotiation_rounds` - Trading Team negotiation rounds

**Full implementation:**

```python
"""
LangSmith Prometheus Exporter

Polls LangSmith API every 60s, exposes metrics at http://localhost:8001/metrics
for Prometheus to scrape.

Requirements:
  pip install prometheus-client langsmith

Environment:
  LANGCHAIN_API_KEY=lsv2_pt_...
  LANGCHAIN_PROJECT=langgraph-learning (optional)

Usage:
  python prometheus_exporter.py
"""

from prometheus_client import start_http_server, Gauge, Counter, Histogram
from langsmith import Client
from datetime import datetime, timedelta
import time
import os
import sys

# ============================================================================
# Prometheus Metrics Definitions
# ============================================================================

langsmith_total_cost = Gauge(
    'langsmith_total_cost_usd',
    'Total cost in USD for the run',
    ['project', 'example']
)

langsmith_request_count = Counter(
    'langsmith_requests_total',
    'Total number of LangSmith runs',
    ['project', 'example', 'status']
)

langsmith_latency = Histogram(
    'langsmith_latency_seconds',
    'LangSmith run latency in seconds',
    ['project', 'example'],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, float('inf'))
)

langsmith_llm_calls = Counter(
    'langsmith_llm_calls_total',
    'Total LLM calls made',
    ['project', 'example', 'model']
)

langsmith_tokens = Counter(
    'langsmith_tokens_total',
    'Total tokens used',
    ['project', 'example', 'model', 'type']  # type: input or output
)

langsmith_agent_calls = Counter(
    'langsmith_agent_calls_total',
    'Agent-specific call counts',
    ['project', 'example', 'agent']
)

langsmith_negotiation_rounds = Histogram(
    'langsmith_negotiation_rounds',
    'Number of negotiation rounds (Trading Team)',
    ['project', 'example'],
    buckets=(0, 1, 2, 3, 4, 5, float('inf'))
)

langsmith_errors = Counter(
    'langsmith_errors_total',
    'Total errors encountered',
    ['project', 'example', 'error_type']
)


# ============================================================================
# Exporter Class
# ============================================================================

class LangSmithExporter:
    """
    Polls LangSmith API and updates Prometheus metrics.
    """
    
    def __init__(self, project_name=None, poll_interval=60):
        """
        Args:
            project_name: LangSmith project name (default from env)
            poll_interval: How often to poll LangSmith API (seconds)
        """
        self.client = Client()
        self.project_name = project_name or os.getenv("LANGCHAIN_PROJECT", "default")
        self.poll_interval = poll_interval
        self.last_check = datetime.now() - timedelta(hours=1)
        
    def extract_example_name(self, run_name):
        """
        Extract example name from run name.
        
        "DevOps Agent - Issue 123" -> "DevOps Agent"
        "Trading Team" -> "Trading Team"
        """
        if " - " in run_name:
            return run_name.split(" - ")[0]
        return run_name
    
    def collect_metrics(self):
        """
        Fetch new runs from LangSmith and update Prometheus metrics.
        """
        
        try:
            print(f"⏱️  Polling LangSmith (project: {self.project_name})...")
            
            # Get runs since last check
            runs = list(self.client.list_runs(
                project_name=self.project_name,
                start_time=self.last_check,
                is_root=True  # Only top-level runs, not sub-runs
            ))
            
            if not runs:
                print(f"   No new runs since {self.last_check.strftime('%H:%M:%S')}")
                self.last_check = datetime.now()
                return
            
            print(f"   Found {len(runs)} new runs")
            
            for run in runs:
                example = self.extract_example_name(run.name)
                status = run.status or "unknown"
                
                # Cost
                if run.total_cost:
                    langsmith_total_cost.labels(
                        project=self.project_name,
                        example=example
                    ).set(run.total_cost)
                
                # Request count
                langsmith_request_count.labels(
                    project=self.project_name,
                    example=example,
                    status=status
                ).inc()
                
                # Latency
                if run.total_time:
                    langsmith_latency.labels(
                        project=self.project_name,
                        example=example
                    ).observe(run.total_time)
                
                # Errors
                if run.error:
                    error_type = type(run.error).__name__ if hasattr(run.error, '__name__') else "error"
                    langsmith_errors.labels(
                        project=self.project_name,
                        example=example,
                        error_type=error_type
                    ).inc()
                
                # Get child runs for detailed metrics
                try:
                    child_runs = list(self.client.list_runs(
                        trace_id=run.id,
                        is_root=False
                    ))
                    
                    self._process_child_runs(child_runs, example)
                    
                except Exception as e:
                    print(f"   ⚠️  Error processing child runs: {e}")
                
                # Extract state-specific metrics
                self._extract_state_metrics(run, example)
            
            self.last_check = datetime.now()
            print(f"   ✅ Updated metrics at {self.last_check.strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"   ❌ Error collecting metrics: {e}")
    
    def _process_child_runs(self, child_runs, example):
        """Process child runs to extract LLM and agent metrics."""
        
        for child in child_runs:
            child_name = child.name.lower()
            
            # Detect LLM calls
            if "llm" in child_name or "claude" in child_name or "gpt" in child_name:
                # Try to extract model name
                model = "unknown"
                if child.extra and isinstance(child.extra, dict):
                    metadata = child.extra.get("metadata", {})
                    model = metadata.get("model", "unknown")
                
                langsmith_llm_calls.labels(
                    project=self.project_name,
                    example=example,
                    model=model
                ).inc()
                
                # Estimate tokens (rough approximation: 4 chars per token)
                if child.inputs:
                    input_str = str(child.inputs)
                    input_tokens = len(input_str) // 4
                    langsmith_tokens.labels(
                        project=self.project_name,
                        example=example,
                        model=model,
                        type="input"
                    ).inc(input_tokens)
                
                if child.outputs:
                    output_str = str(child.outputs)
                    output_tokens = len(output_str) // 4
                    langsmith_tokens.labels(
                        project=self.project_name,
                        example=example,
                        model=model,
                        type="output"
                    ).inc(output_tokens)
            
            # Detect agent calls
            if "agent" in child_name:
                # Extract agent name: "market analysis" -> "market"
                agent_name = child_name.split()[0] if " " in child_name else child_name
                
                langsmith_agent_calls.labels(
                    project=self.project_name,
                    example=example,
                    agent=agent_name
                ).inc()
    
    def _extract_state_metrics(self, run, example):
        """Extract metrics from run state (e.g., negotiation rounds)."""
        
        # Trading Team: negotiation rounds
        if "trading" in example.lower():
            if run.outputs and isinstance(run.outputs, dict):
                rounds = run.outputs.get("negotiation_round", 0)
                
                langsmith_negotiation_rounds.labels(
                    project=self.project_name,
                    example=example
                ).observe(rounds)
    
    def run(self):
        """Run the exporter daemon."""
        
        print("=" * 70)
        print("🚀 LangSmith Prometheus Exporter")
        print("=" * 70)
        print(f"Project:        {self.project_name}")
        print(f"Poll Interval:  {self.poll_interval}s")
        print(f"Metrics Port:   8001")
        print(f"Metrics URL:    http://localhost:8001/metrics")
        print("=" * 70)
        print()
        
        # Verify LangSmith connection
        try:
            list(self.client.list_projects(limit=1))
            print("✅ LangSmith connection verified")
        except Exception as e:
            print(f"❌ LangSmith connection failed: {e}")
            print("   Check LANGCHAIN_API_KEY environment variable")
            sys.exit(1)
        
        # Start HTTP server for Prometheus to scrape
        start_http_server(8001)
        print("✅ HTTP server started on port 8001")
        print()
        
        # Main loop
        print("Starting metric collection loop...")
        print()
        
        while True:
            self.collect_metrics()
            time.sleep(self.poll_interval)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Get configuration from environment
    project_name = os.getenv("LANGCHAIN_PROJECT")
    poll_interval = int(os.getenv("POLL_INTERVAL", "60"))
    
    # Create and run exporter
    exporter = LangSmithExporter(
        project_name=project_name,
        poll_interval=poll_interval
    )
    
    try:
        exporter.run()
    except KeyboardInterrupt:
        print("\n\n⏹️  Exporter stopped by user")
        sys.exit(0)
```

---

### **2. test_exporter.py** (Test Script)

**Purpose:** Test that exporter works before deploying

```python
"""
Test the LangSmith Prometheus Exporter.

Usage:
  python test_exporter.py
"""

import requests
import time
import os

def test_exporter():
    """Test that exporter is running and producing metrics."""
    
    print("🧪 Testing LangSmith Prometheus Exporter\n")
    
    # Check environment
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        print("❌ LANGCHAIN_API_KEY not set")
        return False
    
    print("✅ LANGCHAIN_API_KEY is set")
    
    # Check if exporter is running
    try:
        response = requests.get("http://localhost:8001/metrics", timeout=5)
        
        if response.status_code != 200:
            print(f"❌ Exporter returned status {response.status_code}")
            return False
        
        print("✅ Exporter is running on port 8001")
        
        # Check for expected metrics
        metrics_text = response.text
        
        expected_metrics = [
            "langsmith_total_cost_usd",
            "langsmith_requests_total",
            "langsmith_latency_seconds"
        ]
        
        missing = []
        for metric in expected_metrics:
            if metric in metrics_text:
                print(f"✅ Found metric: {metric}")
            else:
                missing.append(metric)
        
        if missing:
            print(f"⚠️  Missing metrics: {', '.join(missing)}")
            print("   (This is OK if no runs have happened yet)")
        
        # Show sample metrics
        print("\n📊 Sample Metrics:\n")
        for line in metrics_text.split('\n')[:20]:
            if line and not line.startswith('#'):
                print(f"   {line}")
        
        print("\n✅ Exporter test passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to exporter on port 8001")
        print("   Make sure prometheus_exporter.py is running")
        return False
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_exporter()
    exit(0 if success else 1)
```

---

### **3. prometheus.yml.example** (Prometheus Config Snippet)

**Purpose:** Show what to add to existing Prometheus config

```yaml
# Add this to your existing prometheus.yml

global:
  scrape_interval: 60s      # Match exporter poll interval
  evaluation_interval: 60s

scrape_configs:
  # Your existing scrapes (keep these)
  - job_name: 'application'
    static_configs:
      - targets: ['localhost:8000']
  
  # NEW: LangSmith exporter
  - job_name: 'langsmith'
    static_configs:
      - targets: ['localhost:8001']
    scrape_interval: 60s      # Poll every 60s
    scrape_timeout: 10s
```

**After adding:**
```bash
# Validate config
promtool check config prometheus.yml

# Reload Prometheus
curl -X POST http://localhost:9090/-/reload

# Or restart
sudo systemctl restart prometheus
```

---

### **4. prometheus_alerts.yml** (Alert Rules)

**Purpose:** Define alerts for AI performance

```yaml
# prometheus_alerts.yml
# Add to your Prometheus alerting rules

groups:
  - name: langsmith_ai_performance
    interval: 60s
    rules:
      # Alert: Daily AI costs exceed $100
      - alert: HighAICostDaily
        expr: sum(increase(langsmith_total_cost_usd[24h])) > 100
        for: 5m
        labels:
          severity: warning
          component: ai
        annotations:
          summary: "AI costs exceeded $100 in last 24h"
          description: "Total LangSmith costs: ${{ $value | humanize }}"
      
      # Alert: Hourly AI costs exceed $10
      - alert: HighAICostHourly
        expr: sum(increase(langsmith_total_cost_usd[1h])) > 10
        for: 5m
        labels:
          severity: info
          component: ai
        annotations:
          summary: "AI costs exceeded $10 in last hour"
          description: "Cost spike detected: ${{ $value | humanize }}/hour"
      
      # Alert: p95 latency > 10 seconds
      - alert: HighAILatency
        expr: histogram_quantile(0.95, rate(langsmith_latency_seconds_bucket[5m])) > 10
        for: 5m
        labels:
          severity: warning
          component: ai
        annotations:
          summary: "AI workflow p95 latency > 10s"
          description: "{{ $labels.example }}: p95 latency is {{ $value | humanize }}s"
      
      # Alert: Error rate > 5%
      - alert: HighAIErrorRate
        expr: |
          sum(rate(langsmith_requests_total{status!="success"}[5m]))
          /
          sum(rate(langsmith_requests_total[5m]))
          > 0.05
        for: 5m
        labels:
          severity: warning
          component: ai
        annotations:
          summary: "AI error rate > 5%"
          description: "Current error rate: {{ $value | humanizePercentage }}"
      
      # Alert: Trading Team negotiations exceeding 2 rounds frequently
      - alert: ExcessiveNegotiations
        expr: histogram_quantile(0.95, rate(langsmith_negotiation_rounds_bucket[10m])) > 2
        for: 10m
        labels:
          severity: info
          component: trading_team
        annotations:
          summary: "Trading Team struggling to find suitable trades"
          description: "p95 negotiation rounds: {{ $value | humanize }}"
      
      # Alert: Specific example has high cost
      - alert: ExpensiveExample
        expr: rate(langsmith_total_cost_usd[1h]) > 5
        for: 10m
        labels:
          severity: info
          component: ai
        annotations:
          summary: "{{ $labels.example }} is expensive"
          description: "{{ $labels.example }} costing ${{ $value | humanize }}/hour"
```

**Load alerts:**
```bash
# Add to prometheus.yml:
rule_files:
  - "prometheus_alerts.yml"

# Reload
curl -X POST http://localhost:9090/-/reload
```

---

### **5. grafana_dashboard.json** (Grafana Dashboard)

**Purpose:** Pre-built dashboard for LangSmith metrics

```json
{
  "dashboard": {
    "title": "LangGraph AI Performance",
    "tags": ["langsmith", "ai", "langgraph"],
    "timezone": "browser",
    "schemaVersion": 16,
    "version": 1,
    "refresh": "30s",
    
    "panels": [
      {
        "id": 1,
        "title": "Total AI Cost (Last 24h)",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "sum(increase(langsmith_total_cost_usd[24h]))",
            "legendFormat": "Total Cost",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "currencyUSD",
            "decimals": 2
          }
        }
      },
      
      {
        "id": 2,
        "title": "Request Rate (req/min)",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0},
        "targets": [
          {
            "expr": "sum(rate(langsmith_requests_total[5m])) * 60",
            "legendFormat": "Requests/min",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "reqpm",
            "decimals": 1
          }
        }
      },
      
      {
        "id": 3,
        "title": "p95 Latency",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0},
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(langsmith_latency_seconds_bucket[5m]))",
            "legendFormat": "p95",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "s",
            "decimals": 2
          }
        }
      },
      
      {
        "id": 4,
        "title": "Success Rate",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0},
        "targets": [
          {
            "expr": "sum(rate(langsmith_requests_total{status=\"success\"}[5m])) / sum(rate(langsmith_requests_total[5m]))",
            "legendFormat": "Success %",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percentunit",
            "decimals": 1,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "red"},
                {"value": 0.9, "color": "yellow"},
                {"value": 0.95, "color": "green"}
              ]
            }
          }
        }
      },
      
      {
        "id": 5,
        "title": "Cost by Example (Last 1h)",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4},
        "targets": [
          {
            "expr": "sum(increase(langsmith_total_cost_usd[1h])) by (example)",
            "legendFormat": "{{example}}",
            "refId": "A"
          }
        ],
        "yaxes": [
          {"format": "currencyUSD", "label": "Cost"},
          {"format": "short"}
        ]
      },
      
      {
        "id": 6,
        "title": "Request Rate by Example",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4},
        "targets": [
          {
            "expr": "sum(rate(langsmith_requests_total[5m])) by (example) * 60",
            "legendFormat": "{{example}}",
            "refId": "A"
          }
        ],
        "yaxes": [
          {"format": "reqpm", "label": "Requests/min"},
          {"format": "short"}
        ]
      },
      
      {
        "id": 7,
        "title": "Latency Distribution by Example",
        "type": "graph",
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 12},
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(langsmith_latency_seconds_bucket[5m])) by (example)",
            "legendFormat": "{{example}} - p50",
            "refId": "A"
          },
          {
            "expr": "histogram_quantile(0.95, rate(langsmith_latency_seconds_bucket[5m])) by (example)",
            "legendFormat": "{{example}} - p95",
            "refId": "B"
          },
          {
            "expr": "histogram_quantile(0.99, rate(langsmith_latency_seconds_bucket[5m])) by (example)",
            "legendFormat": "{{example}} - p99",
            "refId": "C"
          }
        ],
        "yaxes": [
          {"format": "s", "label": "Latency"},
          {"format": "short"}
        ]
      },
      
      {
        "id": 8,
        "title": "LLM Calls by Model",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 20},
        "targets": [
          {
            "expr": "sum(rate(langsmith_llm_calls_total[5m])) by (model) * 60",
            "legendFormat": "{{model}}",
            "refId": "A"
          }
        ],
        "yaxes": [
          {"format": "cpm", "label": "Calls/min"},
          {"format": "short"}
        ]
      },
      
      {
        "id": 9,
        "title": "Agent Activity (Trading Team)",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 20},
        "targets": [
          {
            "expr": "sum(rate(langsmith_agent_calls_total{example=~\".*Trading.*\"}[5m])) by (agent) * 60",
            "legendFormat": "{{agent}}",
            "refId": "A"
          }
        ],
        "yaxes": [
          {"format": "cpm", "label": "Calls/min"},
          {"format": "short"}
        ]
      },
      
      {
        "id": 10,
        "title": "Negotiation Rounds (Trading Team)",
        "type": "graph",
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 28},
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(langsmith_negotiation_rounds_bucket[5m]))",
            "legendFormat": "p50 rounds",
            "refId": "A"
          },
          {
            "expr": "histogram_quantile(0.95, rate(langsmith_negotiation_rounds_bucket[5m]))",
            "legendFormat": "p95 rounds",
            "refId": "B"
          }
        ],
        "yaxes": [
          {"format": "short", "label": "Negotiation Rounds"},
          {"format": "short"}
        ]
      }
    ]
  }
}
```

---

### **6. systemd/langsmith-exporter.service** (Systemd Service)

**Purpose:** Run exporter as a system service (auto-restart, logs)

```ini
[Unit]
Description=LangSmith Prometheus Exporter
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
Group=YOUR_USERNAME
WorkingDirectory=/path/to/langgraph/06-observability/grafana-integration
Environment="LANGCHAIN_API_KEY=lsv2_pt_YOUR_KEY_HERE"
Environment="LANGCHAIN_PROJECT=langgraph-learning"
Environment="POLL_INTERVAL=60"
ExecStart=/usr/bin/python3 prometheus_exporter.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=langsmith-exporter

[Install]
WantedBy=multi-user.target
```

**Install service:**
```bash
# Edit service file with your details
sudo cp systemd/langsmith-exporter.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable langsmith-exporter
sudo systemctl start langsmith-exporter

# Check status
sudo systemctl status langsmith-exporter

# View logs
sudo journalctl -u langsmith-exporter -f
```

---

### **7. setup.sh** (Automated Setup Script)

**Purpose:** One-command setup for the entire integration

```bash
#!/bin/bash

# LangSmith → Grafana Integration Setup Script

set -e  # Exit on error

echo "============================================================"
echo "🚀 LangSmith → Grafana Integration Setup"
echo "============================================================"
echo ""

# Check environment
if [ -z "$LANGCHAIN_API_KEY" ]; then
    echo "❌ LANGCHAIN_API_KEY not set"
    echo "   Get key from: https://smith.langchain.com/settings"
    echo "   Then run: export LANGCHAIN_API_KEY='lsv2_pt_...'"
    exit 1
fi

echo "✅ LANGCHAIN_API_KEY is set"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install prometheus-client langsmith requests

# Test LangSmith connection
echo ""
echo "🔍 Testing LangSmith connection..."
python -c "from langsmith import Client; Client().list_projects(limit=1); print('✅ Connection successful')"

# Create systemd service
echo ""
echo "⚙️  Setting up systemd service..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_FILE="/etc/systemd/system/langsmith-exporter.service"

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=LangSmith Prometheus Exporter
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment="LANGCHAIN_API_KEY=$LANGCHAIN_API_KEY"
Environment="LANGCHAIN_PROJECT=${LANGCHAIN_PROJECT:-langgraph-learning}"
Environment="POLL_INTERVAL=60"
ExecStart=/usr/bin/python3 $SCRIPT_DIR/prometheus_exporter.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=langsmith-exporter

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable langsmith-exporter
sudo systemctl start langsmith-exporter

echo "✅ Service started"

# Wait for exporter to start
echo ""
echo "⏳ Waiting for exporter to start..."
sleep 3

# Test metrics endpoint
echo ""
echo "🧪 Testing metrics endpoint..."
if curl -s http://localhost:8001/metrics | head -5 > /dev/null; then
    echo "✅ Metrics endpoint working"
else
    echo "❌ Metrics endpoint not responding"
    echo "   Check logs: sudo journalctl -u langsmith-exporter -f"
    exit 1
fi

# Print next steps
echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "Next Steps:"
echo ""
echo "1. Add to Prometheus config (prometheus.yml):"
echo "   - job_name: 'langsmith'"
echo "     static_configs:"
echo "       - targets: ['localhost:8001']"
echo ""
echo "2. Reload Prometheus:"
echo "   curl -X POST http://localhost:9090/-/reload"
echo ""
echo "3. Import Grafana dashboard:"
echo "   Grafana → Import → Upload grafana_dashboard.json"
echo ""
echo "4. View metrics:"
echo "   http://localhost:8001/metrics"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u langsmith-exporter -f"
echo ""
echo "============================================================"
```

**Make executable:**
```bash
chmod +x setup.sh
```

---

## 🚀 Setup Instructions

### **Quick Start (Automated):**

```bash
cd langgraph/06-observability/grafana-integration

# Set API key
export LANGCHAIN_API_KEY="lsv2_pt_..."

# Run setup script
./setup.sh
```

### **Manual Setup:**

```bash
# 1. Install dependencies
pip install prometheus-client langsmith requests

# 2. Test exporter
python prometheus_exporter.py
# (In another terminal) curl http://localhost:8001/metrics

# 3. Configure Prometheus
# Add snippet from prometheus.yml.example to your prometheus.yml
curl -X POST http://localhost:9090/-/reload

# 4. Import Grafana dashboard
# Upload grafana_dashboard.json via Grafana UI

# 5. (Optional) Install as service
sudo cp systemd/langsmith-exporter.service /etc/systemd/system/
sudo systemctl enable langsmith-exporter
sudo systemctl start langsmith-exporter
```

---

## ✅ Verification Checklist

After setup, verify each component:

- [ ] **Exporter running**
  ```bash
  curl http://localhost:8001/metrics | head -20
  # Should show: langsmith_total_cost_usd, langsmith_requests_total, etc.
  ```

- [ ] **Prometheus scraping**
  ```bash
  # Go to: http://localhost:9090/targets
  # Check: 'langsmith' target shows "UP" (green)
  ```

- [ ] **Metrics in Prometheus**
  ```bash
  # Go to: http://localhost:9090/graph
  # Query: langsmith_requests_total
  # Should show data
  ```

- [ ] **Grafana dashboard**
  ```bash
  # Go to: http://localhost:3000
  # Import grafana_dashboard.json
  # Should show graphs with data
  ```

- [ ] **Alerts configured**
  ```bash
  # Go to: http://localhost:9090/alerts
  # Should show: HighAICostDaily, HighAILatency, etc.
  ```

---

## 📊 Example Queries (PromQL)

**Total cost in last 24 hours:**
```promql
sum(increase(langsmith_total_cost_usd[24h]))
```

**Request rate by example:**
```promql
sum(rate(langsmith_requests_total[5m])) by (example) * 60
```

**p95 latency:**
```promql
histogram_quantile(0.95, rate(langsmith_latency_seconds_bucket[5m]))
```

**Error rate:**
```promql
sum(rate(langsmith_requests_total{status!="success"}[5m]))
/
sum(rate(langsmith_requests_total[5m]))
```

**Most expensive example (last hour):**
```promql
topk(3, sum(increase(langsmith_total_cost_usd[1h])) by (example))
```

**Agent activity (Trading Team):**
```promql
sum(rate(langsmith_agent_calls_total{example=~".*Trading.*"}[5m])) by (agent)
```

---

## 🐛 Troubleshooting

### **Problem: Exporter not starting**

```bash
# Check logs
sudo journalctl -u langsmith-exporter -n 50

# Common issues:
# 1. LANGCHAIN_API_KEY not set
export LANGCHAIN_API_KEY="lsv2_pt_..."

# 2. Port 8001 already in use
sudo lsof -i :8001
# Kill process or change port in exporter
```

### **Problem: No metrics in Prometheus**

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq

# Verify exporter is exposing metrics
curl http://localhost:8001/metrics

# Check Prometheus config
promtool check config prometheus.yml

# Reload Prometheus
curl -X POST http://localhost:9090/-/reload
```

### **Problem: Grafana shows "No Data"**

```bash
# Check data source
# Grafana → Configuration → Data Sources → Prometheus
# Test connection

# Run a query in Prometheus first
# http://localhost:9090/graph
# Query: langsmith_requests_total
# If it works there, it should work in Grafana
```

---

## 🎯 Key Metrics to Track

| Metric | Description | Alert Threshold |
|--------|-------------|----------------|
| `langsmith_total_cost_usd` | Cost per run | > $100/day |
| `langsmith_latency_seconds` | Run latency | p95 > 10s |
| `langsmith_requests_total` | Request count | Error rate > 5% |
| `langsmith_llm_calls_total` | LLM calls | Sudden spike |
| `langsmith_negotiation_rounds` | Trading negotiations | p95 > 2 rounds |
| `langsmith_agent_calls_total` | Agent activity | Imbalanced activity |

---

## 📝 Notes for Claude Code

**Implementation order:**
1. Create all files in `grafana-integration/` directory
2. Test `prometheus_exporter.py` standalone first
3. Test with `test_exporter.py`
4. Update Prometheus config
5. Import Grafana dashboard
6. Set up systemd service (optional)
7. Configure alerts

**Testing without LangSmith data:**
- The exporter will run but show no metrics initially
- Run a LangGraph example (e.g., DevOps Agent)
- Within 60s, metrics should appear

**Dependencies:**
- Requires existing Prometheus/Grafana setup
- Requires LangSmith API key
- Python 3.8+

---

**Ready to implement!** 🚀