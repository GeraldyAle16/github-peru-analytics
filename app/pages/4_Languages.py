import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Language Analytics", layout="wide")
st.title("Programming Languages Distribution")

@st.cache_data
def load_data():
    try:
        repos_df = pd.read_csv("data/processed/repositories.csv")
        class_df = pd.read_csv("data/processed/classifications.csv")
        return repos_df, class_df
    except:
        return pd.DataFrame(), pd.DataFrame()

repos_df, class_df = load_data()

if repos_df.empty:
    st.error("No data available.")
    st.stop()

st.markdown("Distribution of programming languages used across public GitHub repositories in Peru.")

# Language distribution (Donut and Bar - Required 9.3)
langs = repos_df["language"].value_counts().reset_index()
langs.columns = ["language", "count"]

col1, col2 = st.columns([1, 1])
with col1:
    fig_pie = px.pie(langs.head(15), values="count", names="language", hole=0.4,
                    title="Top 15 Programming Languages (Donut)", color_discrete_sequence=px.colors.qualitative.Alphabet)
    st.plotly_chart(fig_pie, use_container_width=True)
with col2:
    fig_bar = px.bar(langs.head(15), x="language", y="count", color="count",
                    title="Top 15 Programming Languages (Bar Chart)", color_continuous_scale="Viridis")
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# Industry by Language Heatmap (Required 9.3)
if not class_df.empty:
    st.subheader("Industry by Language Correlation (Heatmap)")
    st.markdown("Mapping which programming languages are most prevalent in each Peruvian industry sector.")
    
    merged = pd.merge(class_df, repos_df[['id', 'language']], left_on='repo_id', right_on='id')
    heatmap_data = merged.groupby(['industry_name', 'language']).size().unstack(fill_value=0)
    
    top_industries = merged['industry_name'].value_counts().nlargest(10).index
    top_langs = merged['language'].value_counts().nlargest(10).index
    heatmap_data = heatmap_data.loc[top_industries, top_langs]
    
    fig_heat = px.imshow(heatmap_data, 
                        labels=dict(x="Programming Language", y="Industry", color="Repo Count"),
                        x=heatmap_data.columns,
                        y=heatmap_data.index,
                        color_continuous_scale="Viridis",
                        aspect="auto")
    st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

# Top Developers per Language (Required 9.1)
st.subheader("Top Developers per Language")
selected_lang = st.selectbox("Select Language to see Top Developers:", options=langs["language"])

lang_repos = repos_df[repos_df["language"] == selected_lang]
lang_devs = lang_repos.groupby('owner')['stargazers_count'].sum().reset_index()
lang_devs = lang_devs.nlargest(10, 'stargazers_count')
lang_devs.columns = ["Developer", "Total Stars in this Language"]

if not lang_devs.empty:
    fig_lang_devs = px.bar(lang_devs, x="Total Stars in this Language", y="Developer", orientation="h",
                          color="Total Stars in this Language", color_continuous_scale="Purples")
    st.plotly_chart(fig_lang_devs, use_container_width=True)
else:
    st.write("No developers found for this language.")
