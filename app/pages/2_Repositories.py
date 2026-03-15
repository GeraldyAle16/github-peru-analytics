import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Repositories Browser", layout="wide")
st.title("Repository Browser")

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/repositories.csv")

try:
    repos_df = load_data()
except:
    st.error("No repository data available.")
    st.stop()

search_term = st.text_input("Search description or repo name")

col1, col2 = st.columns(2)
with col1:
    industries = ["All"] + sorted([str(x) for x in repos_df["industry"].unique() if str(x) != 'nan'])
    ind_filter = st.selectbox("Industry Category", options=industries)
with col2:
    languages = ["All"] + sorted([str(x) for x in repos_df["language"].unique() if str(x) != 'nan'])
    lang_filter = st.selectbox("Primary Language", options=languages)

filtered = repos_df.copy()
if search_term:
    search_term = search_term.lower()
    filtered = filtered[
        filtered["name"].str.lower().str.contains(search_term, na=False) |
        filtered["description"].str.lower().str.contains(search_term, na=False)
    ]
if ind_filter != "All":
    filtered = filtered[filtered["industry"] == ind_filter]
if lang_filter != "All":
    filtered = filtered[filtered["language"] == lang_filter]

st.dataframe(
    filtered[["name", "owner", "industry", "language", "description", "stargazers_count", "forks_count", "open_issues_count"]],
    use_container_width=True
)
