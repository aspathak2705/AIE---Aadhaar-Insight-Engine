import sqlite3
import pandas as pd

DB_PATH = "data/aadhaar.db"

def create_connection():
    return sqlite3.connect(DB_PATH)

def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS regional_features (
        date TEXT,
        state TEXT,
        district TEXT,
        pincode TEXT,
        region_key TEXT,
        total_enrolment INTEGER,
        total_demographic INTEGER,
        total_biometric INTEGER,
        demo_to_enrol_ratio REAL,
        bio_to_enrol_ratio REAL,
        activity_ratio REAL,
        bio_share REAL,
        demo_share REAL,
        anomaly_score REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_features (
        month TEXT,
        state TEXT,
        district TEXT,
        pincode TEXT,
        region_key TEXT,
        total_enrolment INTEGER,
        total_demographic INTEGER,
        total_biometric INTEGER,
        growth_rate REAL
    )
    """)

    cursor.execute("CREATE INDEX idx_state ON regional_features(state);")
    cursor.execute("CREATE INDEX idx_region ON regional_features(region_key);")
    cursor.execute("CREATE INDEX idx_anomaly ON regional_features(anomaly_score);")

    conn.commit()

def load_csv_to_db(conn):
    df = pd.read_csv("data/processed/features/anomaly_features.csv")
    df.to_sql("regional_features", conn, if_exists="replace", index=False)

    ts_df = pd.read_csv("data/processed/time_series/monthly_features.csv")
    ts_df.to_sql("monthly_features", conn, if_exists="replace", index=False)

def main():
    conn = create_connection()
    create_tables(conn)
    load_csv_to_db(conn)
    conn.close()

if __name__ == "__main__":
    main()