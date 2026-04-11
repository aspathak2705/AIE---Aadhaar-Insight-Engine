import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(
    layout="wide",
    page_title="Aadhaar Intelligence System",
    page_icon="🇮🇳"
)

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/processed/features/anomaly_features.csv")
        monthly_df = pd.read_csv("data/processed/time_series/monthly_features.csv")
        return df, monthly_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        raise e

df, monthly_df = load_data()

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.title("🧭 Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "📊 Overview",
        "🗺️ Geo Intelligence",
        "📈 Temporal Analysis",
        "📊 Distribution",
        "🔍 Investigation"
    ]
)

# -------------------------------
# GLOBAL FILTER
# -------------------------------
st.sidebar.markdown("## 🔍 Filters")

selected_state = st.sidebar.selectbox(
    "Select State",
    ["All"] + sorted(df["state"].unique())
)

if selected_state != "All":
    df = df[df["state"] == selected_state]
    monthly_df = monthly_df[monthly_df["state"] == selected_state]

# -------------------------------
# 📊 OVERVIEW PAGE
# -------------------------------
if page == "📊 Overview":

    st.title("📊 System Overview")

    st.markdown("""
    This dashboard detects unusual Aadhaar activity patterns across India.
    It helps identify anomalies, spikes, and high-risk regions.
    """)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🌍 Regions", df["region_key"].nunique())
    col2.metric("⚠️ Avg Risk", round(df["anomaly_score"].mean(), 3))
    col3.metric("🚨 High Risk", (df["anomaly_score"] > 0.7).sum())
    col4.metric("📈 Max Activity", int(df["activity_ratio"].max()))

    # Alert
    high_risk = df[df["anomaly_score"] > 0.8]

    if len(high_risk) > 0:
        st.error(f"🚨 {len(high_risk)} HIGH RISK regions detected!")

    st.subheader("🚨 Top Risk Regions")

    st.dataframe(
        df.sort_values("anomaly_score", ascending=False).head(10),
        use_container_width=True
    )

# -------------------------------
# 🗺️ GEO INTELLIGENCE
# -------------------------------
elif page == "🗺️ Geo Intelligence":

    st.title("🗺️ Geo Intelligence")

    st.markdown("""
    Identify which regions show abnormal behavior.
    Darker colors = higher risk.
    """)

    metric_option = st.selectbox(
        "Color by:",
        ["anomaly_score", "activity_ratio"]
    )

    state_df = df.groupby("state")[metric_option].mean().reset_index()

    with open("Dashboard/india_district.geojson") as f:
        india_geojson = json.load(f)

    for feature in india_geojson["features"]:
        feature["properties"]["NAME_1"] = feature["properties"]["NAME_1"].lower().strip()

    state_df["state"] = state_df["state"].str.lower().str.strip()

    fig = px.choropleth(
        state_df,
        geojson=india_geojson,
        locations="state",
        featureidkey="properties.NAME_1",
        color=metric_option,
        color_continuous_scale="Reds"
    )

    fig.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 📈 TEMPORAL ANALYSIS
# -------------------------------
elif page == "📈 Temporal Analysis":

    st.title("📈 Time-Based Analysis")

    st.markdown("""
    Detect spikes and unusual trends over time.
    """)

    region = st.selectbox("Select Region", monthly_df["region_key"].unique())

    region_df = monthly_df[monthly_df["region_key"] == region]

    region_df["rolling"] = region_df["activity_ratio"].rolling(3).mean()

    fig = px.line(region_df, x="month", y="activity_ratio", title="Activity Trend")

    fig.add_scatter(x=region_df["month"], y=region_df["rolling"], name="Trend")

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 📊 DISTRIBUTION
# -------------------------------
elif page == "📊 Distribution":

    st.title("📊 Distribution Analysis")

    st.markdown("""
    Understand how activity is distributed across regions.
    """)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.box(df, y="activity_ratio", title="Outlier Detection")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(df, x="activity_ratio", nbins=50)
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 🔍 INVESTIGATION
# -------------------------------
elif page == "🔍 Investigation":

    st.title("🔍 Deep Investigation")

    st.markdown("""
    Drill down into specific regions to analyze risk.
    """)

    state = st.selectbox("State", df["state"].unique())

    district_df = df[df["state"] == state]

    district = st.selectbox("District", district_df["district"].unique())

    pincode_df = district_df[district_df["district"] == district]

    fig = px.bar(
        pincode_df.sort_values("anomaly_score", ascending=False).head(10),
        x="pincode",
        y="anomaly_score",
        title="Top Risk Pincodes"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(pincode_df.sort_values("anomaly_score", ascending=False).head(20))