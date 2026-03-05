"""
Train AQI Risk Classifier using only 5 significant features
Features: pm2_5, pm10, no2, so2, o3
"""

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, accuracy_score
import joblib
from pathlib import Path
from datetime import datetime

def train_aqi_classifier():
    """
    Train AQI risk classifier on 5 key air quality features
    """
    print("=" * 60)
    print("AQI RISK CLASSIFIER TRAINING")
    print("=" * 60)
    
    # -------------------------
    # 1. Load the dataset
    # -------------------------
    data_path = Path(__file__).parent.parent / "datasets" / "dashboard_df.csv"
    print(f"\n📂 Loading data from: {data_path}")
    
    if not data_path.exists():
        print(f"❌ Dataset not found at {data_path}")
        return
    
    df = pd.read_csv(data_path)
    print(f"✅ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # -------------------------
    # 2. Define 5 significant features
    # -------------------------
    significant_features = ['pm2_5', 'pm10', 'no2', 'so2', 'o3']
    
    print(f"\n🔍 Using significant features: {significant_features}")
    
    # Check which features are available
    available_features = [f for f in significant_features if f in df.columns]
    
    if len(available_features) < len(significant_features):
        missing = set(significant_features) - set(available_features)
        print(f"⚠️ Warning: Missing features: {missing}")
        print(f"✅ Available features: {available_features}")
    
    if not available_features:
        print("❌ No significant features found in dataset!")
        return
    
    # -------------------------
    # 3. Create target variable (AQI risk categories)
    # -------------------------
    print("\n🏷️ Creating AQI risk categories...")
    
    if 'us_aqi' not in df.columns:
        print("❌ No AQI column found to create target variable")
        return
    
    # Create 4 risk categories based on AQI values
    conditions = [
        (df['us_aqi'] <= 50),           # Good
        (df['us_aqi'] <= 100),           # Moderate
        (df['us_aqi'] <= 150),           # Unhealthy for Sensitive
        (df['us_aqi'] > 150)             # Unhealthy
    ]
    
    choices = ['Good', 'Moderate', 'Unhealthy for Sensitive', 'Unhealthy']
    df['aqi_risk'] = np.select(conditions, choices, default='Unknown')
    
    print("✅ Created risk categories from us_aqi")
    print("\n📊 Risk category distribution (before balancing):")
    print(df['aqi_risk'].value_counts())
    
    # Check if Unhealthy class exists
    if 'Unhealthy' not in df['aqi_risk'].values:
        print("\n⚠️ No 'Unhealthy' samples found! Combining categories...")
        # Combine 'Unhealthy for Sensitive' and 'Unhealthy' into 'High Risk'
        df['aqi_risk'] = df['aqi_risk'].replace({
            'Unhealthy for Sensitive': 'High Risk',
            'Unhealthy': 'High Risk'
        })
        print("New distribution:")
        print(df['aqi_risk'].value_counts())
    
    # -------------------------
    # 4. Prepare feature matrix and target
    # -------------------------
    print("\n🛠️ Preparing feature matrix...")
    
    X = df[available_features].copy()
    y = df['aqi_risk'].copy()
    
    # Drop rows with missing values
    initial_rows = len(X)
    X = X.dropna()
    y = y.loc[X.index]
    
    dropped_rows = initial_rows - len(X)
    print(f"✅ Features prepared: {X.shape[0]} samples, {X.shape[1]} features")
    if dropped_rows > 0:
        print(f"   Dropped {dropped_rows} rows with missing values")
    
    # Check class distribution
    class_counts = y.value_counts()
    print(f"\n📊 Risk category distribution:")
    print(class_counts)
    
    # -------------------------
    # 5. Create and train pipeline with class weights
    # -------------------------
    print("\n🤖 Training AQI classifier...")
    
    # Calculate class weights to handle imbalance
    class_weights = compute_class_weight('balanced', classes=np.unique(y), y=y)
    class_weight_dict = dict(zip(np.unique(y), class_weights))
    print(f"Using class weights: {class_weight_dict}")
    
    # Create base model with class weights
    base_model = ExtraTreesClassifier(n_estimators=200, random_state=42, class_weight=class_weight_dict)
    
    # Create pipeline with feature selection
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('feature_selection', SelectFromModel(estimator=base_model)),
        ('classifier', ExtraTreesClassifier(n_estimators=200, random_state=42, class_weight=class_weight_dict))
    ])
    
    # Train the model
    pipeline.fit(X, y)
    print("✅ Model training complete!")
    
    # -------------------------
    # 6. Evaluate model with per-class accuracy
    # -------------------------
    print("\n📊 Evaluating model...")
    
    y_pred = pipeline.predict(X)
    accuracy = accuracy_score(y, y_pred)
    print(f"\nOverall Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y, y_pred))
    
    # -------------------------
    # 7. Test with extreme values
    # -------------------------
    print("\n🧪 Testing with extreme pollution values:")
    test_cases = [
        {'pm2_5': 15, 'pm10': 25, 'no2': 20, 'so2': 10, 'o3': 50},   # Should be Good
        {'pm2_5': 55, 'pm10': 80, 'no2': 60, 'so2': 30, 'o3': 120},  # Should be High Risk
        {'pm2_5': 250, 'pm10': 300, 'no2': 200, 'so2': 150, 'o3': 200},  # Should be High Risk
    ]
    
    for i, test in enumerate(test_cases):
        test_df = pd.DataFrame([test])
        # Ensure only available features are used
        test_df = test_df[available_features]
        pred = pipeline.predict(test_df)[0]
        if hasattr(pipeline, 'predict_proba'):
            proba = pipeline.predict_proba(test_df)[0]
            confidence = max(proba) * 100
            print(f"Test {i+1}: {test} -> {pred} (confidence: {confidence:.1f}%)")
        else:
            print(f"Test {i+1}: {test} -> {pred}")
    
    # -------------------------
    # 8. Package the model
    # -------------------------
    print("\n📦 Packaging model with metadata...")
    
    # Get feature importance
    if hasattr(pipeline.named_steps['classifier'], 'feature_importances_'):
        importances = pipeline.named_steps['classifier'].feature_importances_
        feature_importance = dict(zip(available_features, importances))
    else:
        feature_importance = {}
    
    model_package = {
        'pipeline': pipeline,
        'features': available_features,
        'classes': list(pipeline.classes_),
        'feature_importance': feature_importance,
        'training_samples': len(X),
        'accuracy': accuracy
    }
    
    # -------------------------
    # 9. Save the model to central folder
    # -------------------------
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Save with clear name
    save_path = models_dir / "aqi_risk_classifier_v1.pkl"
    
    print(f"\n💾 Saving model to: {save_path}")
    joblib.dump(model_package, save_path)
    
    # Save backup with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = models_dir / f"aqi_risk_classifier_{timestamp}.pkl"
    joblib.dump(model_package, backup_path)
    print(f"✅ Backup saved to: {backup_path}")
    
    # -------------------------
    # 10. Verify the save
    # -------------------------
    if save_path.exists():
        file_size = save_path.stat().st_size / 1024
        print(f"\n✅ Model successfully saved!")
        print(f"   File: {save_path.name}")
        print(f"   Size: {file_size:.2f} KB")
        print(f"   Features: {available_features}")
        print(f"   Classes: {list(pipeline.classes_)}")
        print(f"   Training samples: {len(X)}")
        print(f"   Accuracy: {accuracy:.3f}")
    else:
        print("\n❌ Error: Model file was not created!")
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    
    return model_package

if __name__ == "__main__":
    train_aqi_classifier()