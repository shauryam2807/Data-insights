import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

def generate_associations(df: pd.DataFrame, col_types: dict) -> list:
    """
    Finds association rules (like market basket analysis) among categorical columns.
    """
    cat_cols = [col for col, ctype in col_types.items() if ctype == 'categorical']
    
    if len(cat_cols) < 2:
        return []
        
    df_cat = df[cat_cols].copy()
    for col in cat_cols:
        top_vals = df_cat[col].value_counts().nlargest(10).index
        df_cat[col] = df_cat[col].apply(lambda x: x if x in top_vals else 'Other')
        
    df_encoded = pd.get_dummies(df_cat).astype(bool)
    
    if len(df_encoded.columns) == 0:
        return []
        
    try:
        frequent_itemsets = apriori(df_encoded, min_support=0.05, use_colnames=True)
        
        if frequent_itemsets.empty:
            return []
            
        # Try newer API first, then fall back to older API
        try:
            rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.2, num_items_col="num_items")
        except TypeError:
            try:
                rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.2)
            except Exception:
                return []
        
        if rules.empty:
            return []
            
        rules = rules[rules['confidence'] > 0.5]
        
        results = []
        for _, row in rules.iterrows():
            antecedents = [str(x) for x in list(row['antecedents'])]
            consequents = [str(x) for x in list(row['consequents'])]
            
            results.append({
                "if": antecedents,
                "then": consequents,
                "support": round(float(row['support']), 3),
                "confidence": round(float(row['confidence']), 3),
                "lift": round(float(row['lift']), 2)
            })
            
        results = sorted(results, key=lambda x: x['lift'], reverse=True)
        return results[:20]
        
    except Exception as e:
        print(f"Error in association mining: {e}")
        return []
