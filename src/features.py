import pandas as pd


def get_category_views(df):
    """Return total views grouped by movie category"""
    return df.groupby("Category")["Number_of_Views"].sum().reset_index()


def get_monthly_views(df):
    """Return monthly viewing trend"""
    return df.groupby("Viewing_Month")["Number_of_Views"].sum().reset_index()


def get_top_movies(df, n=5):
    """Return top N movies by views"""
    return df.sort_values(by="Number_of_Views", ascending=False).head(n)


def get_basic_stats(df):
    """Return summary metrics"""
    return {
        "total_films": df["Film_Name"].nunique(),
        "total_views": df["Number_of_Views"].sum(),
        "avg_rating": round(df["Viewer_Rate"].mean(), 2)
    }
