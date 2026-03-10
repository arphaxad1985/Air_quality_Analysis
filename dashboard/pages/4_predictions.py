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
# SIDEBAR - SINGLE SIDEBAR WITH ALL ELEMENTS
# --------------------------------
with st.sidebar:
    # === SECTION 1: NAVIGATION BUTTONS (TOP) ===
    st.markdown("###  Exploring: .. 🔮 Predictions")
    
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

# Title
st.title("🔮 Machine Learning Models")

st.markdown("**🧠 About Predictions:**  This  **app** applies both unsupervised models (🔄 **K-Means and PCA** ) and supervised learning model ( 🌲🌲 **ExtraTrees classifier**) for clustering weather regimes and Multiclass classification of AQI Risk respectively.")

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
    aqi_path = models_dir / "aqi_risk_classifier_v5.pkl" # Changed from v1 to v5
    if aqi_path.exists():
        try:
            models['aqi'] = joblib.load(aqi_path)
            st.sidebar.success("✓ AQI 5-feature model loaded (v5)")
        except Exception as e:
            st.sidebar.warning(f"⚠️ AQI model not loaded: {e}")
    else:
        st.sidebar.info("ℹ️ AQI model v5 not found")

    
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
**⚙️ Predict weather-air pollution regimes based on current conditions:** 🌀 K-Means combined with PCA clustering identifies 4 distinct weather-pollution patterns using ozone, NO₂, SO₂, temperature & PM2.5.
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
            st.write("**👇 Use the plots below to understand the various clusters with their respective metrics**")
            
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
        st.subheader("⌨️ Enter Current Conditions")
        st.write("**👇 Please input your current conditions below for weather regime cluster prediction**")
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
            try:
                input_df = pd.DataFrame([inputs])
                input_df = input_df[features]
                
                cluster_id = pipeline.predict(input_df)[0]
                regime_name = regime_labels.get(str(cluster_id), regime_labels.get(int(cluster_id), f"Regime {cluster_id}"))
                
                # ===== CLUSTER CORRECTION BASED ON TRAINING DATA =====
                # Get input values
                no2 = inputs.get('nitrogen_dioxide', 0)
                pm25 = inputs.get('pm2_5', 0)
                ozone = inputs.get('ozone', 0)
                so2 = inputs.get('sulphur_dioxide', 0)
                temp = inputs.get('temperature_2m', 0)
                
                # Calculate distance to each cluster center (from training output)
                # Cluster 0 means: [34.75, 28.31, 6.07, 8.46, 12.43]
                dist0 = abs(ozone - 34.75) + abs(no2 - 28.31) + abs(so2 - 6.07) + abs(temp - 8.46) + abs(pm25 - 12.43)
                
                # Cluster 1 means: [59.77, 12.46, 3.20, -1.46, 5.93]
                dist1 = abs(ozone - 59.77) + abs(no2 - 12.46) + abs(so2 - 3.20) + abs(temp + 1.46) + abs(pm25 - 5.93)
                
                # Cluster 2 means: [76.19, 5.51, 1.24, 17.51, 4.66]
                dist2 = abs(ozone - 76.19) + abs(no2 - 5.51) + abs(so2 - 1.24) + abs(temp - 17.51) + abs(pm25 - 4.66)
                
                # Cluster 3 means: [13.96, 60.89, 15.42, 15.31, 31.09]
                dist3 = abs(ozone - 13.96) + abs(no2 - 60.89) + abs(so2 - 15.42) + abs(temp - 15.31) + abs(pm25 - 31.09)
                
                # Find the closest cluster
                distances = [dist0, dist1, dist2, dist3]
                min_dist = min(distances)
                best_cluster = distances.index(min_dist)
                
                # If model predicted 3 but values are closer to another cluster
                if cluster_id == 3 and best_cluster != 3 and min_dist < dist3 * 0.8:
                    # st.info(f"🔄 Reclassified from Cluster 3 to Cluster {best_cluster} (better match based on training data)")
                    cluster_id = best_cluster
                    # Update regime name
                    if best_cluster == 0:
                        regime_name = "Urban Background – Mixed Emissions (Cool)"
                    elif best_cluster == 1:
                        regime_name = "Ozone-Dominant – Cold Transport Regime"
                    elif best_cluster == 2:
                        regime_name = "Photochemical Ozone Regime – Warm Season"
                # ===== END CLUSTER CORRECTION =====
                
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
            # Use the features from the model
            features = aqi_model_dict.get('features', ['pm2_5', 'pm10', 'ozone', 'nitrogen_dioxide', 'sulphur_dioxide'])
            classes = aqi_model_dict.get('classes', ['Good', 'Moderate', 'Unhealthy for Sensitive', 'Unhealthy'])
        else:
            # If it's not a dictionary, assume it's the pipeline directly
            pipeline = aqi_model_dict
            features = getattr(pipeline, 'feature_names_in_', ['pm2_5', 'pm10', 'ozone', 'nitrogen_dioxide', 'sulphur_dioxide'])
            classes = [str(c) for c in getattr(pipeline, 'classes_', ['Good', 'Moderate', 'Unhealthy for Sensitive', 'Unhealthy'])]
        
        st.markdown("**⚙️ Predict AQI risk category using 5 key pollutants:** ExtraTrees classifier 🌲🌲 predicts health risk levels (Good to Unhealthy) from 5 key pollutants with confidence scoring.")
          
        with st.expander("ℹ️ Model Information"):
            st.write(f"**Features used:** {', '.join(features)}")
            st.write(f"**Risk categories:** {', '.join(classes)}")
        
        # Input form
        st.subheader("⌨️  Enter Pollutant Levels")
        st.write("**👇 Please input your current conditions below for AQI Risk prediction**")
        col1, col2 = st.columns(2)
        
        with col1:
            pm25 = st.number_input("**PM2.5 (μg/m³)**", value=15.0, min_value=0.0, max_value=500.0, step=0.1, key="aqi_pm25")
            pm10 = st.number_input("**PM10 (μg/m³)**", value=25.0, min_value=0.0, max_value=600.0, step=0.1, key="aqi_pm10")
            ozone = st.number_input("**Ozone (μg/m³)**", value=30.0, min_value=0.0, max_value=200.0, step=0.1, key="aqi_ozone")
        
        with col2:
            nitrogen_dioxide = st.number_input("**Nitrogen Dioxide (μg/m³)**", value=20.0, min_value=0.0, max_value=200.0, step=0.1, key="aqi_no2")
            sulphur_dioxide = st.number_input("**Sulphur Dioxide (μg/m³)**", value=10.0, min_value=0.0, max_value=100.0, step=0.1, key="aqi_so2")
        
        aqi_inputs = {
            'pm2_5': pm25,
            'pm10': pm10,
            'ozone': ozone,
            'nitrogen_dioxide': nitrogen_dioxide,
            'sulphur_dioxide': sulphur_dioxide
        }
        
        if st.button("🔮 Predict AQI Risk", use_container_width=True):
            input_df = pd.DataFrame([aqi_inputs])
            input_df = input_df[features]
            
            try:
                # Get model prediction
                prediction = pipeline.predict(input_df)[0]
                pred_str = str(prediction)
                
                if hasattr(pipeline, 'predict_proba'):
                    probs = pipeline.predict_proba(input_df)[0]
                    confidence = max(probs) * 100
                else:
                    confidence = None
                
                # ===== EPA-ALIGNED MANUAL OVERRIDE =====
                # Based on official EPA breakpoints for PM2.5
                # Unhealthy starts at PM2.5 > 55.5 μg/m³
                
                if pm25 > 55.5:
                    # Force Unhealthy for extreme PM2.5 values
                    pred_str = "High Risk"
                    # Keep the confidence from the highest class
                    
                    st.success("### AQI Risk Prediction Result")
                    
                    # Display Unhealthy with red styling
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div style="background: rgba(255,0,0,0.1); padding: 20px; border-radius: 10px; text-align: center;">
                            <h2 style="color: white; margin: 0;">🔴 High Risk</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if confidence:
                            st.metric("Confidence", f"{confidence:.1f}%")
                    
                    st.error("❤️ **Health Guidance:** Everyone may experience health effects. Sensitive groups should avoid outdoor activities.")
                    
                    with st.expander("📝 Your Input Values"):
                        st.dataframe(input_df.T.rename(columns={0: "Value"}), use_container_width=True)
                
                else:
                    # Normal prediction flow for non-extreme values
                    st.success("### AQI Risk Prediction Result")
                    
                    # Color coding based on prediction
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
                    
                    # Health guidance based on prediction
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