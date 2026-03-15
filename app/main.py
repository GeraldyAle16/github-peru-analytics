import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="GitHub Peru Analytics",
    page_icon="🇵🇪",
    layout="wide"
)

@st.cache_data
def load_data():
    try:
        users_df = pd.read_csv("data/processed/users.csv")
        repos_df = pd.read_csv("data/processed/repositories.csv")
        class_df = pd.read_csv("data/processed/classifications.csv") if os.path.exists("data/processed/classifications.csv") else pd.DataFrame()
        return users_df, repos_df, class_df
    except FileNotFoundError:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

users_df, repos_df, class_df = load_data()

st.sidebar.title("🇵🇪 GitHub Peru Analytics")
st.sidebar.markdown("Analyzing the Peruvian developer ecosystem")

if users_df.empty:
    st.error("Data not found. Please run scripts/extract_data.py -> classify_repos.py -> calculate_metrics.py")
    st.stop()

st.title("Peru Developer Ecosystem Overview")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Developers", len(users_df))
with col2:
    st.metric("Total Repositories", len(repos_df))
with col3:
    st.metric("Total Stars", int(repos_df["stargazers_count"].sum()))
with col4:
    active_pct = (users_df["is_active"].sum() / len(users_df)) * 100
    st.metric("Active Developers", f"{active_pct:.1f}%")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Top 10 Developers by Impact")
    top_devs = users_df.nlargest(10, "impact_score")[["login", "impact_score"]]
    fig = px.bar(top_devs, x="login", y="impact_score", color="impact_score", color_continuous_scale="Viridis")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    if not class_df.empty:
        st.subheader("Industry Distribution (Top Repositories)")
        industry_counts = class_df["industry_name"].value_counts().reset_index()
        industry_counts.columns = ["industry_name", "count"]
        fig = px.pie(industry_counts, values="count", names="industry_name", hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run purely the GPT-4 classification script to view AI Industry distribution")
