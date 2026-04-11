import pandas as pd

# MERGE DATASETS
def merge_datasets(enrol_df, demo_df, bio_df):
    merge_cols = ["state", "district", "pincode", "region_key"]

    df = enrol_df.merge(demo_df, on=merge_cols, how="left")
    df = df.merge(bio_df, on=merge_cols, how="left")

    print("Total rows:", len(df))
    print("Unique regions:", df["region_key"].nunique())

    return df

# FILL MISSING VALUES
def fill_missing_values(df):
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    return df

# CREATE TOTALS
def create_totals(df):
    df["total_enrolment"] = df[
        ["age_0_5", "age_5_17", "age_18_greater"]
    ].sum(axis=1)

    df["total_demographic"] = df[
        ["demo_age_5_17", "demo_age_17_"]
    ].sum(axis=1)

    df["total_biometric"] = df[
        ["bio_age_5_17", "bio_age_17_"]
    ].sum(axis=1)

    return df


# AGGREGATE REGION (NO TIME)
def aggregate_region(df, value_cols):
    group_cols = ["state", "district", "pincode", "region_key"]
    return df.groupby(group_cols)[value_cols].sum().reset_index()

# FEATURE TABLES (CLEAN SEMANTICS)
def create_ratio_features(df):
    return df[[
        "state", "district", "pincode", "region_key",
        "activity_ratio",
        "bio_share",
        "demo_share"
    ]].copy()


def create_volume_features(df):
    return df[[
        "state", "district", "pincode", "region_key",
        "total_enrolment",
        "total_demographic",
        "total_biometric"
    ]].copy()


# BASIC FEATURE PIPELINE
def create_basic_features(enrol_df, demo_df, bio_df):

    # Aggregate per region
    enrol_df = aggregate_region(
        enrol_df, ["age_0_5", "age_5_17", "age_18_greater"]
    )

    demo_df = aggregate_region(
        demo_df, ["demo_age_5_17", "demo_age_17_"]
    )

    bio_df = aggregate_region(
        bio_df, ["bio_age_5_17", "bio_age_17_"]
    )

    # Merge
    df = merge_datasets(enrol_df, demo_df, bio_df)

    # Fill missing
    df = fill_missing_values(df)

    # Totals
    df = create_totals(df)

    # NEW SEMANTIC FEATURES (CRITICAL)
    df["activity_ratio"] = (
        df["total_biometric"] + df["total_demographic"]
    ) / df["total_enrolment"].clip(lower=50)

    df["activity_ratio"] = df["activity_ratio"].clip(0, 200)

    SMOOTHING = 10  # small constant

    df["bio_share"] = df["total_biometric"] / (
        df["total_biometric"] + df["total_demographic"] + SMOOTHING
    )

    df["demo_share"] = df["total_demographic"] / (
        df["total_biometric"] + df["total_demographic"] + SMOOTHING
    )

    # Debug (can remove later)
    print("\nVolume Stats:")
    print(df[["total_enrolment", "total_demographic", "total_biometric"]].describe())

    return df


# TIME-SERIES FUNCTIONS
def add_month_column(df):
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


def aggregate_monthly(df, value_cols):
    df = add_month_column(df)

    group_cols = ["state", "district", "pincode", "region_key", "month"]
    return df.groupby(group_cols)[value_cols].sum().reset_index()


# MONTHLY FEATURE PIPELINE
def create_monthly_features(enrol_df, demo_df, bio_df):

    # Monthly aggregation
    enrol_df = aggregate_monthly(
        enrol_df, ["age_0_5", "age_5_17", "age_18_greater"]
    )

    demo_df = aggregate_monthly(
        demo_df, ["demo_age_5_17", "demo_age_17_"]
    )

    bio_df = aggregate_monthly(
        bio_df, ["bio_age_5_17", "bio_age_17_"]
    )

    # Merge
    merge_cols = ["state", "district", "pincode", "region_key", "month"]

    df = enrol_df.merge(demo_df, on=merge_cols, how="left")
    df = df.merge(bio_df, on=merge_cols, how="left")

    # Fill missing
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Totals
    df["total_enrolment"] = df[
        ["age_0_5", "age_5_17", "age_18_greater"]
    ].sum(axis=1)

    df["total_demographic"] = df[
        ["demo_age_5_17", "demo_age_17_"]
    ].sum(axis=1)

    df["total_biometric"] = df[
        ["bio_age_5_17", "bio_age_17_"]
    ].sum(axis=1)

    # SAME SEMANTICS FOR TIME SERIES
    df["activity_ratio"] = (
        df["total_biometric"] + df["total_demographic"]
    ) / df["total_enrolment"].clip(lower=50)

    df["bio_share"] = df["total_biometric"] / (
        df["total_biometric"] + df["total_demographic"] + 1
    )

    df["demo_share"] = df["total_demographic"] / (
        df["total_biometric"] + df["total_demographic"] + 1
    )

    return df