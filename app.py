import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

# -----------------------------------------------------
# PAGE SETTINGS
# -----------------------------------------------------
st.set_page_config(
    page_title="Film Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('style.css')

st.title("Film Analytics Dashboard")

# -----------------------------------------------------
# LOAD DATA
# -----------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/Film_Dataset_Cleaned.csv")
    df['Release_Date'] = pd.to_datetime(df['Release_Date'])
    df['Viewing_Month'] = pd.to_datetime(df['Viewing_Month'])
    return df

df = load_data()

# Initialize session state for filters
if 'filter_category' not in st.session_state:
    st.session_state.filter_category = 'All'
if 'filter_language' not in st.session_state:
    st.session_state.filter_language = 'All'
if 'filter_month' not in st.session_state:
    st.session_state.filter_month = 'All'

# -----------------------------------------------------
# 1. SIDEBAR FILTERS
# -----------------------------------------------------
st.sidebar.header("Filters")

# Get unique values for filters
all_categories = sorted(df['Category'].unique().tolist())
all_languages = sorted(df['Language'].unique().tolist())
all_months = sorted(df['Viewing_Month'].dt.month.unique().tolist())
all_years = sorted(df['Release_Date'].dt.year.unique().tolist())

# Use simple selectbox widgets
selected_category = st.sidebar.selectbox(
    "Filter by Category",
    options=['All'] + all_categories,
    index=0
)

selected_language = st.sidebar.selectbox(
    "Filter by Language",
    options=['All'] + all_languages,
    index=0
)

# Filter by Month (viewing month)
month_options = ['All'] + [f"{m:02d}" for m in all_months]
selected_month = st.sidebar.selectbox(
    "Filter by Month",
    options=month_options,
    format_func=lambda x: x if x == 'All' else ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(x)-1],
    index=0
)

# Filter by Year (release year)
selected_year = st.sidebar.selectbox(
    "Filter by Year",
    options=['All'] + all_years,
    index=0
)

# Minimum Viewer Rating Slider
min_rating = st.sidebar.slider(
    "Minimum Viewer Rating",
    min_value=float(df['Viewer_Rate'].min()),
    max_value=float(df['Viewer_Rate'].max()),
    value=float(df['Viewer_Rate'].min()),
    step=0.1
)

# Sort Leaderboard By
sort_by = st.sidebar.radio(
    "Sort Leaderboard By",
    options=["Views", "Rating"],
    index=0
)

# Apply filters
df_filtered = df.copy()

# Category filter
if selected_category != 'All':
    df_filtered = df_filtered[df_filtered['Category'] == selected_category]

# Language filter
if selected_language != 'All':
    df_filtered = df_filtered[df_filtered['Language'] == selected_language]

# Month filter (viewing month)
if selected_month != 'All':
    df_filtered = df_filtered[df_filtered['Viewing_Month'].dt.month == int(selected_month)]

# Year filter (release year)
if selected_year != 'All':
    df_filtered = df_filtered[df_filtered['Release_Date'].dt.year == selected_year]

# Rating filter
df_filtered = df_filtered[df_filtered['Viewer_Rate'] >= min_rating]

# -----------------------------------------------------
# 2. TOP KPI SUMMARY
# -----------------------------------------------------
st.header("Key Performance Indicators")

# Calculate metrics
total_films = len(df_filtered)
total_views = df_filtered['Number_of_Views'].sum()
avg_rating = df_filtered['Viewer_Rate'].mean()
most_viewed_lang = df_filtered.groupby('Language')['Number_of_Views'].sum().idxmax() if len(df_filtered) > 0 else "N/A"
top_category = df_filtered.groupby('Category')['Number_of_Views'].sum().idxmax() if len(df_filtered) > 0 else "N/A"

# December performance rank
monthly_views = df.groupby(df['Viewing_Month'].dt.month)['Number_of_Views'].sum().sort_values(ascending=False)
december_rank = (monthly_views.rank(ascending=False).get(12, 0))

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Films", f"{total_films:,}")
with col2:
    st.metric("Total Views", f"{total_views:,}")
