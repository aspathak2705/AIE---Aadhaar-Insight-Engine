import os
import pandas as pd
from glob import glob


def load_csv_files(folder_path: str) -> pd.DataFrame:
    """
    Load and concatenate all CSV files from a folder
    """
    all_files = glob(os.path.join("D0_Data_Visualization/data/raw", "*.csv"))

    if not all_files:
        raise FileNotFoundError(f"No CSV files found in {folder_path}")

    df_list = []
    for file in all_files:
        try:
            df = pd.read_csv(file)
            df_list.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    return pd.concat(df_list, ignore_index=True)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names (lowercase, strip spaces)
    """
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    return df


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Minimal cleaning for Phase 1
    """
    # Strip whitespace from string columns
    for col in ["state", "district"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Ensure pincode is string
    if "pincode" in df.columns:
        df["pincode"] = df["pincode"].astype(str).str.strip()

    return df


def aggregate_data(df: pd.DataFrame, value_columns: list) -> pd.DataFrame:
    """
    Aggregate data by date, state, district, pincode
    """
    group_cols = ["date", "state", "district", "pincode"]

    df = df.groupby(group_cols)[value_columns].sum().reset_index()

    return df


def process_dataset(input_path: str, value_columns: list) -> pd.DataFrame:
    """
    Full pipeline for one dataset type
    """
    df = load_csv_files(input_path)
    df = standardize_columns(df)
    df = basic_clean(df)

    # Ensure date format
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df = aggregate_data(df, value_columns)

    return df


def save_dataframe(df: pd.DataFrame, output_path: str):
    """
    Save dataframe to CSV
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")