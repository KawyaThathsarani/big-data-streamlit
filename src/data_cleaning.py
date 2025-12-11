import pandas as pd


def load_data(filepath: str):
    """Load the dataset from CSV"""
    df = pd.read_csv("data/Film_Dataset.csv")
    return df


def clean_data(df: pd.DataFrame):
    """Clean and format dataset"""

    # Convert dates
    df["Release_Date"] = pd.to_datetime(df["Release_Date"], errors="coerce")
    df["Viewing_Month"] = pd.to_datetime(df["Viewing_Month"], errors="coerce")

    # Remove duplicates
    df = df.drop_duplicates()

    # Remove missing values if any
    df = df.dropna()

    return df