with col3:
    st.metric("Avg Rating", f"{avg_rating:.2f}")
with col4:
    st.metric("Top Language", most_viewed_lang)
with col5:
    st.metric("Top Category", top_category)
with col6:
    st.metric("Dec Rank", f"#{int(december_rank)}" if december_rank > 0 else "N/A")

st.divider()

# -----------------------------------------------------
# 3. LEADERBOARD SECTION
# -----------------------------------------------------
col_header, col_spacer, col_radio = st.columns([2, 2, 1])

with col_header:
    st.header("Top Films Leaderboard")

with col_radio:
    # Leaderboard display options
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    leaderboard_option = st.radio(
        "Display",
        options=["Top 10", "Top 20", "All"],
        horizontal=True,
        label_visibility="collapsed"
    )

# Sort leaderboard
if sort_by == "Views":
    df_sorted = df_filtered.sort_values('Number_of_Views', ascending=False)
else:
    df_sorted = df_filtered.sort_values('Viewer_Rate', ascending=False)

# Apply display limit
if leaderboard_option == "Top 10":
    df_display = df_sorted.head(10)
elif leaderboard_option == "Top 20":
    df_display = df_sorted.head(20)
else:
    df_display = df_sorted

# Add rank
df_display = df_display.reset_index(drop=True)
df_display.index += 1
df_display.index.name = 'Rank'

# Display leaderboard
st.dataframe(
    df_display[['Film_Name', 'Category', 'Language', 'Viewer_Rate', 'Number_of_Views']],
    width='stretch'
)

st.divider()

# -----------------------------------------------------
# 4. VIEWS OVER TIME
# -----------------------------------------------------
st.header("Views Over Time")

col1, col2 = st.columns(2)

with col1:
    st.subheader("(A) Views by Month")
    
    # Aggregate by month
    monthly_views = df_filtered.groupby(
        df_filtered['Viewing_Month'].dt.month
    )['Number_of_Views'].sum().reset_index()
    monthly_views.columns = ['Month', 'Views']
    
    # Create month names
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_views['Month_Name'] = monthly_views['Month'].apply(lambda x: month_names[int(x)-1])
    monthly_views['Month_Code'] = monthly_views['Month'].apply(lambda x: f"{int(x):02d}")
    
    # Highlight December
    monthly_views['Color'] = monthly_views['Month'].apply(lambda x: 'December' if x == 12 else 'Other Months')
    
    fig_monthly = px.bar(
        monthly_views,
        x='Month_Name',
        y='Views',
        title='Monthly Views Distribution',
        color='Color',
        color_discrete_map={'December': '#FF6B6B', 'Other Months': '#4ECDC4'},
        custom_data=['Month_Code']
    )
    fig_monthly.update_layout(showlegend=True)
    
    st.plotly_chart(fig_monthly, width='stretch')

with col2:
    st.subheader("(B) Views by Year")
    
    # Extract year and aggregate
    yearly_views = df_filtered.copy()
    yearly_views['Year'] = yearly_views['Release_Date'].dt.year
    yearly_agg = yearly_views.groupby('Year')['Number_of_Views'].sum().reset_index()
    
    fig_yearly = px.line(
        yearly_agg,
        x='Year',
        y='Number_of_Views',
        title='Yearly Views Trend',
        markers=True
    )
    st.plotly_chart(fig_yearly, width='stretch')

st.divider()

# -----------------------------------------------------
# 5. CATEGORY & LANGUAGE INSIGHTS
# -----------------------------------------------------
st.header("Category & Language Insights")

col1, col2 = st.columns(2)

with col1:
    st.subheader("(A) Views by Category")
    
    category_views = df_filtered.groupby('Category')['Number_of_Views'].sum().reset_index()
    
    fig_cat = px.pie(
        category_views,
        names='Category',
        values='Number_of_Views',
        title='Category Distribution',
        hole=0.4
    )
    
    st.plotly_chart(fig_cat, width='stretch')

