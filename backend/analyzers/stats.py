import pandas as pd
import numpy as np
from scipy.stats import entropy


def _safe_round(val, decimals=2):
    """Convert numpy values to Python float, handle NaN/Inf."""
    if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
        return 0
    try:
        return round(float(val), decimals)
    except (TypeError, ValueError):
        return 0


def generate_numeric_stats(df: pd.DataFrame, col_types: dict) -> dict:
    stats_report = {}
    numeric_cols = [col for col, ctype in col_types.items() if ctype == 'numeric' and col in df.columns]
    
    if not numeric_cols:
        return stats_report
        
    desc = df[numeric_cols].describe()
    
    for col in numeric_cols:
        stats_report[col] = {
            "mean": _safe_round(desc.loc['mean', col]),
            "median": _safe_round(df[col].median()),
            "min": _safe_round(desc.loc['min', col]),
            "max": _safe_round(desc.loc['max', col]),
            "std_dev": _safe_round(desc.loc['std', col]),
            "skewness": _safe_round(df[col].skew())
        }
        
    return stats_report


def generate_categorical_stats(df: pd.DataFrame, col_types: dict) -> dict:
    cat_stats = {}
    cat_cols = [col for col, ctype in col_types.items() if ctype == 'categorical' and col in df.columns]
    
    for col in cat_cols:
        value_counts = df[col].value_counts()
        
        probs = value_counts / len(df[col])
        ent = entropy(probs)
        
        cat_stats[col] = {
            "unique_count": int(df[col].nunique()),
            "top_values": {str(k): int(v) for k, v in value_counts.head(5).items()},
            "entropy": _safe_round(ent)
        }
        
    return cat_stats
