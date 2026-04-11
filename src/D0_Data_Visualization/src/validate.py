import pandas as pd
import yaml


def load_schema(schema_path="D0_Data_Visualization\config\schema.yaml"):
    with open(schema_path, "r") as file:
        return yaml.safe_load(file)


def check_required_columns(df: pd.DataFrame, required_cols: list):
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def check_nulls(df: pd.DataFrame):
    null_counts = df.isnull().sum()
    if null_counts.any():
        print("⚠️ Null values found:\n", null_counts[null_counts > 0])


def check_negative_values(df: pd.DataFrame, numeric_cols: list):
    for col in numeric_cols:
        if (df[col] < 0).any():
            raise ValueError(f"Negative values found in column: {col}")


def check_duplicates(df: pd.DataFrame):
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        print(f"⚠️ Found {dup_count} duplicate rows")


def validate_dataframe(df: pd.DataFrame, dataset_type: str, schema: dict):
    """
    Full validation pipeline
    """
    config = schema[dataset_type]

    check_required_columns(df, config["required_columns"])
    check_nulls(df)
    check_negative_values(df, config["numeric_columns"])
    check_duplicates(df)

    print(f"✅ Validation passed for {dataset_type}")

    return df