with col2:
    st.subheader("(B) Views by Language")
    
    language_views = df_filtered.groupby('Language')['Number_of_Views'].sum().reset_index()
    language_views = language_views.sort_values('Number_of_Views', ascending=True)
    
    fig_lang = px.bar(
        language_views,
        x='Number_of_Views',
        y='Language',
        orientation='h',
        title='Language Performance'
    )
    
    st.plotly_chart(fig_lang, width='stretch')

# (C) Category × Language Heatmap
st.subheader("(C) Category × Language Heatmap")

heatmap_data = df_filtered.pivot_table(
    values='Number_of_Views',
    index='Category',
    columns='Language',
    aggfunc='sum',
    fill_value=0
)

fig_heatmap = px.imshow(
    heatmap_data,
    labels=dict(x="Language", y="Category", color="Views"),
    title="Views by Category and Language",
    color_continuous_scale='Blues',
    aspect="auto"
)
st.plotly_chart(fig_heatmap, width='stretch')

st.divider()

# -----------------------------------------------------
# 6. VIEWER RATING INSIGHTS
# -----------------------------------------------------
st.header("Viewer Rating Insights")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("(A) Rating Distribution")
    
    fig_rating_dist = px.histogram(
        df_filtered,
        x='Viewer_Rate',
        nbins=20,
        title='Rating Distribution',
        labels={'Viewer_Rate': 'Rating'},
        color_discrete_sequence=['#4ECDC4']
    )
    fig_rating_dist.update_traces(marker_line_color='white', marker_line_width=1.5)
    st.plotly_chart(fig_rating_dist, width='stretch')

with col2:
    st.subheader("(B) High Rating + Low Views")
    
    # Calculate bottom 40% threshold for views
    views_threshold = df_filtered['Number_of_Views'].quantile(0.4)
    rating_threshold = 4.0
    
    hidden_gems = df_filtered[
        (df_filtered['Viewer_Rate'] >= rating_threshold) &
        (df_filtered['Number_of_Views'] <= views_threshold)
    ].sort_values('Viewer_Rate', ascending=False).head(10)
    
    st.write(f"Films with Rating ≥ {rating_threshold} and Views ≤ {views_threshold:.0f}")
    st.dataframe(
        hidden_gems[['Film_Name', 'Category', 'Language', 'Viewer_Rate', 'Number_of_Views']],
        width='stretch'
    )

st.divider()

# -----------------------------------------------------
# 7. POPULARITY VS QUALITY ANALYSIS
# -----------------------------------------------------
st.header("Popularity vs Quality Analysis")

st.subheader("(A) Scatter Plot: Rating vs Views")

# Create scatter plot
fig_scatter = px.scatter(
    df_filtered,
    x='Viewer_Rate',
    y='Number_of_Views',
    color='Category',
    size='Number_of_Views',
    hover_data=['Film_Name', 'Language'],
    title='Viewer Rating vs Number of Views',
    labels={'Viewer_Rate': 'Viewer Rating', 'Number_of_Views': 'Number of Views'}
)
st.plotly_chart(fig_scatter, width='stretch')

