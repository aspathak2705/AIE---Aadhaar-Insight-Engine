import pandas as pd


def merge_datasets(enrol_df, demo_df, bio_df):
    #Merge all 3 datasets into unified dataset
    merge_cols = ["state", "district", "pincode", "region_key"]

    df = enrol_df.merge(demo_df, on=merge_cols, how="left")
    df = df.merge(bio_df, on=merge_cols, how="left")

    print("Total rows:", len(df))
    print("Unique regions:", df["region_key"].nunique())
    

    return df


def fill_missing_values(df):
    #Fill missing numeric values with 0
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)

    return df


def create_totals(df):
    #Create total columns
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


def create_ratios(df):
    #Create safe ratios
    df["demo_to_enrol_ratio"] = (
        df["total_demographic"] / df["total_enrolment"].clip(lower=10)
    )

    df["bio_to_enrol_ratio"] = (
        df["total_biometric"] / df["total_enrolment"].clip(lower=10)
    )

    return df


def create_growth_features(df):
    #Monthly growth per region
    df = df.sort_values(["region_key", "date"])

    df["monthly_growth"] = df.groupby("region_key")["total_enrolment"].pct_change()

    return df

def aggregate_region(df, value_cols):
    group_cols = ["state", "district", "pincode", "region_key"]
    return df.groupby(group_cols)[value_cols].sum().reset_index()

def create_ratio_features(df):
    ratio_df = df[[
        "state", "district", "pincode", "region_key",
        "demo_to_enrol_ratio",
        "bio_to_enrol_ratio"
    ]].copy()

    return ratio_df

def create_volume_features(df):
    volume_df = df[[
        "state", "district", "pincode", "region_key",
        "total_enrolment",
        "total_demographic",
        "total_biometric"
    ]].copy()

    return volume_df

def add_month_column(df):
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df

def aggregate_monthly(df, value_cols):
    df = add_month_column(df)

    group_cols = ["state", "district", "pincode", "region_key", "month"]

    df = df.groupby(group_cols)[value_cols].sum().reset_index()

    return df

def create_monthly_features(enrol_df, demo_df, bio_df):

    # Aggregate monthly
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

    # Ratios (safe)
    df["demo_to_enrol_ratio"] = (
        df["total_demographic"] / df["total_enrolment"].clip(lower=10)
    )

    df["bio_to_enrol_ratio"] = (
        df["total_biometric"] / df["total_enrolment"].clip(lower=10)
    )

    return df


def create_basic_features(enrol_df, demo_df, bio_df):

    enrol_df = aggregate_region(
        enrol_df, ["age_0_5", "age_5_17", "age_18_greater"]
    )

    demo_df = aggregate_region(
        demo_df, ["demo_age_5_17", "demo_age_17_"]
    )

    bio_df = aggregate_region(
        bio_df, ["bio_age_5_17", "bio_age_17_"]
    )

    df = merge_datasets(enrol_df, demo_df, bio_df)

    df = fill_missing_values(df)
    df = create_totals(df)

    print(df[["total_enrolment", "total_demographic", "total_biometric"]].describe())

    df = create_ratios(df)

    return df