import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Language Analytics", layout="wide")
st.title("Programming Languages Distribution")

@st.cache_data
def load_data():
    try: return pd.read_csv("data/processed/repositories.csv")
    except: return pd.DataFrame()

df = load_data()
if df.empty:
    st.error("No data available.")
    st.stop()

st.markdown("Distribution of programming languages used across public GitHub repositories in Peru.")

langs = df["language"].value_counts().reset_index()
langs.columns = ["language", "count"]

fig = px.pie(langs.head(15), values="count", names="language", hole=0.4)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Top Used Languages")
st.dataframe(langs.head(15), use_container_width=True)
