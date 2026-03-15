import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Industry Analysis", layout="wide")
st.title("Industry Artificial Intelligence Analysis")

@st.cache_data
def load_data():
    try:
        class_df = pd.read_csv("data/processed/classifications.csv")
        repos_df = pd.read_csv("data/processed/repositories.csv")
        return class_df, repos_df
    except:
        return pd.DataFrame(), pd.DataFrame()

class_df, repos_df = load_data()

if class_df.empty:
    st.error("Industry classifications not found. Please run the AI Agent script.")
    st.stop()

st.markdown("Distribution of GitHub Repositories based on AI Inference of READMEs mapping to Peruvian industry standards (CIIU).")

# Join classifications with repo data to get stars/metadata
merged_df = pd.merge(class_df, repos_df[['id', 'stargazers_count', 'forks_count', 'owner', 'language']], 
                     left_on='repo_id', right_on='id', how='left')

# Industry volume chart
inds = merged_df["industry_name"].value_counts().reset_index()
inds.columns = ["industry", "count"]

col1, col2 = st.columns([1, 1])
with col1:
    fig = px.bar(inds, x="count", y="industry", orientation="h", 
                 title="Repository Volume per Industry", color="count", color_continuous_scale="Viridis")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.subheader("Industry Summary")
    st.dataframe(inds, use_container_width=True)

st.divider()

# Developer Specialization (Required 9.1)
st.subheader("Developer Specialization by Industry")
st.markdown("Top developers based on total stars earned in repositories within each industry.")

selected_ind = st.selectbox("Select Industry to examine Top Developers:", options=inds["industry"])
industry_repos = merged_df[merged_df["industry_name"] == selected_ind]

# Group by owner to see specialization
spec_df = industry_repos.groupby('owner')['stargazers_count'].sum().reset_index()
spec_df = spec_df.nlargest(10, 'stargazers_count')
spec_df.columns = ["Developer", "Total Stars in this Industry"]

if not spec_df.empty:
    fig_spec = px.bar(spec_df, x="Total Stars in this Industry", y="Developer", orientation="h",
                     color="Total Stars in this Industry", color_continuous_scale="Blues")
    st.plotly_chart(fig_spec, use_container_width=True)
else:
    st.write("No developer data available for this category.")

# Repo Details
st.subheader(f"Top Repositories in {selected_ind}")
st.dataframe(industry_repos[["repo_name", "language", "stargazers_count", "confidence", "reasoning"]].sort_values("stargazers_count", ascending=False), use_container_width=True)
