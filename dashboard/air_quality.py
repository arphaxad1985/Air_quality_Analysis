import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------
# Page configuration
# --------------------------------
st.set_page_config(
    page_title="Air Quality & Weather Dashboard",
    page_icon="🌪️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------
# Styling - Elegant Red with Sea Blue Accents
# --------------------------------
st.markdown("""
<style>
    /* Main background - Soft red gradient */
    .stApp {
        background: linear-gradient(135deg, #C41E3A 0%, #A52A2A 100%);
        background-attachment: fixed;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.6rem;
        color: white !important;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        letter-spacing: 1px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #FFE4E1 !important;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    /* Sidebar - Sea Blue */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #006994 0%, #0077BE 100%);
        backdrop-filter: blur(10px);
        border-right: 1px solid #00BFFF;
    }
    
    /* Sidebar text - White for maximum visibility */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: white !important;
        font-weight: 500;
        letter-spacing: 0.3px;
    }
    
    /* Sidebar header */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #E0FFFF !important;
        border-bottom: 2px solid #87CEEB;
        padding-bottom: 10px;
    }
    
    /* Sidebar select boxes - Sea blue theme */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid #87CEEB;
        border-radius: 8px;
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: #E0FFFF;
    }
    
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] option {
        background: #006994;
        color: white;
    }
    
    /* Sidebar radio/checkbox */
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stCheckbox label {
        color: white !important;
    }
    
    /* Navigation Buttons - Sea Blue */
    .stButton button {
        background: linear-gradient(135deg, #006994 0%, #0077BE 100%);
        color: white;
        border: 2px solid #87CEEB;
        border-radius: 25px;
        padding: 12px 20px;
        font-weight: 600;
        font-size: 16px;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        text-transform: uppercase;
    }
    
    .stButton button:hover {
        transform: translateY(-3px);
        background: linear-gradient(135deg, #0077BE 0%, #0099FF 100%);
        border-color: #E0FFFF;
        box-shadow: 0 6px 12px rgba(0, 105, 148, 0.4);
        color: white;
    }
    
    .stButton button:active {
        transform: translateY(-1px);
        box-shadow: 0 3px 8px rgba(0, 105, 148, 0.4);
    }
    
    /* Metric cards styling */
    [data-testid="stMetricValue"] {
        color: white !important;
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(5px);
        font-size: 1.8rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #FFE4E1 !important;
        font-size: 1rem !important;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    
    /* Info box - Dashboard Structure - Sea Blue with white text */
    .stAlert {
        background: linear-gradient(135deg, #006994 0%, #0077BE 100%) !important;
        border-radius: 15px;
        border-left: 5px solid #87CEEB;
        color: white !important;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    /* Style the text inside the info box */
    .stAlert p, .stAlert ul, .stAlert li, .stAlert span {
        color: white !important;
        font-weight: 400;
    }
    
    /* Make bullet points white */
    .stAlert ul li {
        color: white !important;
    }
    
    /* Headers inside info box */
    .stAlert strong {
        color: #E0FFFF !important;
        font-weight: 600;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        letter-spacing: 0.5px;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(205, 92, 92, 0.3) !important;
        border-width: 2px;
        border-radius: 2px;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(0, 105, 148, 0.3);
        border-radius: 20px;
        padding: 5px;
        border: 1px solid #87CEEB;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: white !important;
        font-weight: 500;
        border-radius: 15px;
        padding: 8px 20px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(135, 206, 235, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #006994 0%, #0077BE 100%) !important;
        color: white !important;
    }
    
    /* Caption text */
    .stCaption {
        color: #FFE4E1 !important;
        opacity: 0.9;
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

st.markdown("---")

# --------------------------------
# Navigation
# --------------------------------
st.subheader("📋 Navigation")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Overview", use_container_width=True):
        st.switch_page("pages/1_overview.py")

with col2:
    if st.button("Insights", use_container_width=True):
        st.switch_page("pages/2_insights.py")

with col3:
    if st.button("Monitoring", use_container_width=True):
        st.switch_page("pages/3_monitoring.py")

with col4:
    if st.button("Predictions", use_container_width=True):
        st.switch_page("pages/4_predictions.py")

st.markdown("---")

# --------------------------------
# Data preview (SAFE LOADER)
# --------------------------------
data_path = Path(__file__).parent.parent / "datasets" / "dashboard_df.csv"

@st.cache_data
def load_preview():
    return pd.read_csv(data_path)

df = load_preview()

#  CLEAN DATE COLUMN HERE 
df['date_day'] = df['date_day'].astype(str).str.split(' to ').str[0]
df['date_day'] = pd.to_datetime(df['date_day'], errors='coerce')
df = df.dropna(subset=['date_day'])

# --------------------------------
# Quick KPIs
# --------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Cities", df["city"].nunique())

with col2:
    st.metric("Records", f"{len(df):,}")

with col3:
    st.metric("Average AQI", f"{df['us_aqi'].mean():.1f}")

# Date metrics
col4, col5 = st.columns(2)

with col4:
    st.metric(
        "Start Date",
        pd.to_datetime(df['date_day']).min().strftime('%Y-%m-%d')
    )

with col5:
    st.metric(
        "End Date",
        pd.to_datetime(df['date_day']).max().strftime('%Y-%m-%d')
    )

st.markdown("---")

st.info("""
**Dashboard Structure**
- **Overview**: Dataset preview, statistics, and summary charts (visualizations)  
- **Insights**: City-by-city comparisons, detailed analysis and AQI health interpretation.  
- **Monitoring**: Trends, correlations, city level exploration and comparison (Visualizations).  
- **Predictions**: Weather regime clustering and AQI risk forecasting  
""")

st.caption("**Use the navigation buttons above or the sidebar to explore pages.**")