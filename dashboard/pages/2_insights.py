import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Insights", page_icon="🌪️", layout="wide")

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
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #85bb65 0%, #2e7d32 100%);
        backdrop-filter: blur(10px);
        border-right: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Make sidebar text white for better contrast */
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

# Hide automatic page navigation by streamlit
st.markdown("""
<style>
    /* Hide the entire page navigation section */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------
# HEADER
# --------------------------------
st.markdown('<div class="main-header">💨 Air Quality & Weather Analysis Dashboard🌫️</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Analysing the influence of weather conditions on air pollution levels</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div style="text-align: center; color: black; font-size: 0.9rem; margin-top: -10px; margin-bottom: 10px;">⚖️ © ECO 4N6 Limited. All rights reserved. 🌱</div>',
    unsafe_allow_html=True
)

st.title(" 🔎 Insights")
st.markdown("**This dashboard page covers:**  1.City by city comparisons against various polution metrics:  2. Detailed city statistics and 3. AQI Information and health guidelines👇")

# Load data
data_path = Path(__file__).parent.parent.parent / "datasets" / "dashboard_df.csv"

@st.cache_data
def load_data():
    return pd.read_csv(data_path)

df = load_data()

# --------------------------------
# SIDEBAR - SINGLE SIDEBAR WITH ALL ELEMENTS
# --------------------------------
with st.sidebar:
    # === SECTION 1: NAVIGATION BUTTONS (TOP) ===
    st.markdown("###  Exploring: .. 🔎 Insights")
    
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("air_quality.py")
    
    if st.button("📊 Overview", use_container_width=True):
        st.switch_page("pages/1_overview.py")
    
    if st.button("🔎 Insights", use_container_width=True):
        st.switch_page("pages/2_insights.py")
    
    if st.button("📈 Monitoring", use_container_width=True):
        st.switch_page("pages/3_monitoring.py")
    
    if st.button("🔮 Predictions", use_container_width=True):
        st.switch_page("pages/4_predictions.py")
    
    
    # === SECTION 2: FILTER SETTINGS (MIDDLE) ===
    st.header(" Filter Settings")
    
    all_cities = sorted(df['city'].unique())
    selected_cities = st.multiselect(
        "Select Cities for Comparison",
        all_cities,
        default=all_cities[:3] if len(all_cities) > 3 else all_cities
    )
    
    metric = st.selectbox(
        "Select Metric for Comparison",
        ["us_aqi", "pm2_5", "temperature_2m", "humidity", "wind_speed"],
        format_func=lambda x: x.replace('_', ' ').title()
    )
    

    st.info("Use filters above to customize comparison views.")
    
    # === SECTION 3: LOGO AT BOTTOM ===
    # Push logo to bottom with spacer
    st.markdown("<br>" * 0, unsafe_allow_html=True)
    
    import os
    from pathlib import Path
    from PIL import Image
    import datetime
    
    logo_path = Path(__file__).parent.parent / "logo.png"
    
    if logo_path.exists():
        try:
            logo = Image.open(logo_path)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(logo, width=150)
                st.markdown(f"""
                <div style='text-align: center; margin-top: 5px;'>
                    <span style='color: #E0FFFF; font-size: 0.7rem;'>
                        ⚖️ © {datetime.datetime.now().year} ECO 4N6 Limited
                    </span>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown("**ECO4N6**")
            st.caption(f"⚖️ © {datetime.datetime.now().year}")
    else:
        st.markdown(f"""
        <div style='text-align: center; padding: 10px;'>
            <div style='font-size: 1.2rem; font-weight: bold; color: #E0FFFF;'>ECO4N6</div>
            <div style='font-size: 0.8rem; font-style: italic; color: #FFE4E1;'>Pioneering Sustainable<br>Forensic Techniques</div>
            <div style='font-size: 0.7rem; color: #FFE4E1; margin-top: 5px;'>⚖️ © {datetime.datetime.now().year}</div>
        </div>
        """, unsafe_allow_html=True)

# Calculate city statistics
if selected_cities:
    filtered_df = df[df['city'].isin(selected_cities)]
else:
    filtered_df = df
    selected_cities = all_cities

city_stats = filtered_df.groupby("city").agg({
    "us_aqi": ["mean", "min", "max", "std"],
    "pm2_5": "mean",
    "temperature_2m": "mean",
    "relative_humidity_2m": "mean",
    "wind_speed_10m": "mean"
}).round(2)

city_stats.columns = ['_'.join(col).strip() for col in city_stats.columns.values]
city_stats = city_stats.reset_index()
city_stats = city_stats.sort_values("us_aqi_mean", ascending=False)

# City Comparison Dashboard
st.header("🏙️ 1. City Comparison Dashboard")
st.markdown("**⏪ Use filter settings on the side pannel for customized city comparisons against polution metrics..⏪**")

# Create comparison chart based on selected metric
fig = go.Figure()

# Determine which metric to plot
if metric == "us_aqi":
    y_values = city_stats['us_aqi_mean']
    y_label = "Average AQI"
    title_metric = "AQI"
    
elif metric == "pm2_5":
    y_values = city_stats['pm2_5_mean']
    y_label = "Average PM2.5 (µg/m³)"
    title_metric = "PM2.5"
    
elif metric == "temperature_2m":
    y_values = city_stats['temperature_2m_mean']
    y_label = "Average Temperature (°C)"
    title_metric = "Temperature"
    
elif metric == "humidity":
    y_values = city_stats['relative_humidity_2m_mean']
    y_label = "Average Humidity (%)"
    title_metric = "Humidity"
    
elif metric == "wind_speed":
    y_values = city_stats['wind_speed_10m_mean']
    y_label = "Average Wind Speed (km/h)"
    title_metric = "Wind Speed"

for idx, row in city_stats.iterrows():
    value = y_values.iloc[idx]
    
    # Color coding based on AQI only if showing AQI
    if metric == "us_aqi":
        if value <= 50:
            color = '#2ECC71'
        elif value <= 100:
            color = '#F39C12'
        elif value <= 150:
            color = '#E74C3C'
        else:
            color = '#8B0000'
    else:
        # Use a blue gradient for non-AQI metrics
        color = px.colors.sequential.Blues[3 + (idx % 5)]
    
    # Create hover text with all available data
    hover_text = (
        f"<b>{row['city']}</b><br><br>"
        f"{y_label}: {value:.1f}<br>"
        f"PM2.5: {row['pm2_5_mean']:.1f} µg/m³<br>"
        f"Temperature: {row['temperature_2m_mean']:.1f}°C<br>"
        f"Humidity: {row['relative_humidity_2m_mean']:.1f}%<br>"
        f"Wind Speed: {row['wind_speed_10m_mean']:.1f} km/h<br>"
        "<extra></extra>"
    )
    
    fig.add_trace(go.Bar(
        x=[row['city']],
        y=[value],
        marker_color=color,
        hovertemplate=hover_text,
        text=f"{value:.1f}",
        textposition='outside'
    ))

# Add threshold lines only for AQI
if metric == "us_aqi":
    fig.add_hline(y=50, line_dash="dash", line_color="blue",
                  annotation_text="Good Air Quality", annotation_position="top left")
    fig.add_hline(y=100, line_dash="dot", line_color="orange",
                  annotation_text="Moderate", annotation_position="top left")

fig.update_layout(
    title=f"Average {title_metric} by City",
    xaxis_title="City",
    yaxis_title=y_label,
    showlegend=False,
    height=500,
    xaxis_tickangle=-45
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("**👇 Please scroll down for more details.**")
st.markdown("""
<style>
@keyframes bounce {
    0%, 100% {transform: translateY(0);}
    50% {transform: translateY(10px);}
}
.bounce-arrow {
    animation: bounce 1.5s infinite;
    text-align: center;
    font-size: 2rem;
    color: #888;
}
</style>
<div class='bounce-arrow'>⬇️</div>
""", unsafe_allow_html=True)

# Detailed City Statistics
st.header(" 📌 2. Detailed City Statistics")

# Create formatted table
display_df = city_stats.copy()
display_df.columns = [col.replace('_', ' ').title() for col in display_df.columns]

# Add color coding
def color_aqi(val):
    if val <= 50:
        color = '#d4edda'
    elif val <= 100:
        color = '#fff3cd'
    elif val <= 150:
        color = '#f8d7da'
    else:
        color = '#721c24'
    return f'background-color: {color}; color: {"white" if val > 150 else "black"}'

styled_df = display_df.style.map(color_aqi, subset=['Us Aqi Mean']).format({
    'Us Aqi Mean': '{:.1f}',
    'Us Aqi Min': '{:.1f}',
    'Us Aqi Max': '{:.1f}',
    'Us Aqi Std': '{:.2f}',
    'Pm2_5 Mean': '{:.1f}',
    'Temperature 2M Mean': '{:.1f}',
    'Relative Humidity 2M Mean': '{:.1f}',
    'Wind Speed 10M Mean': '{:.1f}'
})

st.dataframe(styled_df, use_container_width=True)

# Download button
csv = city_stats.to_csv(index=False)
st.download_button(
    label=" Download Selected Cities Data",
    data=csv,
    file_name="city_aqi_comparison.csv",
    mime="text/csv",
    use_container_width=True
)

# AQI Information Panel
st.markdown("---")
st.header(" 🌬️🫁 Air Quality Index (AQI) Information & Health Guidelines 🩺")


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    ### 🟢 **Good (0-50)**
    **Air Quality:** Satisfactory  
    **Health Impact:** Minimal risk  
    **Action:** Normal outdoor activities
    """)

with col2:
    st.markdown("""
    ### 🟡 **Moderate (51-100)**
    **Air Quality:** Acceptable  
    **Health Impact:** Sensitive groups affected  
    **Action:** Reduce prolonged exertion
    """)

with col3:
    st.markdown("""
    ### 🟠 **Unhealthy for Sensitive Groups (101-150)**
    **Air Quality:** Unhealthy for some  
    **Health Impact:** Heart/lung disease risks  
    **Action:** Limit outdoor activities
    """)

with col4:
    st.markdown("""
    ### 🔴 **Unhealthy (151-200)**
    **Air Quality:** Unhealthy  
    **Health Impact:** Everyone affected  
    **Action:** Avoid outdoor activities
    """)


st.markdown("""
<div style="
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    padding: 25px;
    border-radius: 15px;
    border: 3px solid #4fc3f7;
    box-shadow: 0 8px 16px rgba(0, 105, 148, 0.4);
    margin: 20px 0;
">
    <h4 style="color: white; margin-top: 0; font-size: 1.4rem; text-align: center; border-bottom: 2px solid #4fc3f7; padding-bottom: 10px;">
        ⚠️ HEALTH & SAFETY INFORMATION ⚠️
    </h4>
    <div style="display: flex; align-items: center; gap: 20px;">
        <div style="font-size: 3rem; background: rgba(79, 195, 247, 0.2); padding: 15px; border-radius: 50%;">🏥</div>
        <div style="flex: 1;">
            <p style="color: white; font-size: 1.1rem; margin: 5px 0;">
                <strong>🔴 AQI > 200:</strong> <span style="background: #ff4d4d; color: white; padding: 3px 10px; border-radius: 20px;">Very Unhealthy</span>
            </p>
            <p style="color: white; font-size: 1.1rem; margin: 5px 0;">
                <strong>🟣 AQI > 300:</strong> <span style="background: #9c27b0; color: white; padding: 3px 10px; border-radius: 20px;">Hazardous</span>
            </p>
            <p style="color: white; font-size: 1.1rem; margin: 10px 0 0 0; background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
                👥 <strong>Sensitive groups:</strong> children, elderly, respiratory/heart conditions
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

#footnote
import datetime
st.markdown(f"""
<div style='text-align: center; color: #aaa; font-size: 0.9rem;'>
    🌱 <b>ECO 4N6 Limited</b> 🌱 © {datetime.datetime.now().year} | Environmental Intelligence | Pioneering Sustainable Forensic Techniques ⚖️
</div>
""", unsafe_allow_html=True)