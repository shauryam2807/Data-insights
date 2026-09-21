import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def generate_correlations(df: pd.DataFrame, col_types: dict) -> list:
    """
    Calculates Pearson correlation matrix for numeric columns and returns
    significant correlations with p-values.
    """
    numeric_cols = [col for col, ctype in col_types.items() if ctype == 'numeric']
    
    if len(numeric_cols) < 2:
        return []
        
    df_num = df[numeric_cols].dropna()
    if len(df_num) < 5: # Need enough data
        return []

    correlations = []
    
    # Iterate through combinations
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            col1 = numeric_cols[i]
            col2 = numeric_cols[j]
            
            # Check if columns have zero variance
            if df_num[col1].nunique() <= 1 or df_num[col2].nunique() <= 1:
                continue
                
            corr, p_value = pearsonr(df_num[col1], df_num[col2])
            
            # Only keep somewhat strong or significant correlations
            if p_value < 0.05 and abs(corr) > 0.3:
                correlations.append({
                    "col1": col1,
                    "col2": col2,
                    "correlation": round(corr, 2),
                    "p_value": round(p_value, 4),
                    "strength": "strong" if abs(corr) > 0.7 else "moderate",
                    "direction": "positive" if corr > 0 else "negative"
                })
                
    # Sort by strongest correlation
    correlations = sorted(correlations, key=lambda x: abs(x['correlation']), reverse=True)
    return correlations
