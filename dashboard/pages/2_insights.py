import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# Then your headers
st.markdown('<div class="main-header">🌫️ Air Quality & Weather Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analysing the influence of weather conditions on air pollution levels</div>', unsafe_allow_html=True)
st.markdown("---")

st.title(" Insights")
st.markdown("City comparisons, detailed analysis, and AQI health guidelines")

@st.cache_data
def load_data():
    return pd.read_csv("../datasets/dashboard_df.csv")

df = load_data()

# Sidebar for city selection
with st.sidebar:
    st.header(" Filter Settings")
    
    # City selector
    all_cities = sorted(df['city'].unique())
    selected_cities = st.multiselect(
        "Select Cities for Comparison",
        all_cities,
        default=all_cities[:3] if len(all_cities) > 3 else all_cities
    )
    
    # Metric selector
    metric = st.selectbox(
        "Select Metric for Comparison",
        ["us_aqi", "pm2_5", "temperature_2m", "humidity", "wind_speed"],
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    st.markdown("---")
    st.info("Use the filters to customize the comparison view below.")

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
    "relative_humidity_2m": "mean",  # Correct column name
    "wind_speed_10m": "mean"          # Correct column name
}).round(2)

city_stats.columns = ['_'.join(col).strip() for col in city_stats.columns.values]
city_stats = city_stats.reset_index()
city_stats = city_stats.sort_values("us_aqi_mean", ascending=False)

# City Comparison Dashboard
st.header("🏙️ City Comparison Dashboard")

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
    y_values = city_stats['relative_humidity_2m_mean']  # Using correct column
    y_label = "Average Humidity (%)"
    title_metric = "Humidity"
    
elif metric == "wind_speed":
    y_values = city_stats['wind_speed_10m_mean']  # Using correct column
    y_label = "Average Wind Speed (km/h)"
    title_metric = "Wind Speed"

for idx, row in city_stats.iterrows():
    value = y_values.iloc[idx]
    
    # Color coding based on AQI only if showing AQI
    if metric == "us_aqi":
        if value <= 50:
            color = '#2ECC71'  # Green
        elif value <= 100:
            color = '#F39C12'  # Orange
        elif value <= 150:
            color = '#E74C3C'  # Red
        else:
            color = '#8B0000'  # Dark Red
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

# Detailed City Statistics
st.header(" Detailed City Statistics")

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
st.header(" AQI Information & Health Guidelines")

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

st.markdown("---")
st.info("""
**Note:** Based on US EPA AQI standards. AQI above 200 is considered "Very Unhealthy" 
and above 300 is "Hazardous". Sensitive groups include children, elderly, and 
people with respiratory or heart conditions.
""")
st.markdown("---")
