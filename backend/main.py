from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from cleaners import parse_uploaded_file, detect_column_types, clean_data_and_get_health_report
from analyzers.stats import generate_numeric_stats, generate_categorical_stats
from analyzers.correlations import generate_correlations
from analyzers.associations import generate_associations
from analyzers.anomalies import generate_anomalies
from analyzers.segments import generate_segments
from insights import generate_plain_english_insights
import os

app = FastAPI(title="Data Insights API")

@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """Main analysis endpoint. Accepts CSV/Excel and returns full analysis report."""
    try:
        file_content = await file.read()
        df = parse_uploaded_file(file_content, file.filename)
        col_types = detect_column_types(df)
        df_clean, health_report = clean_data_and_get_health_report(df, col_types)
        
        # 1. Basic Statistics
        num_stats = generate_numeric_stats(df_clean, col_types)
        cat_stats = generate_categorical_stats(df_clean, col_types)
        
        # 2. Advanced Analysis
        correlations = generate_correlations(df_clean, col_types)
        associations = generate_associations(df_clean, col_types)
        anomalies = generate_anomalies(df_clean, col_types)
        segments = generate_segments(df_clean, col_types)
        
        # 3. Plain English Insights
        insights = generate_plain_english_insights(
            correlations, associations, anomalies, segments,
            num_stats=num_stats, cat_stats=cat_stats, health_report=health_report,
            col_types=col_types, column_names=list(df_clean.columns)
        )
        
        return {
            "status": "success",
            "message": f"Successfully analyzed {file.filename}",
            "rows": len(df_clean),
            "columns": len(df_clean.columns),
            "column_types": col_types,
            "health_report": health_report,
            "basic_stats": num_stats,
            "categorical_stats": cat_stats,
            "correlations": correlations,
            "associations": associations,
            "anomalies": anomalies,
            "segments": segments,
            "insights": insights
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@app.get("/")
async def serve_frontend():
    """Serve the dashboard UI."""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
