import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

from src.data_cleaning import load_data, clean_data
from src.features import (
    get_category_views,
    get_monthly_views,
    get_top_movies,
    get_basic_stats,
)
from src.utils import custom_style
from src.modeling import predict_top_category


# -----------------------------------------------------
# PAGE SETTINGS
# -----------------------------------------------------
st.set_page_config(
    page_title="IMovie Dashboard",
    layout="wide"
)

custom_style()
st.title("IMovie – Marketing Strategy Dashboard for Dec 2025")


# -----------------------------------------------------
# LOAD & CLEAN DATA
# -----------------------------------------------------
df = load_data("data/Film_Dataset.csv")
df = clean_data(df)


# Ensure Release_Date is datetime
df['Release_Date'] = pd.to_datetime(df['Release_Date'])

# Current date (today)
today = pd.Timestamp.today()

# Days since release
df['days_since_release'] = (today - df['Release_Date']).dt.days

# Convert to months (approximate: 30 days per month)
df['months_since_release'] = df['days_since_release'] / 30

# Replace 0 months with 1 to avoid division by zero
df['months_since_release'] = df['months_since_release'].replace(0, 1)

# Trending score
df['trending_score'] = df['Number_of_Views'] / df['months_since_release']

# display in streamlit
st.header(" Trending Movies (Fastest Growing)")

trending_movies = df.sort_values(by='trending_score', ascending=False).head(10)

st.dataframe(trending_movies[['Film_Name', 'Release_Date',
             'Number_of_Views', 'months_since_release', 'trending_score']])


# -----------------------------------------------------
# BASIC METRICS
# -----------------------------------------------------
metrics = get_basic_stats(df)

col1, col2, col3 = st.columns(3)
col1.metric("Total Films", metrics["total_films"])
col2.metric("Total Views", metrics["total_views"])
col3.metric("Average Rating", metrics["avg_rating"])


# -----------------------------------------------------
# CATEGORY VIEWS
# -----------------------------------------------------
st.header("Views by Category")
cat_df = get_category_views(df)

fig1 = px.bar(cat_df, x="Category", y="Number_of_Views",
              title="Total Views by Category",
              text_auto=True)

st.plotly_chart(fig1, use_container_width=True)


# -----------------------------------------------------
# MONTHLY TREND
# -----------------------------------------------------
st.header(" Monthly Viewing Trend")
monthly_df = get_monthly_views(df)

fig2 = px.line(monthly_df, x="Viewing_Month", y="Number_of_Views",
               markers=True,
               title="Viewing Trend Over Time")

st.plotly_chart(fig2, use_container_width=True)


# -----------------------------------------------------
# TOP MOVIES
# -----------------------------------------------------
st.header(" Top 5 Most Watched Movies")
top_movies = get_top_movies(df)

st.dataframe(top_movies)


def show_interactive_pie(df, column):
    # Count values
    data = df[column].value_counts().reset_index()
    data.columns = [column, "Count"]

    fig = px.pie(
        data,
        names=column,
        values="Count",
        title=f"Distribution of {column}",
        hole=0.3,
    )

    fig.update_traces(
        pull=[0.05]*len(data),       # slight pull-out animation
        hoverinfo="label+percent+value"
    )

    fig.update_layout(
        transition_duration=500      # smooth animation
    )

    st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------
# INTERACTIVE PIE CHART
# -----------------------------------------------------
st.header("Interactive Pie Chart")

column_option = st.selectbox(
    "Choose a column for the pie chart:",
    ["Category", "Language"]   # add more if needed
)

show_interactive_pie(df, column_option)


# -----------------------------------------------------
# MARKETING INSIGHTS
# -----------------------------------------------------
st.header("Marketing Insights (For December 2025)")

top_category = predict_top_category(df)

st.subheader("Recommended Category to Promote")
st.success(f"Top trending category: **{top_category}**")

st.write("""
### Suggested Marketing Actions:
- Promote movies under the top category.
- Create a **holiday special playlist** (December season).
- Use top-rated films (4.5+ rating) for push notifications.
- Offer **weekend and holiday subscription bundles**.
- Promote Horror, Romance, and Action/Sci-Fi based on view trends.
""")
