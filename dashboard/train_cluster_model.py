"""
Train Weather-Air Regime Clustering Model
Uses only the most significant features: ozone, nitrogen_dioxide, sulphur_dioxide, temperature_2m, pm2_5
"""

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import os
import joblib
from pathlib import Path

def train_cluster_model():
    """
    Train clustering model on air quality features
    """
    print("=" * 60)
    print("WEATHER-AIR REGIME CLUSTERING MODEL TRAINING")
    print("=" * 60)
    
    # -------------------------
    # 1. Load the dataset
    # -------------------------
    # Adjust path to your dataset
    data_path = Path(__file__).parent.parent / "datasets" / "dashboard_df.csv"
    print(f"\n .. Loading data from: {data_path}")
    
    if not data_path.exists():
        print(f"× Dataset not found at {data_path}")
        return
    
    df = pd.read_csv(data_path)
    print(f"✓ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # -------------------------
    # 2. Define most significant features
    # -------------------------
    significant_features = [
        "ozone",
        "nitrogen_dioxide", 
        "sulphur_dioxide",
        "temperature_2m",
        "pm2_5"
    ]
    
    print(f"\n🔎 Using significant features: {significant_features}")
    
    # Check which features are available
    available_features = [f for f in significant_features if f in df.columns]
    
    if len(available_features) < len(significant_features):
        missing = set(significant_features) - set(available_features)
        print(f"⚠️ Warning: Missing features: {missing}")
        print(f"✓ Available features: {available_features}")
    
    if not available_features:
        print("× No significant features found in dataset!")
        return
    
    # -------------------------
    # 3. Prepare feature matrix
    # -------------------------
    print("\n🛠️ Preparing feature matrix...")
    X = df[available_features].copy()
    
    # Drop rows with missing values
    initial_rows = len(X)
    X = X.dropna()
    dropped_rows = initial_rows - len(X)
    print(f"✓ Features prepared: {X.shape[0]} samples, {X.shape[1]} features")
    if dropped_rows > 0:
        print(f"   Dropped {dropped_rows} rows with missing values")
    
    # -------------------------
    # 4. Create and train pipeline
    # -------------------------
    print("\n⚙️ Training clustering model...")
    
    # Determine number of PCA components (max 5, but not more than features)
    n_components = min(len(available_features), 5)
    
    # Create pipeline
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('pca', PCA(n_components=n_components, random_state=42)),
        ('cluster', KMeans(n_clusters=4, random_state=42, n_init=20))
    ])
    
    # Train the model
    pipeline.fit(X)
    print("✓ Model training complete!")
    
    # -------------------------
    # 5. Analyze clusters
    # -------------------------
    print("\n📊 Analyzing cluster characteristics...")
    
    # Get cluster labels
    cluster_labels = pipeline.predict(X)
    
    # Create dataframe with clusters
    X_with_clusters = X.copy()
    X_with_clusters['Cluster'] = cluster_labels
    
    # Calculate cluster profiles
    cluster_profiles = {}
    for cluster_id in range(4):
        cluster_data = X_with_clusters[X_with_clusters['Cluster'] == cluster_id]
        
        if len(cluster_data) > 0:
            profile = {}
            for feature in available_features:
                profile[f"{feature}_mean"] = cluster_data[feature].mean()
                profile[f"{feature}_std"] = cluster_data[feature].std()
            
            cluster_profiles[int(cluster_id)] = profile
            print(f"\n  Cluster {cluster_id}: {len(cluster_data)} samples")
            for feature in available_features:
                print(f"    {feature}: {profile[f'{feature}_mean']:.2f} ± {profile[f'{feature}_std']:.2f}")
    
    # -------------------------
    # 6. Create meaningful regime labels based on actual data patterns
    # -------------------------
    print("\n🏷️ Creating regime labels based on cluster characteristics...")
    
    # This will be customized based on your actual data
    # You can adjust these after seeing the cluster profiles
    regime_labels = {
        0: "Urban Background – Mixed Emissions (Cool)",
        1: "Ozone-Dominant – Cold Transport Regime", 
        2: "Photochemical Ozone Regime – Warm Season",
        3: "Combustion-Dominant Pollution Episode"
    }
    
    print("Regime labels:")
    for cluster_id, label in regime_labels.items():
        print(f"  Cluster {cluster_id}: {label}")
    
    # -------------------------
    # 7. Package the model
    # -------------------------
    print("\n Packaging model with metadata...")
    
    model_package = {
        "pipeline": pipeline,
        "features": available_features,
        "regime_labels": regime_labels,
        "cluster_profiles": cluster_profiles,
        "n_clusters": 4,
        "pca_components": n_components,
        "training_samples": len(X),
        "feature_importance": "PCA transformed - all significant features used"
    }
    
    # -------------------------
    # 8. Save the model
    # -------------------------
    # Save directly to central models folder (already exists)
    models_dir = Path(__file__).parent.parent / "models"  # Go up to air_quality_analysis/models/
    
    # Save with clear, distinct name
    save_path = models_dir / "weather_regime_cluster_v1.pkl"
    
    print(f"\n ..Saving model to: {save_path}")
    joblib.dump(model_package, save_path)
    
    # Also save a backup with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = models_dir / f"weather_regime_cluster_{timestamp}.pkl"
    joblib.dump(model_package, backup_path)
    print(f"✓ Backup saved to: {backup_path}")
    
    # -------------------------
    # 9. Verify the save
    # -------------------------
    if save_path.exists():
        file_size = save_path.stat().st_size / 1024  # Size in KB
        print(f"\n✓ Model successfully saved!")
        print(f"   File: {save_path.name}")
        print(f"   Size: {file_size:.2f} KB")
        print(f"   Features: {available_features}")
        print(f"   Training samples: {len(X)}")
    else:
        print("\n× Error: Model file was not created!")
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    
    return model_package

if __name__ == "__main__":
    train_cluster_model()