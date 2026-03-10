import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

st.set_page_config(page_title="Monitoring", page_icon="🌪️", layout="wide")

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
# SIDEBAR - WITH BUTTONS AND LOGO AT BOTTOM
# --------------------------------
with st.sidebar:
    st.markdown("###  Exploring: ..📊 Monitoring")
    
    
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
    
    # This pushes everything below down
    st.markdown("<br>" * 1, unsafe_allow_html=True)
    
    # --------------------------------
    # ROBUST LOGO LOADING - MOVED INSIDE SIDEBAR
    # --------------------------------
    
    import os
    from pathlib import Path
    from PIL import Image
    import datetime
    
    # Construct the path
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


# --------------------------------
# Header
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
st.markdown("---")

st.title("📈 Monitoring")
st.markdown("**This dashboard page covers:**  1. City Details Exploration, 2. Real-time trends, 3. City-level monitoring, and  4.Correlations")

# This works everywhere (local AND cloud)
data_path = Path(__file__).parent.parent.parent / "datasets" / "dashboard_df.csv"

@st.cache_data
def load_data():
    return pd.read_csv(data_path)

df = load_data()

#CLEAN DATE COLUMN HERE 
df['date_day'] = df['date_day'].astype(str).str.split(' to ').str[0]
df['date_day'] = pd.to_datetime(df['date_day'], errors='coerce')
df = df.dropna(subset=['date_day'])

# Convert problematic column to numeric
if 'Value' in df.columns:
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    
# Create tabs for different monitoring views
tab1, tab2, tab3, tab4 = st.tabs([" 🌆 1. City Explorer", "📈 2. Trends", "🏙️ 3. City Level Monitoring", " 📐 4. Correlations"])

with tab1:
    # City Details Explorer
    st.header(" 🌆 1. City Details Explorer")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_city = st.selectbox("Select a City", sorted(df['city'].unique()))
        
        if selected_city:
            city_df = df[df['city'] == selected_city]
            
            # City metrics
            st.metric("Total Days", len(city_df))
            st.metric("Average AQI", f"{city_df['us_aqi'].mean():.1f}")
            st.metric("Average Temperature", f"{city_df['temperature_2m'].mean():.1f}°C")
            st.metric("Average PM2.5", f"{city_df['pm2_5'].mean():.1f} µg/m³")
    
    with col2:
        if selected_city:
            city_df = df[df['city'] == selected_city]
            
            # Time series for selected city
            fig = px.line(
                city_df,
                x='date_day',
                y='us_aqi',
                title=f'AQI Trend for {selected_city}',
                markers=True
            )
            
            # Add threshold lines
            fig.add_hline(y=50, line_dash="dash", line_color="green", 
                         annotation_text="Good", annotation_position="top left")
            fig.add_hline(y=100, line_dash="dash", line_color="orange", 
                         annotation_text="Moderate", annotation_position="top left")
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Trends
    st.header("📈 2. Trends Analysis")
    
    # Multi-city time series
    selected_cities_trend = st.multiselect(
        "Select Cities for Trend Comparison",
        sorted(df['city'].unique()),
        default=sorted(df['city'].unique())[:3]
    )
    
    if selected_cities_trend:
        trend_df = df[df['city'].isin(selected_cities_trend)]
        
        fig = px.line(
            trend_df,
            x='date_day',
            y='us_aqi',
            color='city',
            title='AQI Trends Comparison',
            markers=True
        )
        
        # Add range selector
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    # City Comparison
    st.header("🏙️ 3. City Level Monitoring")
    
    col1, col2 = st.columns(2)
    
    with col1:
        compare_cities = st.multiselect(
            "Select Cities",
            sorted(df['city'].unique()),
            default=sorted(df['city'].unique())[:4]
        )
        
        compare_metric = st.selectbox(
            "Compare Metric",
            ["us_aqi", "pm2_5", "temperature_2m", "humidity"]
        )
    
    if compare_cities:
        compare_df = df[df['city'].isin(compare_cities)]
        
        # Box plot comparison
        fig = px.box(
            compare_df,
            x='city',
            y=compare_metric,
            color='city',
            title=f'{compare_metric.replace("_", " ").title()} Distribution by City',
            points='all'
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    # Correlations
    st.header("📐 4. Correlations Analysis")
    
    # Select variables for correlation
    numeric_cols = [col for col in df.select_dtypes(include=['float64', 'int64']).columns 
                   if col not in ['lat', 'lon']]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        x_var = st.selectbox("X Variable", numeric_cols, index=numeric_cols.index('temperature_2m'))
    with col2:
        y_var = st.selectbox("Y Variable", numeric_cols, index=numeric_cols.index('us_aqi'))
    with col3:
        color_var = st.selectbox("Color by", ['city', 'us_aqi', 'pm2_5'])
    
    # Scatter plot with regression
    fig = px.scatter(
        df,
        x=x_var,
        y=y_var,
        color=color_var,
        trendline="ols",
        title=f'{x_var.replace("_", " ").title()} vs {y_var.replace("_", " ").title()}',
        hover_data=['city', 'date_day']
    )
    
    # Calculate correlation coefficient
    correlation = df[x_var].corr(df[y_var])
    fig.add_annotation(
        x=0.05, y=0.95,
        xref="paper", yref="paper",
        text=f"Correlation: {correlation:.3f}",
        showarrow=False,
        bgcolor="white",
        bordercolor="black",
        borderwidth=1
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation heatmap
    if st.checkbox("Show Correlation Heatmap"):
        corr_matrix = df[numeric_cols].corr()
        
        fig2 = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title='Correlation Matrix'
        )
        st.plotly_chart(fig2, use_container_width=True)

# Prediction Navigation
st.markdown("---")
st.subheader("🔮 Prediction Models")
st.write("Explore atmospheric regime clustering and AQI risk forecasting 👇")

if st.button("Go to Predictions Page", use_container_width=True):
    st.switch_page("pages/4_predictions.py")

#footnote
import datetime
st.markdown(f"""
<div style='text-align: center; color: #aaa; font-size: 0.9rem;'>
    🌱 <b>ECO 4N6 Limited</b> 🌱 © {datetime.datetime.now().year} | Environmental Intelligence | Pioneering Sustainable Forensic Techniques ⚖️
</div>
""", unsafe_allow_html=True)