import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def generate_segments(df: pd.DataFrame, col_types: dict) -> list:
    """
    Automatically segments the data using K-Means clustering.
    """
    numeric_cols = [col for col, ctype in col_types.items() if ctype == 'numeric']
    
    if len(numeric_cols) < 2:
        return []
        
    df_num = df[numeric_cols].dropna()
    
    if len(df_num) < 100:
        return []
        
    try:
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_num)
        
        n_clusters = min(3, len(df_num))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(scaled_data)
        
        df_clustered = df_num.copy()
        df_clustered['Cluster'] = clusters
        
        results = []
        for i in range(n_clusters):
            cluster_data = df_clustered[df_clustered['Cluster'] == i]
            
            if len(cluster_data) == 0:
                continue
                
            summary = {}
            for col in numeric_cols:
                summary[col] = round(float(cluster_data[col].mean()), 2)
                
            results.append({
                "cluster_id": int(i),
                "size": int(len(cluster_data)),
                "percentage": round(float(len(cluster_data) / len(df_num) * 100), 1),
                "average_values": summary
            })
            
        return results
        
    except Exception as e:
        print(f"Error in segmentation: {e}")
        return []
