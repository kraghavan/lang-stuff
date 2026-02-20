#!/bin/bash

# Script to set up lang-stuff repository structure
echo "🚀 Setting up lang-stuff repository structure..."

# Create main directories
mkdir -p langgraph/01-earnings-analyzer/{examples,data}
mkdir -p langgraph/02-loan-approval/data
mkdir -p langgraph/03-fraud-detection/data
mkdir -p langchain
mkdir -p langsmith
mkdir -p langflow
mkdir -p shared

echo "📁 Creating directory structure..."

# Create placeholder READMEs for future sections
cat > langchain/README.md << 'EOF'
# LangChain Examples

Simple chains and basic patterns.

**Status**: 📋 Coming Soon

This section will contain examples of:
- Basic prompt chains
- Sequential workflows
- Simple RAG applications
- When to use LangChain vs LangGraph

Check back soon!
EOF

cat > langsmith/README.md << 'EOF'
# LangSmith Examples

Observability, debugging, and testing workflows.

**Status**: 📋 Coming Soon

This section will contain examples of:
- Tracing workflows
- Debugging LangGraph applications
- A/B testing prompts
- Performance monitoring

Check back soon!
EOF

cat > langflow/README.md << 'EOF'
# LangFlow Examples

Visual workflow prototyping and rapid development.

**Status**: 📋 Coming Soon

This section will contain examples of:
- Visual workflow builders
- Drag-and-drop prototyping
- Converting LangFlow to code
- Quick experimentation patterns

Check back soon!
EOF

# Create shared utilities placeholder
cat > shared/utils.py << 'EOF'
"""
Shared utility functions across all lang-stuff examples.
"""

def format_currency(amount: float) -> str:
    """Format a number as USD currency."""
    return f"${amount:,.2f}"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values."""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
EOF

cat > shared/data_loaders.py << 'EOF'
"""
Common data loading utilities.
"""

import pandas as pd
from typing import Optional


def load_csv_safely(filepath: str, **kwargs) -> Optional[pd.DataFrame]:
    """
    Safely load a CSV file with error handling.
    
    Args:
        filepath: Path to CSV file
        **kwargs: Additional arguments to pass to pd.read_csv
        
    Returns:
        DataFrame if successful, None if error
    """
    try:
        df = pd.read_csv(filepath, **kwargs)
        print(f"✅ Loaded {len(df)} rows from {filepath}")
        return df
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return None
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return None
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Environment variables
.env
.env.local
*.env

# Data files (large datasets)
*.csv
*.xlsx
*.json
*.parquet
!**/sample*.csv
!**/example*.csv

# OS
.DS_Store
Thumbs.db

# LangSmith
.langsmith/

# Logs
*.log
logs/

# Temporary files
tmp/
temp/
EOF

# Create placeholder data files
cat > langgraph/02-loan-approval/data/README.md << 'EOF'
# Loan Approval Data

Download the Lending Club dataset from Kaggle:
https://www.kaggle.com/datasets/wordsforthewise/lending-club

Place `accepted_2007_to_2018.csv` in this directory.

Alternatively, use the sample data provided in the example scripts.
EOF

cat > langgraph/03-fraud-detection/data/README.md << 'EOF'
# Fraud Detection Data

Download fraud detection datasets from Kaggle:
- https://www.kaggle.com/datasets/nelgiriyewithana/credit-card-fraud-detection-dataset-2023
- https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

Place the CSV files in this directory.

Alternatively, use the synthetic data generator included in the example scripts.
EOF

echo "✅ Directory structure created!"
echo ""
echo "📋 Next steps:"
echo "1. Run this script in your lang-stuff repo root: bash setup_repo.sh"
echo "2. Review the created structure"
echo "3. Start building in langgraph/01-earnings-analyzer/"
echo ""
echo "🎯 Structure created:"
tree -L 3 -I '__pycache__|*.pyc' 2>/dev/null || find . -type d | sed 's|[^/]*/| |g'
