import pandas as pd


def predict_top_category(df):
    """Predict category with highest demand for next month"""
    category_views = df.groupby("Category")["Number_of_Views"].sum()
    return category_views.idxmax()
