import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Air Quality Predictions",
    page_icon="🌪️",
    layout="wide"
)

# --------------------------------
# Custom CSS (same as other pages)
# --------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    h1, h2, h3 {
        color: white !important;
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

# Title
st.title("🔮 Machine Learning Models")

st.markdown("**About Predictions** — This app applies both unsupervised models (K-Means and PCA) and supervised learning model (ExtraTrees classifier) for clustering weather regimes and Multiclass classification of AQI Risk respectively.")

# Load models from central location (works everywhere)
@st.cache_resource
def load_models():
    models = {}
    
    # Path to models folder - works locally AND on Streamlit Cloud
    models_dir = Path(__file__).parent.parent.parent / "models"
    
    # Load cluster model (new 5-feature version)
    cluster_path = models_dir / "weather_regime_cluster_v1.pkl"
    if cluster_path.exists():
        try:
            models['cluster'] = joblib.load(cluster_path)
            st.sidebar.success("✓ Weather cluster model loaded")
        except Exception as e:
            st.sidebar.error(f"Error loading cluster model: {e}")
    else:
        st.sidebar.error(f"❌ Cluster model not found at {cluster_path}")
    
    # Load AQI model (new 5-feature version)
    aqi_path = models_dir / "aqi_risk_classifier_v1.pkl"
    if aqi_path.exists():
        try:
            models['aqi'] = joblib.load(aqi_path)
            st.sidebar.success("✓ AQI 5-feature model loaded")
        except Exception as e:
            st.sidebar.warning(f"⚠️ AQI model not loaded: {e}")
    else:
        st.sidebar.info("ℹ️ AQI model not found")
    
    return models

# CALL THE FUNCTION
models = load_models()

# Check if models are available
if not models:
    st.error("× No prediction models found. Please train the models first.")
    st.stop()

# Create tabs for different predictions
tab1, tab2 = st.tabs(["🌪️ Weather Regime Clustering", "🌫️ AQI Risk Prediction"])

