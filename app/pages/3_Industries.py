import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Industry Analysis", layout="wide")
st.title("Industry Artificial Intelligence Analysis")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/processed/classifications.csv")
        return df
    except:
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.error("Industry classifications not found. Please run the AI Agent script.")
    st.stop()

st.markdown("Distribution of GitHub Repositories based on AI Inference of READMEs mapping to Peruvian industry standards (CIIU).")

inds = df["industry_name"].value_counts().reset_index()
inds.columns = ["industry", "count"]

col1, col2 = st.columns([1, 1])
with col1:
    fig = px.bar(inds, x="count", y="industry", orientation="h", title="Repository Volume per Industry")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.dataframe(inds, use_container_width=True)

st.subheader("Explore Top Repos per Industry")
selected_ind = st.selectbox("Select Industry", options=inds["industry"])
filtered = df[df["industry_name"] == selected_ind]
st.dataframe(filtered[["repo_name", "confidence", "reasoning"]], use_container_width=True)
