import os
import pandas as pd
from glob import glob
from src.clean import clean_dataframe, add_region_key


def load_csv_files(folder_path: str) -> pd.DataFrame:
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
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    return df


def process_dataset(input_path: str, value_columns: list) -> pd.DataFrame:
    df = load_csv_files(input_path)
    df = standardize_columns(df)

    df = clean_dataframe(df)
    df = add_region_key(df)

    group_cols = ["date", "state", "district", "pincode", "region_key"]
    df = df.groupby(group_cols)[value_columns].sum().reset_index()

    return df


def save_dataframe(df: pd.DataFrame, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")