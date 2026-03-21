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
