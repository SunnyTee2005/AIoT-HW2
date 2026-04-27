import streamlit as st
import sqlite3
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Temperature Forecast Web App", layout="wide", initial_sidebar_state="collapsed")

# Inject Custom CSS for aesthetics as per AIoT requirements
st.markdown("""
<style>
    /* Dark Theme Optimization */
    .stApp {
        background-color: #0e1117;
        color: #e6edf3;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    .stSelectbox label {
        color: #a3b3c2;
        font-weight: 500;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

st.title("⛅ Temperature Forecast Web App")

# Function to load data from SQLite DB
@st.cache_data
def load_data():
    try:
        conn = sqlite3.connect("data.db")
        # Ensure identical column names to the screenshot: dataDate, MinT, MaxT
        df = pd.read_sql_query("SELECT regionName, dataDate, mint as MinT, maxt as MaxT FROM TemperatureForecasts", conn)
        conn.close()
        return df
    except sqlite3.OperationalError:
        return pd.DataFrame() # No data

df = load_data()

if df.empty:
    st.error("⚠️ Database 'data.db' is empty or not found. Please run `fetch_data.py` with a valid CWA_API_KEY first.")
    st.stop()

# Taiwan Regions approximate coordinates
region_coords = {
    "北部地區": [25.0330, 121.5654], # Taipei
    "中部地區": [24.1477, 120.6736], # Taichung
    "南部地區": [22.9997, 120.2270], # Tainan
    "東北部地區": [24.7523, 121.7583], # Yilan
    "東部地區": [23.9774, 121.6050], # Hualien
    "東南部地區": [22.7563, 121.1504], # Taitung
}

def get_color(temp):
    if temp < 20: return "#3182bd" # Blue
    elif 20 <= temp <= 25: return "#31a354" # Green
    elif 25 <= temp <= 30: return "#e6550d" # Orange/Yellow
    else: return "#de2d26" # Red

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("🗺️ Taiwan Region Map Tracker")
    
    dates = df["dataDate"].unique()
    selected_date = st.selectbox("Select Date for Map View", dates)
    
    map_df = df[df["dataDate"] == selected_date]
    
    m = folium.Map(location=[23.6978, 120.9605], zoom_start=7.4, tiles="CartoDB dark_matter")
    
    for idx, row in map_df.iterrows():
        region = row["regionName"]
        if region in region_coords:
            avg_temp = (row["MinT"] + row["MaxT"]) / 2
            color = get_color(avg_temp)
            
            popup_html = f"""
            <div style='font-family: Inter, sans-serif; font-size: 14px;'>
                <b>{region}</b><br>
                Date: {selected_date}<br>
                Min Temperature: {row['MinT']}°C<br>
                Max Temperature: {row['MaxT']}°C
            </div>
            """
            
            folium.CircleMarker(
                location=region_coords[region],
                radius=18,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Click for {region} Info",
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
            ).add_to(m)
            
    st_folium(m, width="100%", height=550)

with col2:
    st.subheader("📈 Temperature Data & Trends")
    regions = df["regionName"].unique()
    selected_region = st.selectbox("Select a Region", regions)
    
    region_df = df[df["regionName"] == selected_region].sort_values("dataDate")
    
    if not region_df.empty:
        st.markdown(f"**Temperature Trends for {selected_region}**")
        chart_data = region_df.set_index("dataDate")[["MinT", "MaxT"]]
        st.line_chart(chart_data, color=["#A9D6E5", "#01497C"])
        
        st.markdown(f"**Temperature Data for {selected_region}**")
        st.dataframe(region_df.reset_index(drop=True), use_container_width=True)
