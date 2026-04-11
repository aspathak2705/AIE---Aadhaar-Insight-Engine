import pandas as pd

# Z-SCORE FUNCTION
def compute_z_score(series):
    mean = series.mean()
    std = series.std()

    if std == 0 or pd.isna(std):
        return pd.Series([0] * len(series), index=series.index)

    return (series - mean) / std

# IQR OUTLIER DETECTION
def compute_iqr_flag(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    # Slightly stricter than 1.5 for skewed data
    upper_bound = q3 + 1.5 * iqr

    return (series > upper_bound).astype(int)

# ANOMALY FEATURE CREATION
def create_anomaly_features(df):

    #Build anomaly features using correct system semantics

    # PRIMARY SIGNAL: ACTIVITY RATIO
    df["z_score_activity"] = compute_z_score(df["activity_ratio"])
    df["iqr_flag_activity"] = compute_iqr_flag(df["activity_ratio"])

    # Normalize z-score (clip extreme values)
    df["z_score_activity_norm"] = (
        df["z_score_activity"].abs().clip(0, 5) / 5
    )

    # SECONDARY SIGNAL: SHARE BALANCE
    df["z_score_bio_share"] = compute_z_score(df["bio_share"])
    df["z_score_demo_share"] = compute_z_score(df["demo_share"])

    df["z_score_share_norm"] = (
        (df["z_score_bio_share"].abs() + df["z_score_demo_share"].abs())
        .clip(0, 5) / 5
    )

    # FINAL ANOMALY SCORE
    df["anomaly_score"] = (
    0.5 * df["z_score_activity_norm"] +
    0.3 * df["z_score_share_norm"] +
    0.2 * df["iqr_flag_activity"]
    )

    return df

# FINAL ANOMALY TABLE
def get_anomaly_table(df):
    #Extract clean anomaly dataset
    anomaly_df = df[[
        "state",
        "district",
        "pincode",
        "region_key",

        # Core features
        "total_enrolment",
        "total_demographic",
        "total_biometric",

        # New semantic features
        "activity_ratio",
        "bio_share",
        "demo_share",

        # Anomaly signals
        "z_score_activity",
        "iqr_flag_activity",
        "anomaly_score"
    ]].copy()

    return anomaly_df