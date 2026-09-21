def generate_plain_english_insights(correlations, associations, anomalies, segments, 
                                     num_stats=None, cat_stats=None, health_report=None,
                                     col_types=None, column_names=None) -> list:
    """
    Takes raw mathematical outputs from analyzers and translates them into
    plain English, ranked insights for non-technical stakeholders.
    """
    insights = []
    
    # =============================================
    # ABOUT THIS DATA (What is this dataset about?)
    # =============================================
    if column_names and col_types:
        num_count = sum(1 for v in col_types.values() if v == 'numeric')
        cat_count = sum(1 for v in col_types.values() if v == 'categorical')
        rows = health_report.get('rows_after', 0) if health_report else 0
        
        col_list = ', '.join(column_names[:8])
        if len(column_names) > 8:
            col_list += f' and {len(column_names) - 8} more'
        
        text = f"This dataset contains {rows} records with {len(column_names)} columns: {col_list}. "
        text += f"It has {num_count} numeric and {cat_count} text/category columns."
        
        insights.append({
            "type": "About",
            "text": text,
            "confidence_score": 100,
            "badge": "About This Data",
            "details": f"Column types detected automatically: {num_count} numeric, {cat_count} categorical"
        })

    # =============================================
    # DATA CLEANING SUMMARY (Tell user what was removed)
    # =============================================
    if health_report:
        rows_before = health_report.get('rows_before', 0)
        rows_after = health_report.get('rows_after', 0)
        null_removed = health_report.get('null_rows_removed', 0)
        dupes = health_report.get('duplicates_found', 0)
        
        if null_removed > 0 or dupes > 0:
            parts = []
            if dupes > 0:
                parts.append(f"{dupes} duplicate rows")
            if null_removed > 0:
                parts.append(f"{null_removed} rows with missing/null values")
            
            removed_text = " and ".join(parts)
            text = f"Data Cleaning: We removed {removed_text} from your original {rows_before} rows. All insights below are based on the remaining {rows_after} clean rows ({round(rows_after/rows_before*100, 1)}% of original data)."
            
            insights.append({
                "type": "Data Cleaning",
                "text": text,
                "confidence_score": 100,
                "badge": "Cleaned Data",
                "details": f"Original: {rows_before} rows → After cleaning: {rows_after} rows"
            })

    # =============================================
    # 0. Basic Number Insights (Sabse Pehle Yeh Dikhao)
    # =============================================
    if num_stats:
        for col, stats in num_stats.items():
            # A. Average kya hai
            insights.append({
                "type": "Summary",
                "text": f"The average '{col}' is {stats['mean']}. Values range from {stats['min']} (lowest) to {stats['max']} (highest).",
                "confidence_score": 100,
                "badge": "Key Metric",
                "details": f"Median: {stats['median']}, Std Dev: {stats['std_dev']}"
            })
            
            # B. Skewness check — kya data ek side jhuka hai?
            skew = stats.get('skewness', 0)
            if abs(skew) > 1:
                if skew > 0:
                    skew_text = f"Most '{col}' values are on the lower side, but a few extremely high values are pulling the average up. The typical (median) value of {stats['median']} might be more reliable than the average of {stats['mean']}."
                else:
                    skew_text = f"Most '{col}' values are on the higher side, but a few very low values exist. The typical (median) value of {stats['median']} might be more reliable than the average of {stats['mean']}."
                
                insights.append({
                    "type": "Data Quality",
                    "text": skew_text,
                    "confidence_score": 85,
                    "badge": "Worth Noting",
                    "details": f"Skewness: {skew} (values beyond ±1 indicate significant skew)"
                })
    
    # =============================================
    # 1. Category Insights (Text columns ke baare mein)
    # =============================================
    if cat_stats:
        for col, stats in cat_stats.items():
            top_values = stats.get('top_values', {})
            unique = stats.get('unique_count', 0)
            
            if top_values:
                # Sabse zyada kaunsa hai
                top_name = list(top_values.keys())[0]
                top_count = list(top_values.values())[0]
                total = sum(top_values.values())
                
                if total > 0:
                    pct = round(top_count / total * 100, 1)
                    
                    insights.append({
                        "type": "Distribution",
                        "text": f"In '{col}', the most common value is '{top_name}' which appears {top_count} times ({pct}% of data). There are {unique} unique values in total.",
                        "confidence_score": 95,
                        "badge": "Category Breakdown",
                        "details": f"Top 5: {', '.join([f'{k} ({v})' for k, v in top_values.items()])}"
                    })
                    
                    # Agar ek value dominate kar rahi hai
                    if pct > 60:
                        insights.append({
                            "type": "Concentration Risk",
                            "text": f"Warning: '{top_name}' dominates the '{col}' column with {pct}% share. This means your data is heavily concentrated in one category.",
                            "confidence_score": 90,
                            "badge": "Attention Needed",
                            "details": f"High concentration can indicate sampling bias or genuine business pattern"
                        })
    
    # =============================================
    # 2. Correlation Insights
    # =============================================
    for corr in correlations:
        confidence = 100 if corr['p_value'] < 0.01 else 80
        
        if corr['direction'] == 'positive':
            if corr['strength'] == 'strong':
                text = f"Strong connection found: When '{corr['col1']}' goes up, '{corr['col2']}' also goes up significantly. These two are closely linked."
            else:
                text = f"Moderate connection: '{corr['col1']}' and '{corr['col2']}' tend to move in the same direction, but the link is not very strong."
        else:
            if corr['strength'] == 'strong':
                text = f"Strong inverse relationship: When '{corr['col1']}' increases, '{corr['col2']}' tends to decrease significantly."
            else:
                text = f"Moderate inverse trend: Higher '{corr['col1']}' values are somewhat associated with lower '{corr['col2']}' values."
            
        insights.append({
            "type": "Relationship",
            "text": text,
            "confidence_score": confidence,
            "badge": "Connection Found",
            "details": f"Correlation strength: {corr['correlation']} (1.0 = perfect match, -1.0 = perfect opposite)"
        })
        
    # =============================================
    # 3. Association / Pattern Insights
    # =============================================
    for rule in associations:
        antecedent_str = " + ".join(rule['if'])
        consequent_str = " + ".join(rule['then'])
        confidence_pct = int(rule['confidence'] * 100)
        
        text = f"Pattern discovered: When '{antecedent_str}' is present, '{consequent_str}' also appears {confidence_pct}% of the time. This is {rule['lift']}x more likely than random chance."
        
        insights.append({
            "type": "Pattern",
            "text": text,
            "confidence_score": confidence_pct,
            "badge": "High Confidence" if confidence_pct >= 80 else "Medium Confidence",
            "details": f"This pattern appears in {round(rule['support']*100, 1)}% of all records"
        })
        
    # =============================================
    # 4. Anomaly Insights
    # =============================================
    if anomalies:
        count = len(anomalies)
        insights.append({
            "type": "Risk Alert",
            "text": f"{count} unusual record(s) detected that don't follow normal patterns. These could be data entry errors, fraud, or genuinely exceptional cases. Manual review recommended.",
            "confidence_score": 92,
            "badge": "Action Required",
            "details": f"Detected using Isolation Forest AI algorithm. These records deviate significantly from the rest of the data."
        })
        
    # =============================================
    # 5. Segmentation Insights
    # =============================================
    if segments:
        largest = max(segments, key=lambda x: x['size'])
        smallest = min(segments, key=lambda x: x['size'])
        
        text = f"Your data naturally falls into {len(segments)} distinct groups. "
        text += f"The biggest group has {largest['percentage']}% of data, while the smallest has {smallest['percentage']}%."
        
        insights.append({
            "type": "Segmentation",
            "text": text,
            "confidence_score": 85,
            "badge": "Groups Found",
            "details": "Auto-grouped using K-Means clustering based on numeric patterns"
        })
        
    # No insights at all? Still give a friendly message
    if not insights:
        insights.append({
            "type": "Info",
            "text": "No significant patterns or anomalies found. Your data appears to be uniform and well-distributed.",
            "confidence_score": 50,
            "badge": "All Clear",
            "details": "Try uploading a larger dataset (100+ rows) for more detailed analysis"
        })
    
    # Sort: Key Metrics first, then by confidence
    type_priority = {"About": -2, "Data Cleaning": -1, "Summary": 0, "Distribution": 1, "Concentration Risk": 2, 
                     "Data Quality": 3, "Risk Alert": 4, "Relationship": 5, 
                     "Pattern": 6, "Segmentation": 7, "Info": 8}
    
    insights = sorted(insights, key=lambda x: (type_priority.get(x['type'], 99), -x['confidence_score']))
    
    return insights
