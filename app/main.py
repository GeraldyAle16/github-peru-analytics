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

# Key metrics
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

# Row 1: Top 10s
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.subheader("Top 10 Developers by Impact")
    top_devs = users_df.nlargest(10, "impact_score")[["login", "impact_score"]]
    fig1 = px.bar(top_devs, x="login", y="impact_score", color="impact_score", 
                 color_continuous_scale="Viridis", labels={"impact_score": "Impact Score"})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Top 10 Repositories by Stars")
    top_repos = repos_df.nlargest(10, "stargazers_count")[["name", "stargazers_count"]]
    fig2 = px.bar(top_repos, x="name", y="stargazers_count", color="stargazers_count",
                 color_continuous_scale="Magma", labels={"stargazers_count": "Stars"})
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: Distributions & Timeline
st.divider()
col1, col2 = st.columns(2)
with col1:
    if not class_df.empty:
        st.subheader("Industry Distribution (CIIU)")
        industry_counts = class_df["industry_name"].value_counts().reset_index()
        industry_counts.columns = ["industry_name", "count"]
        fig3 = px.pie(industry_counts, values="count", names="industry_name", hole=0.3, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Run AI Agent to view Industry stats")

with col2:
    st.subheader("Activity Timeline (Account Creation)")
    # Convert created_at to datetime safely
    users_df['created_at_dt'] = pd.to_datetime(users_df['created_at'], errors='coerce')
    timeline = users_df.dropna(subset=['created_at_dt']).groupby(users_df['created_at_dt'].dt.year).size().reset_index(name='count')
    fig4 = px.line(timeline, x='created_at_dt', y='count', title='New Developer Accounts per Year',
                  markers=True, labels={"created_at_dt": "Year", "count": "New Accounts"})
    st.plotly_chart(fig4, use_container_width=True)

# Row 3: Technical Metrics & Map
st.divider()
colA, colB = st.columns([2, 1])

with colA:
    st.subheader("Technical Engagement: Stars vs Forks")
    fig5 = px.scatter(repos_df, x="stargazers_count", y="forks_count", 
                     color="language", hover_name="name", size="stargazers_count",
                     log_x=True, log_y=True, labels={"stargazers_count": "Stars (Log)", "forks_count": "Forks (Log)"})
    st.plotly_chart(fig5, use_container_width=True)

with colB:
    st.subheader("Developer Density Map (Peru)")
    # Simplified coordinate mapping for Peru cities
    coords = {
        'Lima': [-12.0464, -77.0428],
        'Arequipa': [-16.409, -71.5375],
        'Trujillo': [-8.116, -79.03],
        'Cusco': [-13.532, -71.9675],
        'Tacna': [-18.006, -70.246],
        'Piura': [-5.194, -80.632],
        'Iquitos': [-3.749, -73.253]
    }
    
    map_data = []
    for city, (lat, lon) in coords.items():
        count = users_df[users_df['location'].str.contains(city, case=False, na=False)].shape[0]
        if count > 0:
            map_data.append({'city': city, 'lat': lat, 'lon': lon, 'developers': count})
    
    if map_data:
        map_df = pd.DataFrame(map_data)
        st.map(map_df, latitude='lat', longitude='lon', size='developers', color='#ff4b4b')
    else:
        st.info("Insufficient location data for geographic map.")
