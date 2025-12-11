import pandas as pd
import numpy as np


def load_data(filepath: str):
    """Load the dataset from CSV"""
    df = pd.read_csv(filepath)
    return df


def clean_data(df: pd.DataFrame):
    """Clean and format dataset"""

    # -----------------------------
    # Convert dates
    # -----------------------------
    df["Release_Date"] = pd.to_datetime(df["Release_Date"], errors="coerce")
    df["Viewing_Month"] = pd.to_datetime(df["Viewing_Month"], errors="coerce")

    # -----------------------------
    # Remove duplicates and missing values
    # -----------------------------
    df = df.drop_duplicates()
    df = df.dropna().reset_index(drop=True)

    # -----------------------------
    # Create unique Movie_ID
    # -----------------------------
    df['Movie_ID'] = (df['Film_Name'] + df['Release_Date'].astype(str) +
                      df['Category'] + df['Language']).apply(lambda x: hash(x))

    # -----------------------------
    # Compute trending score (optional)
    # -----------------------------
    today = pd.Timestamp.today()
    df['days_since_release'] = (today - df['Release_Date']).dt.days
    df['days_since_release'] = df['days_since_release'].replace(0, 1)
    df['months_since_release'] = df['days_since_release'] / 30
    df['trending_score'] = df['Number_of_Views'] / df['months_since_release']

    return df


def save_cleaned_data(df: pd.DataFrame, path: str = "data/Film_Dataset_Cleaned.csv"):
    """Save the cleaned dataframe to CSV"""
    df.to_csv(path, index=False)
    print(f"Cleaned dataset saved to {"data/cleaned_dataset.csv"}")
