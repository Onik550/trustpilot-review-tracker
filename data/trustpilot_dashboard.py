import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Database connection
def get_data():
    conn = sqlite3.connect("C:\\Users\\acer\\trustpilot_review_tracker\\data\\trustpilot_reviews.db")
    df = pd.read_sql_query("SELECT * FROM reviews", conn)
    conn.close()
    return df

# Load Data
df = get_data()

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sidebar Filters
st.sidebar.header("Filters")
selected_company = st.sidebar.multiselect("Select Company", df["company"].unique(), default=df["company"].unique())
selected_rating = st.sidebar.multiselect("Select Rating", df["rating"].unique(), default=df["rating"].unique())
selected_country = st.sidebar.multiselect("Select Country", df["country"].dropna().unique(), default=df["country"].dropna().unique())
selected_date = st.sidebar.date_input("Select Date Range", [df["timestamp"].min().date(), df["timestamp"].max().date()])

# Filter Data
df_filtered = df[
    (df["company"].isin(selected_company)) &
    (df["rating"].isin(selected_rating)) &
    (df["country"].isin(selected_country)) &
    (df["timestamp"].dt.date.between(selected_date[0], selected_date[1]))
]

st.title("📊 Trustpilot Review Dashboard")
st.write("### Filtered Data")
st.dataframe(df_filtered)

# Reviews Over Time
st.write("### Reviews Over Time")
reviews_over_time = df_filtered.groupby(df_filtered["timestamp"].dt.date).size().reset_index(name="Count")
fig_time = px.line(reviews_over_time, x="timestamp", y="Count", markers=True, title="Reviews Trend Over Time")
st.plotly_chart(fig_time)

# Reviews Per Company
st.write("### Total Reviews Per Company")
reviews_per_company = df_filtered["company"].value_counts().reset_index()
reviews_per_company = reviews_per_company.reset_index()  # Ensure 'company' is a column

fig_company = px.bar(reviews_per_company, x="company", y="count", text="count", title="Reviews Per Company")
st.plotly_chart(fig_company)

# Ratings Distribution
st.write("### Ratings Distribution")
fig_ratings = px.pie(df_filtered, names="rating", title="Ratings Breakdown")
st.plotly_chart(fig_ratings)

# Reviews By Country
st.write("### Reviews By Country")
reviews_per_country = df_filtered["country"].value_counts().reset_index()
fig_country = px.bar(reviews_per_country, x="index", y="country", text="country", title="Reviews Per Country")
st.plotly_chart(fig_country)

st.write("### End of Dashboard")
