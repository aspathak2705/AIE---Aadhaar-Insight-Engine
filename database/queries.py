import sqlite3
import pandas as pd

DB_PATH = "data/aadhaar.db"

def get_connection():
    return sqlite3.connect(DB_PATH)


def get_state_data(state):
    conn = get_connection()

    query = """
    SELECT * FROM regional_features
    WHERE state = ?
    """

    df = pd.read_sql(query, conn, params=(state,))
    conn.close()
    return df


def get_top_anomalies(limit=20):
    conn = get_connection()

    query = """
    SELECT * FROM regional_features
    ORDER BY anomaly_score DESC
    LIMIT ?
    """

    df = pd.read_sql(query, conn, params=(limit,))
    conn.close()
    return df


def get_time_series(state):
    conn = get_connection()

    query = """
    SELECT * FROM monthly_features
    WHERE state = ?
    """

    df = pd.read_sql(query, conn, params=(state,))
    conn.close()
    return df