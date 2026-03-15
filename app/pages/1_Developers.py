import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Developers Explorer", layout="wide")
st.title("Developer Explorer")

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/users.csv")

try:
    users_df = load_data()
except:
    st.error("No user data available.")
    st.stop()

# Filter Sidebar/Columns
col1, col2, col3 = st.columns(3)
with col1:
    min_stars = st.slider("Minimum Stars Received", 0, int(users_df['total_stars_received'].max() or 100), 0)
with col2:
    langs = sorted([x for x in users_df["primary_language_1"].unique() if str(x) != 'nan'])
    language_filter = st.multiselect("Filter by Primary Language", options=langs)
with col3:
    active_only = st.checkbox("Show active developers only (< 90d)")

filtered_df = users_df.copy()
if min_stars > 0:
    filtered_df = filtered_df[filtered_df["total_stars_received"] >= min_stars]
if language_filter:
    filtered_df = filtered_df[filtered_df["primary_language_1"].isin(language_filter)]
if active_only:
    filtered_df = filtered_df[filtered_df["is_active"] == True]

# Export to CSV (Required 9.1)
st.subheader(f"Results ({len(filtered_df)} developers found)")

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Data as CSV",
    data=csv,
    file_name='peru_developers_export.csv',
    mime='text/csv',
)

st.dataframe(
    filtered_df[["login", "name", "location", "total_repos", "total_stars_received", "followers", "impact_score", "primary_language_1"]],
    use_container_width=True
)

st.divider()
st.subheader("Developer Impact vs Followers")
fig = px.scatter(filtered_df, x="followers", y="impact_score", color="primary_language_1", 
                 hover_name="login", log_x=True, log_y=True,
                 labels={"followers": "Followers (Log scale)", "impact_score": "Impact Score (Log scale)"})
st.plotly_chart(fig, use_container_width=True)
