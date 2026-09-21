import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def generate_anomalies(df: pd.DataFrame, col_types: dict) -> list:
    """
    Uses Isolation Forest to detect anomalous rows based on numeric features.
    """
    numeric_cols = [col for col, ctype in col_types.items() if ctype == 'numeric']
    
    if len(numeric_cols) < 1:
        return []
        
    df_num = df[numeric_cols].fillna(df[numeric_cols].median())
    
    if len(df_num) < 50:
        return []
        
    try:
        iso = IsolationForest(contamination=0.01, random_state=42)
        preds = iso.fit_predict(df_num)
        
        anomaly_mask = preds == -1
        anomaly_indices = df_num.index[anomaly_mask].tolist()
        
        results = []
        for idx in anomaly_indices:
            row = df_num.loc[idx]
            reasons = []
            for col in numeric_cols:
                median_val = df_num[col].median()
                std_val = df_num[col].std()
                if std_val > 0 and abs(row[col] - median_val) > 2.5 * std_val:
                    reasons.append(f"{col} is {round(float(row[col]), 2)} (median is {round(float(median_val), 2)})")
                    
            if reasons:
                # Convert all values to plain Python types for JSON
                data_dict = {}
                for col in numeric_cols:
                    val = row[col]
                    data_dict[col] = round(float(val), 2) if not pd.isna(val) else None
                    
                results.append({
                    "row_index": int(idx),
                    "reasons": reasons,
                    "data": data_dict
                })
                
        return results
        
    except Exception as e:
        print(f"Error in anomaly detection: {e}")
        return []
