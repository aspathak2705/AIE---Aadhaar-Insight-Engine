import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(layout="wide")


# LOAD DATA
@st.cache_data
def load_data():
    df = pd.read_csv("D0_Data_Visualization/data/processed/features/anomaly_features.csv")
    monthly_df = pd.read_csv("D0_Data_Visualization/data/processed/time_series/monthly_features.csv")
    return df, monthly_df

df, monthly_df = load_data()


# TITLE
st.title("🇮🇳 Aadhaar Intelligence Decision Dashboard")

# KPI OVERVIEW
st.subheader("📊 System Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Regions", df["region_key"].nunique())
col2.metric("Avg Anomaly Score", round(df["anomaly_score"].mean(), 3))
col3.metric("High Risk Regions", (df["anomaly_score"] > 0.7).sum())


st.subheader("🔥 State-Level Anomaly Heatmap")

# -------------------------------
# UI CONTROLS
# -------------------------------
metric_option = st.selectbox(
    "Color by:",
    ["anomaly_score", "activity_ratio"]
)

view_option = st.radio(
    "View Mode:",
    ["Cumulative", "Monthly"]
)

# -------------------------------
# CREATE state_df (IMPORTANT)
# -------------------------------
if view_option == "Cumulative":
    state_df = df.groupby("state")[metric_option].mean().reset_index()
else:
    latest_month = monthly_df["month"].max()
    temp_df = monthly_df[monthly_df["month"] == latest_month]
    state_df = temp_df.groupby("state")[metric_option].mean().reset_index()

# -------------------------------
# FIX STATE NAMES
# -------------------------------
state_df["state"] = state_df["state"].str.title().str.strip()


state_mapping = {
    # Andaman & Nicobar
    "Andaman And Nicobar": "Andaman and Nicobar Islands",
    "Andaman & Nicobar": "Andaman and Nicobar Islands",

    # Andhra
    "Andhra Pradesh": "Andhra Pradesh",

    # Arunachal
    "Arunachal Pradesh": "Arunachal Pradesh",

    # Assam
    "Assam": "Assam",

    # Bihar
    "Bihar": "Bihar",

    # Chandigarh
    "Chandigarh": "Chandigarh",

    # Chhattisgarh
    "Chhattisgarh": "Chhattisgarh",

    # Dadra & Nagar Haveli + Daman & Diu
    "Dadra And Nagar Haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "Daman And Diu": "Dadra and Nagar Haveli and Daman and Diu",

    # Delhi
    "Delhi": "NCT of Delhi",
    "New Delhi": "NCT of Delhi",

    # Goa
    "Goa": "Goa",

    # Gujarat
    "Gujarat": "Gujarat",

    # Haryana
    "Haryana": "Haryana",

    # Himachal
    "Himachal Pradesh": "Himachal Pradesh",

    # Jammu & Kashmir
    "Jammu And Kashmir": "Jammu and Kashmir",
    "Jammu & Kashmir": "Jammu and Kashmir",

    # Jharkhand
    "Jharkhand": "Jharkhand",

    # Karnataka
    "Karnataka": "Karnataka",

    # Kerala
    "Kerala": "Kerala",

    # Ladakh
    "Ladakh": "Ladakh",

    # Lakshadweep
    "Lakshadweep": "Lakshadweep",

    # Madhya Pradesh
    "Madhya Pradesh": "Madhya Pradesh",

    # Maharashtra
    "Maharashtra": "Maharashtra",

    # Manipur
    "Manipur": "Manipur",

    # Meghalaya
    "Meghalaya": "Meghalaya",

    # Mizoram
    "Mizoram": "Mizoram",

    # Nagaland
    "Nagaland": "Nagaland",

    # Odisha
    "Odisha": "Odisha",
    "Orissa": "Odisha",

    # Punjab
    "Punjab": "Punjab",

    # Rajasthan
    "Rajasthan": "Rajasthan",

    # Sikkim
    "Sikkim": "Sikkim",

    # Tamil Nadu
    "Tamil Nadu": "Tamil Nadu",

    # Telangana
    "Telangana": "Telangana",

    # Tripura
    "Tripura": "Tripura",

    # Uttar Pradesh
    "Uttar Pradesh": "Uttar Pradesh",

    # Uttarakhand
    "Uttarakhand": "Uttarakhand",
    "Uttaranchal": "Uttarakhand",

    # West Bengal
    "West Bengal": "West Bengal"
}

