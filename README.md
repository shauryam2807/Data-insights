# Automated Data Insights Platform

An end-to-end data analytics platform that accepts CSV/Excel uploads and automatically generates data cleaning reports, statistical analysis, anomaly detection, and plain-English business insights through an interactive dashboard.

## Features

- **Automated Data Cleaning** — Removes duplicates, drops null rows, normalizes text categories, and assigns a Data Health Score (0–100).
- **Statistical Analysis** — Calculates mean, median, min, max, standard deviation, skewness for numeric columns and category distributions for text columns.
- **Correlation Detection** — Finds statistically significant relationships between numeric features using Pearson correlation with p-value testing.
- **Anomaly Detection** — Uses Isolation Forest (ML) to flag unusual records that deviate from normal patterns.
- **Customer Segmentation** — Applies K-Means clustering to group data into distinct segments automatically.
- **Association Mining** — Discovers patterns in categorical data using the Apriori algorithm.
- **Plain-English Insights** — Converts all analysis into non-technical language that stakeholders can act on immediately.
- **Interactive Dashboard** — Dark-themed, responsive UI with animated metric cards, Chart.js visualizations, and categorized insight cards.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, Uvicorn |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn (Isolation Forest, K-Means), mlxtend (Apriori) |
| Statistics | SciPy (Pearson correlation, entropy) |
| Frontend | HTML5, CSS3, JavaScript, Chart.js |
| Icons | Font Awesome 6 |

## Project Structure

```
data-insights/
├── backend/
│   ├── main.py                 # FastAPI server & API endpoints
│   ├── cleaners.py             # Data parsing, type detection, cleaning
│   ├── insights.py             # Plain-English insight generator
│   ├── requirements.txt        # Python dependencies
│   └── analyzers/
│       ├── __init__.py
│       ├── stats.py            # Numeric & categorical statistics
│       ├── correlations.py     # Pearson correlation analysis
│       ├── associations.py     # Apriori association rules
│       ├── anomalies.py        # Isolation Forest anomaly detection
│       └── segments.py         # K-Means clustering
├── frontend/
│   ├── index.html              # Dashboard layout
│   ├── styles.css              # Premium dark theme styling
│   ├── app.js                  # File upload & API integration
│   ├── charts.js               # Chart.js visualizations
│   └── insights.js             # Insight & anomaly rendering
└── .gitignore
```

## Setup & Installation

### Prerequisites
- Python 3.10+

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/data-insights.git
cd data-insights

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r backend/requirements.txt

# 5. Run the server
cd backend
uvicorn main:app --reload

# 6. Open in browser
# http://localhost:8000
```

## How It Works

1. **Upload** — Drag & drop or browse for a CSV/Excel file on the dashboard.
2. **Clean** — The system automatically detects column types, removes duplicates, drops rows with null values, and normalizes text.
3. **Analyze** — Five ML/statistical engines run in parallel: basic stats, correlations, associations, anomalies, and segmentation.
4. **Report** — Results are translated into plain-English insights and displayed with interactive charts, metric cards, and flagged anomaly records.

## API Endpoint

```
POST /api/analyze
Content-Type: multipart/form-data
Body: file (CSV or Excel)

Response: JSON with status, health_report, basic_stats, categorical_stats,
          correlations, associations, anomalies, segments, insights
```

## Screenshots

Upload your data and the dashboard automatically generates:
- Executive Summary with Health Score, Row Count, Feature Count
- Data Quality report with cleaning details
- Bar charts, Doughnut charts, Range charts, Polar Area charts
- Categorized insights with confidence badges
- Flagged anomaly records for manual review

## License

MIT License
