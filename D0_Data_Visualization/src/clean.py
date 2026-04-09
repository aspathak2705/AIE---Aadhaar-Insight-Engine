import pandas as pd


# Optional: State normalization mapping (extend later if needed)
STATE_MAPPING = {
    "andaman & nicobar islands": "andaman and nicobar islands",
    "dadra & nagar haveli": "dadra and nagar haveli",
    "daman & diu": "daman and diu",
}


def normalize_text(text: str) -> str:
    """
    Standardize text fields (state, district)
    """
    if pd.isna(text):
        return text

    text = str(text).strip().lower()
    text = text.replace("&", "and")

    return text


def normalize_state(state: str) -> str:
    state = normalize_text(state)
    return STATE_MAPPING.get(state, state)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline
    """

    # Normalize text columns
    if "state" in df.columns:
        df["state"] = df["state"].apply(normalize_state)

    if "district" in df.columns:
        df["district"] = df["district"].apply(normalize_text)

    # Clean pincode
    if "pincode" in df.columns:
        df["pincode"] = (
            df["pincode"]
            .astype(str)
            .str.extract(r"(\d{6})")[0]  # keep only valid 6-digit
        )

    # Convert date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df


def add_region_key(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create composite region key
    """
    df["region_key"] = (
        df["state"].astype(str) + "_" +
        df["district"].astype(str) + "_" +
        df["pincode"].astype(str)
    )

    return df