state_df["state"] = state_df["state"].replace(state_mapping)

# -------------------------------
# LOAD GEOJSON
# -------------------------------
with open("D0_Data_Visualization/Dashboard/india_district.geojson") as f:
    india_geojson = json.load(f)

for feature in india_geojson["features"]:
    feature["properties"]["NAME_1"] = feature["properties"]["NAME_1"].lower().strip()

# Normalize dataset
state_df["state"] = state_df["state"].str.lower().str.strip()

# -------------------------------
# PLOT
# -------------------------------
fig = px.choropleth(
    state_df,
    geojson=india_geojson,
    locations="state",
    featureidkey="properties.NAME_1",
    color=metric_option,
    color_continuous_scale="Reds",
    hover_name="state"
)

fig.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig, use_container_width=True)

# 🔥 B. TIME-SERIES SPIKE DETECTION
st.subheader("🔥 Time-Series Spike Detection")

region = st.selectbox("Select Region", monthly_df["region_key"].unique())

region_df = monthly_df[monthly_df["region_key"] == region].sort_values("month")

# Rolling mean
region_df["rolling_mean"] = region_df["activity_ratio"].rolling(3).mean()

# Z-score spike detection
mean = region_df["activity_ratio"].mean()
std = region_df["activity_ratio"].std()
region_df["z_score"] = (region_df["activity_ratio"] - mean) / (std + 1e-6)

# Spike threshold
spikes = region_df[region_df["z_score"] > 2.5]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=region_df["month"],
    y=region_df["activity_ratio"],
    mode='lines+markers',
    name="Activity Ratio"
))

fig.add_trace(go.Scatter(
    x=region_df["month"],
    y=region_df["rolling_mean"],
    mode='lines',
    name="Trend (Rolling Mean)"
))

fig.add_trace(go.Scatter(
    x=spikes["month"],
    y=spikes["activity_ratio"],
    mode='markers',
    marker=dict(color='red', size=10),
    name="Spikes (z > 2.5)"
))

st.plotly_chart(fig, use_container_width=True)


# 🔥 C. RATIO DISTRIBUTION (OUTLIER DETECTION)
st.subheader("🔥 Ratio Distribution & Outliers")

col1, col2 = st.columns(2)

with col1:
    fig = px.box(df, y="activity_ratio", title="Box Plot (Outliers)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(df, x="activity_ratio", nbins=50, title="Distribution")
    st.plotly_chart(fig, use_container_width=True)

# Highlight abnormal regions
threshold = df["anomaly_score"].quantile(0.90)

st.write(f"Top 10% anomaly threshold: {round(threshold,3)}")

abnormal_df = df[df["anomaly_score"] > threshold]

st.dataframe(abnormal_df.head(20))

# 🔥 D. DISTRICT DRILL-DOWN PANEL
st.subheader("🔥 District Drill-Down Intelligence Panel")

state_select = st.selectbox("Select State", df["state"].unique())

district_df = df[df["state"] == state_select]

district_select = st.selectbox(
    "Select District",
    district_df["district"].unique()
)

pincode_df = district_df[district_df["district"] == district_select]

# Top pincode risks
fig = px.bar(
    pincode_df.sort_values("anomaly_score", ascending=False).head(10),
    x="pincode",
    y="anomaly_score",
    title="Top Risk Pincodes"
)

st.plotly_chart(fig, use_container_width=True)

# Show detailed data
st.subheader("📋 Detailed Metrics")

st.dataframe(pincode_df.sort_values("anomaly_score", ascending=False).head(20))