st.subheader("(B) Callout Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    highest_rated = df_filtered.loc[df_filtered['Viewer_Rate'].idxmax()]
    st.metric("Highest Rating", f"{highest_rated['Viewer_Rate']:.1f}")
    st.caption(f"{highest_rated['Film_Name']}")

with col2:
    lowest_rated = df_filtered.loc[df_filtered['Viewer_Rate'].idxmin()]
    st.metric("Lowest Rating", f"{lowest_rated['Viewer_Rate']:.1f}")
    st.caption(f"{lowest_rated['Film_Name']}")

with col3:
    most_viewed = df_filtered.loc[df_filtered['Number_of_Views'].idxmax()]
    st.metric("Highest Views", f"{most_viewed['Number_of_Views']:,}")
    st.caption(f"{most_viewed['Film_Name']}")

with col4:
    least_viewed = df_filtered.loc[df_filtered['Number_of_Views'].idxmin()]
    st.metric("Lowest Views", f"{least_viewed['Number_of_Views']:,}")
    st.caption(f"{least_viewed['Film_Name']}")



# -----------------------------------------------------
# 9. FOOTER
# -----------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #94a3b8;'>
    <p style='margin: 0; font-size: 14px;'>Created for <strong>Big Data Analytics</strong></p>
    <p style='margin: 5px 0; font-size: 14px;'>A1 Data Visualization Assignment</p>
    <p style='margin: 10px 0 0 0; font-size: 12px;'>Film Analytics Dashboard | December 2025</p>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------
# 8. DECEMBER INSIGHTS PANEL
# -----------------------------------------------------
# st.header("December 2025 Strategy Insights")

# # Filter for December
# df_december = df[df['Viewing_Month'].dt.month == 12]

# if len(df_december) > 0:
#     # Top languages in December
#     dec_languages = df_december.groupby('Language')['Number_of_Views'].sum().sort_values(ascending=False).head(3)
    
#     # Top categories in December
#     dec_categories = df_december.groupby('Category')['Number_of_Views'].sum().sort_values(ascending=False).head(3)
    
#     # Films with high rating and low views
#     dec_views_threshold = df_december['Number_of_Views'].quantile(0.4)
#     dec_hidden_gems = df_december[
#         (df_december['Viewer_Rate'] >= 4.0) &
#         (df_december['Number_of_Views'] <= dec_views_threshold)
#     ].sort_values('Viewer_Rate', ascending=False).head(5)
    
#     # Recent releases performing well
#     recent_date = df_december['Release_Date'].max() - pd.Timedelta(days=180)
#     recent_performers = df_december[
#         df_december['Release_Date'] >= recent_date
#     ].sort_values('Number_of_Views', ascending=False).head(5)
    
#     # Generate insights
#     insights = f"""
# ### Key December Insights:

# **Top Performing Languages in December:**
# {chr(10).join([f"- **{lang}**: {views:,} views" for lang, views in dec_languages.items()])}

# **Highest Viewed Categories in December:**
# {chr(10).join([f"- **{cat}**: {views:,} views" for cat, views in dec_categories.items()])}

# **Films to Promote (High Rating + Low Views):**
# {chr(10).join([f"- **{row['Film_Name']}** ({row['Category']}) - Rating: {row['Viewer_Rate']}, Views: {row['Number_of_Views']:,}" for _, row in dec_hidden_gems.iterrows()])}

# **New Releases Performing Well:**
# {chr(10).join([f"- **{row['Film_Name']}** - {row['Number_of_Views']:,} views" for _, row in recent_performers.iterrows()])}

# ### Recommended Actions:
# - Focus marketing efforts on **{dec_languages.index[0]}** language content
# - Promote **{dec_categories.index[0]}** category films during holiday season
# - Create special playlists featuring hidden gems with high ratings
# - Leverage recent successful releases in social media campaigns
# - Offer bundled promotions for top-performing categories
# """
    
#     st.markdown(insights)
# else:
#     st.info("No December data available for insights.")

# st.divider()

# # -----------------------------------------------------
# # 9. FOOTER / METADATA
# # -----------------------------------------------------
# st.markdown("---")
# st.markdown("""
# ### Dashboard Information

# **Data Source:** Film_Dataset_Cleaned.csv  
# **Team Registration Numbers:** [Add your registration numbers here]  
# **Version:** 1.0.0  
# **Last Updated:** December 2025  
# **Dashboard Created By:** Film Analytics Team

# ---
# *This dashboard provides comprehensive insights into film performance to support strategic decision-making for December 2025 marketing campaigns.*
# """)