# ====================================================
# TAB 1: WEATHER REGIME CLUSTERING
# ====================================================
with tab1:
    st.header("🌪️ Weather-Air Pollution Regime Clustering")
    st.markdown("""
**Predict weather-air pollution regimes based on current conditions** — K-Means combined with PCA clustering identifies 4 distinct weather-pollution patterns using ozone, NO₂, SO₂, temperature & PM2.5.
""")
    
    if 'cluster' not in models:
        st.warning("Weather cluster model not available")
    else:
        cluster_model = models['cluster']
        
        # Get model components - handle both dictionary and pipeline
        if isinstance(cluster_model, dict):
            pipeline = cluster_model.get('pipeline')
            features = cluster_model.get('features', [])
            regime_labels = cluster_model.get('regime_labels', {})
            cluster_profiles = cluster_model.get('cluster_profiles', {})
        else:
            # If it's a pipeline directly
            pipeline = cluster_model
            features = getattr(cluster_model, 'feature_names_in_', 
                              ['ozone', 'nitrogen_dioxide', 'sulphur_dioxide', 'temperature_2m', 'pm2_5'])
            regime_labels = {0: "Cluster 0", 1: "Cluster 1", 2: "Cluster 2", 3: "Cluster 3"}
            cluster_profiles = {}
        
        # Visualization of all 4 clusters
        if cluster_profiles:
            st.subheader("📊 Cluster Comparison - All Regimes")
            
            # Prepare data for visualization
            viz_data = []
            for cluster_id in range(4):
                if cluster_id in cluster_profiles:
                    profile = cluster_profiles[cluster_id]
                    regime_name = regime_labels.get(str(cluster_id), regime_labels.get(cluster_id, f"Regime {cluster_id}"))
                    
                    for feature in features:
                        mean_val = profile.get(f"{feature}_mean", 0)
                        viz_data.append({
                            "Cluster": f"Cluster {cluster_id}\n({regime_name})",
                            "Feature": feature.replace('_', ' ').title(),
                            "Value": mean_val
                        })
            
            if viz_data:
                viz_df = pd.DataFrame(viz_data)
                
                fig = px.bar(
                    viz_df,
                    x="Cluster",
                    y="Value",
                    color="Feature",
                    barmode="group",
                    title="Average Feature Values by Cluster",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    text_auto='.1f'
                )
                
                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="Average Value",
                    legend_title="Features",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis=dict(tickfont=dict(color='white')),
                    yaxis=dict(tickfont=dict(color='white'), title_font=dict(color='white')),
                    legend=dict(font=dict(color='white'), bgcolor='rgba(0,0,0,0.5)'),
                    height=500
                )
                
                fig.update_traces(textfont_color='white')
                st.plotly_chart(fig, use_container_width=True)
        
        # Show model info
        with st.expander("📊 Model Information"):
            st.write(f"**Features used:** {', '.join(features)}")
            st.write(f"**Number of clusters:** {len(regime_labels)}")
        
        # Create input form
        st.subheader("📊 Enter Current Conditions")
        
        col1, col2 = st.columns(2)
        inputs = {}
        
        for i, feature in enumerate(features):
            with col1 if i % 2 == 0 else col2:
                if feature == "temperature_2m":
                    default_val, min_val, max_val = 20.0, -10, 40
                elif feature == "pm2_5":
                    default_val, min_val, max_val = 25.0, 0, 500
                elif "dioxide" in feature or feature == "ozone":
                    default_val, min_val, max_val = 30.0, 0, 200
                else:
                    default_val, min_val, max_val = 25.0, 0, 100
                
                inputs[feature] = st.number_input(
                    label=f"**{feature.replace('_', ' ').title()}**",
                    value=float(default_val),
                    min_value=float(min_val),
                    max_value=float(max_val),
                    step=0.1,
                    format="%.1f",
                    key=f"cluster_input_{feature}"
                )
        
        # Predict button
        if st.button("🔮 Predict Weather Regime", use_container_width=True):
            input_df = pd.DataFrame([inputs])
            input_df = input_df[features]
            
            try:
                cluster_id = pipeline.predict(input_df)[0]
                regime_name = regime_labels.get(str(cluster_id), regime_labels.get(int(cluster_id), f"Regime {cluster_id}"))
                
                st.success("### Prediction Result")
                
                res_col1, res_col2 = st.columns([1, 2])
                
                with res_col1:
                    st.metric("Cluster", int(cluster_id))
                
                with res_col2:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
                        <p style="color: #bbb; font-size: 13px; margin: 0;">Weather Regime</p>
                        <p style="color: white; font-size: 15px; font-weight: 600; margin: 0;">{regime_name}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Health impact information
                cluster_health_info = {
                    0: {"icon": "🟡", "title": "WHO Concern", "description": "Moderate urban pollution. Meets UK limits but not WHO health standards."},
                    1: {"icon": "🟡", "title": "WHO Concern", "description": "Low pollution overall. Slight ozone-related respiratory risk."},
                    2: {"icon": "🟢", "title": "Compliant (Seasonal Ozone Watch)", "description": "Warm weather ozone pattern. Sensitive groups may feel breathing effects."},
                    3: {"icon": "🔴", "title": "Health Risk", "description": "High pollution episode. Increased heart and lung health risk."}
                }
                
                info = cluster_health_info.get(int(cluster_id), {"icon": "⚪", "title": "Unknown", "description": ""})
                
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <h4 style="color: white; margin: 0 0 5px 0;">{info['icon']} Health Impact: {info['title']}</h4>
                    <p style="color: #ddd; margin: 0;">{info['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if int(cluster_id) in [0, 1]:
                    st.info("ℹ️ **UK vs WHO:** Meets UK standards but exceeds WHO guidelines.")
                
                # Show input values
                with st.expander("📝 Your Input Values"):
                    st.dataframe(input_df.T.rename(columns={0: "Value"}), use_container_width=True)
                    
            except Exception as e:
                st.error(f"Error making prediction: {e}")

# ====================================================
# TAB 2: AQI RISK PREDICTION
# ====================================================
with tab2:
    st.header("🌫️ Air Quality Index (AQI) Risk Category Prediction")
    
    if 'aqi' not in models:
        st.warning("⚠️ AQI risk model not available. Please train the model first.")
        
        # Fallback option (keep your existing fallback code here)
        # ...
        
    else:
        # The AQI model is a dictionary (like the cluster model)
        aqi_model_dict = models['aqi']
        
        # Extract the pipeline from the dictionary
        if isinstance(aqi_model_dict, dict) and 'pipeline' in aqi_model_dict:
            pipeline = aqi_model_dict['pipeline']
            features = aqi_model_dict.get('features', ['pm2_5', 'pm10', 'no2', 'so2', 'o3'])
            classes = aqi_model_dict.get('classes', ['Good', 'Moderate', 'Unhealthy for Sensitive', 'Unhealthy'])
        else:
            # If it's not a dictionary, assume it's the pipeline directly
            pipeline = aqi_model_dict
            features = getattr(pipeline, 'feature_names_in_', ['pm2_5', 'pm10', 'no2', 'so2', 'o3'])
            classes = [str(c) for c in getattr(pipeline, 'classes_', ['Good', 'Moderate', 'Unhealthy for Sensitive', 'Unhealthy'])]
        
        st.markdown("**Predict AQI risk category using 5 key pollutants:** ExtraTrees classifier predicts health risk levels (Good to Unhealthy) from 5 key pollutants with confidence scoring.")
          
        with st.expander("ℹ️ Model Information"):
            st.write(f"**Features used:** {', '.join(features)}")
            st.write(f"**Risk categories:** {', '.join(classes)}")
        
        # Input form
        st.subheader("📊 Enter Pollutant Levels")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pm25 = st.number_input("**PM2.5 (μg/m³)**", value=15.0, min_value=0.0, max_value=500.0, step=0.1, key="aqi_pm25")
            pm10 = st.number_input("**PM10 (μg/m³)**", value=25.0, min_value=0.0, max_value=600.0, step=0.1, key="aqi_pm10")
            no2 = st.number_input("**NO₂ (μg/m³)**", value=20.0, min_value=0.0, max_value=400.0, step=0.1, key="aqi_no2")
        
        with col2:
            so2 = st.number_input("**SO₂ (μg/m³)**", value=10.0, min_value=0.0, max_value=300.0, step=0.1, key="aqi_so2")
            o3 = st.number_input("**O₃ (μg/m³)**", value=50.0, min_value=0.0, max_value=300.0, step=0.1, key="aqi_o3")
        
        aqi_inputs = {
            'pm2_5': pm25,
            'pm10': pm10,
            'no2': no2,
            'so2': so2,
            'o3': o3
        }
        
        if st.button("🔮 Predict AQI Risk", use_container_width=True):
            input_df = pd.DataFrame([aqi_inputs])
            input_df = input_df[features]
            
            try:
                prediction = pipeline.predict(input_df)[0]
                pred_str = str(prediction)
                
                if hasattr(pipeline, 'predict_proba'):
                    probs = pipeline.predict_proba(input_df)[0]
                    confidence = max(probs) * 100
                else:
                    confidence = None
                
                st.success("### AQI Risk Prediction Result")
                
                # Color coding
                if 'Good' in pred_str:
                    color, bg = "🟢", "rgba(0,255,0,0.1)"
                elif 'Moderate' in pred_str:
                    color, bg = "🟡", "rgba(255,255,0,0.1)"
                elif 'Sensitive' in pred_str:
                    color, bg = "🟠", "rgba(255,165,0,0.1)"
                else:
                    color, bg = "🔴", "rgba(255,0,0,0.1)"
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div style="background: {bg}; padding: 20px; border-radius: 10px; text-align: center;">
                        <h2 style="color: white; margin: 0;">{color} {pred_str}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if confidence:
                        st.metric("Confidence", f"{confidence:.1f}%")
                
                # Health guidance
                if 'Good' in pred_str:
                    st.info("💚 **Health Guidance:** Air quality is satisfactory. Little or no risk.")
                elif 'Moderate' in pred_str:
                    st.info("💛 **Health Guidance:** Acceptable air quality. Unusually sensitive people should limit outdoor activities.")
                elif 'Sensitive' in pred_str:
                    st.warning("🧡 **Health Guidance:** Sensitive groups may experience health effects.")
                else:
                    st.error("❤️ **Health Guidance:** Everyone may experience health effects.")
                
                with st.expander("📝 Your Input Values"):
                    st.dataframe(input_df.T.rename(columns={0: "Value"}), use_container_width=True)
                    
            except Exception as e:
                st.error(f"Error: {e}")
                st.write("Debug - Model type:", type(pipeline))
                
#footnote
import datetime
st.markdown(f"""
<div style='text-align: center; color: #aaa; font-size: 0.9rem;'>
    🌱 <b>ECO 4N6 Limited</b> 🌱 © {datetime.datetime.now().year} | Environmental Intelligence | Pioneering Sustainable Forensic Techniques ⚖️
</div>
""", unsafe_allow_html=True)