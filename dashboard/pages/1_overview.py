import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="Overview", page_icon="🌪️", layout="wide")

# --------------------------------
# Custom CSS for background
# --------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    h1, h2, h3 {
        color: orange !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] {
        color: white !important;
        background: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 10px;
        
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #85bb65 0%, #2e7d32 100%);
        backdrop-filter: blur(10px);
        border-right: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Optional: Make sidebar text white for better contrast */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for headers
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .sub-header {
        font-size: 1.2rem;
        color: #e0e0e0;
        text-align: center;
        margin-bottom: 1rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------
# Header
# --------------------------------
st.markdown('<div class="main-header">🌫️ Air Quality & Weather Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Analysing the influence of weather conditions on air pollution levels</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div style="text-align: center; color: black; font-size: 0.9rem; margin-top: -10px; margin-bottom: 10px;">⚖️ © ECO 4N6 Limited. All rights reserved. 🌱</div>',
    unsafe_allow_html=True
)
st.markdown("---")

st.title(" 📊 The Overview")
st.markdown("**Please scroll down for:** 1.Dataset preview, 2 Basic statistics, and 3.Fundamental visualizations")

# This works everywhere (local AND cloud)
data_path = Path(__file__).parent.parent.parent / "datasets" / "dashboard_df.csv"

@st.cache_data
def load_data():
    return pd.read_csv(data_path)

df = load_data()

# Dataset Preview
st.header("1.Dataset Preview")
with st.expander("View Full Dataset", expanded=False):
    st.dataframe(df, use_container_width=True)
    
# Basic Statistics
st.header("2.Basic Statistics")
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Quick Stats")
    stats_data = {
        "Metric": ["Total Records", "Cities", "Date Range", "Avg AQI", "Avg Temp", "Avg PM2.5"],
        "Value": [
            len(df),
            df["city"].nunique(),
            f"{df['date_day'].min()[:10]} to {df['date_day'].max()[:10]}",
            f"{df['us_aqi'].mean():.1f}",
            f"{df['temperature_2m'].mean():.1f}°C",
            f"{df['pm2_5'].mean():.1f} µg/m³"
        ]
    }
    st.table(pd.DataFrame(stats_data))

with col2:
    st.subheader("Numerical Summary")
    st.dataframe(df.describe(), use_container_width=True)

# Basic Visualizations
st.header("3.Basic Visualizations")

# AQI Distribution
st.subheader("Average Air Quality Index (AQI) by City")
city_aqi_mean = df.groupby("city")["us_aqi"].mean().sort_values(ascending=False)

# Create plot with matplotlib
fig, ax = plt.subplots(figsize=(12, 6))
colors = ['red' if val > 100 else 'orange' if val > 50 else 'green' 
          for val in city_aqi_mean.values]
bars = ax.bar(city_aqi_mean.index, city_aqi_mean.values, color=colors, edgecolor='black')

ax.axhline(y=50, color='blue', linestyle='--', linewidth=2, 
           label='Good Air Quality (AQI ≤ 50)')
ax.axhline(y=100, color='orange', linestyle='--', linewidth=2, 
           label='Moderate (AQI ≤ 100)', alpha=0.5)

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{height:.1f}', ha='center', va='bottom', fontsize=9)

ax.set_ylabel('Mean US AQI')
ax.set_xlabel('City')
ax.set_xticks(range(len(city_aqi_mean.index)))
ax.set_xticklabels(city_aqi_mean.index, rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()

st.pyplot(fig)

# Additional simple visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("AQI Distribution")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.hist(df['us_aqi'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    ax2.set_xlabel('US AQI')
    ax2.set_ylabel('Frequency')
    ax2.axvline(x=50, color='red', linestyle='--', label='Good Threshold')
    ax2.axvline(x=100, color='orange', linestyle='--', label='Moderate Threshold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

with col2:
    st.subheader("Temperature vs AQI")
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    scatter = ax3.scatter(df['temperature_2m'], df['us_aqi'], 
                         c=df['us_aqi'], cmap='RdYlGn_r', alpha=0.6, s=20)
    ax3.set_xlabel('Temperature (°C)')
    ax3.set_ylabel('US AQI')
    ax3.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax3, label='AQI')
    st.pyplot(fig3)

#footnote
import datetime
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #aaa; font-size: 0.9rem;'>
    🌱 <b>ECO 4N6 Limited</b> 🌱 © {datetime.datetime.now().year} | Environmental Intelligence | Pioneering Sustainable Forensic Techniques ⚖️
</div>
""", unsafe_allow_html=True)
