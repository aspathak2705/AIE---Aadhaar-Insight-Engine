from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import uvicorn
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Relative to where we run uvicorn
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "aadhaar.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/overview")
def get_overview(state: str = "All"):
    conn = get_db()
    
    where_clause = ""
    params = ()
    if state != "All":
        where_clause = "WHERE state = ?"
        params = (state,)
    
    query_stats = f"SELECT COUNT(DISTINCT region_key) as regions, AVG(anomaly_score) as avg_risk, SUM(CASE WHEN anomaly_score > 0.7 THEN 1 ELSE 0 END) as high_risk, MAX(activity_ratio) as max_activity FROM regional_features {where_clause}"
    cursor = conn.cursor()
    cursor.execute(query_stats, params)
    stats_row = cursor.fetchone()
    stats = dict(stats_row) if stats_row else {"regions": 0, "avg_risk": 0, "high_risk": 0, "max_activity": 0}
    
    query_top = f"SELECT state, district, pincode, anomaly_score FROM regional_features {where_clause} ORDER BY anomaly_score DESC LIMIT 10"
    top_regions = pd.read_sql(query_top, conn, params=params).to_dict(orient="records")
    
    conn.close()
    return {"stats": stats, "top_regions": top_regions}

@app.get("/api/states")
def get_states():
    conn = get_db()
    query = "SELECT DISTINCT state FROM regional_features ORDER BY state"
    df = pd.read_sql(query, conn)
    conn.close()
    return df['state'].tolist()

@app.get("/api/geo")
def get_geo(metric: str = "anomaly_score", state: str = "All"):
    if metric not in ["anomaly_score", "activity_ratio"]:
        metric = "anomaly_score"
    conn = get_db()

    if state != "All":
        query = f"""
            SELECT state, district, AVG({metric}) as value
            FROM regional_features
            WHERE state = ?
            GROUP BY state, district
        """
        df = pd.read_sql(query, conn, params=(state,))
        if not df.empty:
            df["state"] = df["state"].str.lower().str.strip()
            df["district"] = df["district"].str.lower().str.strip()
    else:
        query = f"SELECT state, AVG({metric}) as value FROM regional_features GROUP BY state"
        df = pd.read_sql(query, conn)
        if not df.empty:
            df["state"] = df["state"].str.lower().str.strip()

    conn.close()
    return df.to_dict(orient="records")

@app.get("/api/regions")
def get_regions(state: str = "All"):
    conn = get_db()
    if state != "All":
        query = "SELECT DISTINCT region_key FROM monthly_features WHERE state = ? ORDER BY region_key"
        df = pd.read_sql(query, conn, params=(state,))
    else:
        query = "SELECT DISTINCT region_key FROM monthly_features ORDER BY region_key"
        df = pd.read_sql(query, conn)
    conn.close()
    return df['region_key'].tolist()

@app.get("/api/temporal")
def get_temporal(state: str = "All", district: str = "All"):
    conn = get_db()
    where_clauses = []
    params = []
    
    if state != "All":
        where_clauses.append("state = ?")
        params.append(state)
    if district != "All":
        where_clauses.append("district = ?")
        params.append(district)
        
    where_stmt = ""
    if where_clauses:
        where_stmt = "WHERE " + " AND ".join(where_clauses)
        
    query = f"SELECT month, AVG(activity_ratio) as activity_ratio FROM monthly_features {where_stmt} GROUP BY month ORDER BY month"
    df = pd.read_sql(query, conn, params=tuple(params))
    conn.close()
    
    if not df.empty:
        df['rolling'] = df['activity_ratio'].rolling(3, min_periods=1).mean()
    else:
        df['rolling'] = []
    
    return df.to_dict(orient="records")

@app.get("/api/districts")
def get_districts(state: str):
    conn = get_db()
    query = "SELECT DISTINCT district FROM monthly_features WHERE state = ? ORDER BY district"
    df = pd.read_sql(query, conn, params=(state,))
    conn.close()
    return df['district'].tolist()

@app.get("/api/distribution")
def get_distribution(state: str = "All", district: str = "All"):
    conn = get_db()
    where_clauses = []
    params = []
    if state != "All":
        where_clauses.append("state = ?")
        params.append(state)
    if district != "All":
        where_clauses.append("district = ?")
        params.append(district)
        
    where_stmt = ""
    if where_clauses:
        where_stmt = "WHERE " + " AND ".join(where_clauses)
        
    query = f"SELECT activity_ratio, district FROM regional_features {where_stmt}"
    df = pd.read_sql(query, conn, params=tuple(params))
    conn.close()
    
    if df.empty:
        return {"histogram": [], "quantiles": {}, "district_breakdown": []}
        
    hist, bins = pd.cut(df['activity_ratio'], bins=20, retbins=True) # Reduced bins for UI
    counts = hist.value_counts(sort=False).tolist()
    bin_edges = bins.tolist()
    distribution = [{"name": f"{round(bin_edges[i], 1)}-{round(bin_edges[i+1], 1)}", "count": c} for i, c in enumerate(counts)]
    
    quantiles = df['activity_ratio'].quantile([0, 0.25, 0.5, 0.75, 1.0]).to_dict()
    quantiles = {str(k): v for k, v in quantiles.items()}
    
    district_breakdown = []
    if state != "All" and district == "All":
        grouped = df.groupby('district')['activity_ratio'].mean().reset_index()
        grouped = grouped.sort_values('activity_ratio', ascending=False)
        district_breakdown = grouped.to_dict(orient="records")
    
    return {"histogram": distribution, "quantiles": quantiles, "district_breakdown": district_breakdown}

@app.get("/api/investigation")
def get_investigation(state: str, district: str = None):
    conn = get_db()
    
    if not district:
        # Get districts for state
        query = "SELECT DISTINCT district FROM regional_features WHERE state = ? ORDER BY district"
        df_districts = pd.read_sql(query, conn, params=(state,))
        conn.close()
        return {"districts": df_districts["district"].tolist()}
    
    query = "SELECT pincode, anomaly_score FROM regional_features WHERE state = ? AND district = ? ORDER BY anomaly_score DESC"
    df = pd.read_sql(query, conn, params=(state, district))
    conn.close()
    
    return {
        "pincodes": df.to_dict(orient="records")
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
