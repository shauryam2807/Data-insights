import pandas as pd
import io

def parse_uploaded_file(file_content: bytes, filename: str) -> pd.DataFrame:
    """Parse uploaded CSV or Excel file into a DataFrame."""
    try:
        if filename.endswith('.csv'):
            try:
                df = pd.read_csv(io.BytesIO(file_content))
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(file_content), encoding='latin1')
                
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file_content))
            
        else:
            raise ValueError(f"Unsupported file format: {filename}. Please upload CSV or Excel.")
            
        return df

    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")

def detect_column_types(df: pd.DataFrame) -> dict:
    """Auto-detect column types: numeric, categorical, datetime, boolean."""
    types = {}
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        unique_count = df[col].nunique()
        
        if 'datetime' in dtype:
            types[col] = 'datetime'
        elif 'bool' in dtype or unique_count == 2:
            types[col] = 'boolean'
        elif 'int' in dtype or 'float' in dtype:
            types[col] = 'numeric'
        else:
            # Fast datetime check: sample 20 values instead of parsing entire column
            if unique_count < 500:
                try:
                    sample = df[col].dropna().head(20)
                    if len(sample) > 0:
                        parsed = pd.to_datetime(sample, errors='coerce', infer_datetime_format=True)
                        if parsed.notnull().mean() > 0.5:
                            types[col] = 'datetime'
                        else:
                            types[col] = 'categorical'
                    else:
                        types[col] = 'categorical'
                except Exception:
                    types[col] = 'categorical'
            else:
                types[col] = 'categorical'
                
    return types

def clean_data_and_get_health_report(df: pd.DataFrame, col_types: dict):
    """Clean data by removing duplicates and null rows. Returns cleaned DataFrame and health report."""
    health_report = {
        "missing_values_fixed": {},
        "duplicates_found": 0,
        "null_rows_removed": 0,
        "rows_before": int(len(df)),
        "rows_after": 0,
        "outliers_flagged": {},
        "warnings": []
    }
    
    # 1. Remove duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        health_report["duplicates_found"] = int(duplicates)
        df = df.drop_duplicates().reset_index(drop=True)
        
    # 2. Count nulls per column (for reporting), then drop rows with any null
    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            health_report["missing_values_fixed"][col] = int(missing_count)
    
    rows_before_null_drop = len(df)
    df = df.dropna().reset_index(drop=True)
    null_rows_removed = rows_before_null_drop - len(df)
    health_report["null_rows_removed"] = int(null_rows_removed)
    health_report["rows_after"] = int(len(df))
        
    # 3. Category normalization
    for col, ctype in col_types.items():
        if col not in df.columns:
            continue
        if ctype == 'categorical':
            df[col] = df[col].astype(str).str.strip().str.title()
            
        # 4. Outlier flagging (IQR method)
        if ctype == 'numeric':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers_count = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            if outliers_count > 0:
                health_report["outliers_flagged"][col] = int(outliers_count)
                
    # Health Score calculation
    total_cells = health_report["rows_before"] * len(col_types)
    if total_cells > 0:
        total_issues = null_rows_removed + health_report["duplicates_found"]
        score = max(0, 100 - (total_issues / health_report["rows_before"] * 100))
        health_report["score"] = round(score)
    else:
        health_report["score"] = 0
    
    return df, health_report
