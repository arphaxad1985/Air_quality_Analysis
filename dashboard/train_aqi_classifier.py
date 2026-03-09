"""
Train AQI Risk Classifier using 5 significant features
Features: pm2_5, pm10, ozone, nitrogen_dioxide, sulphur_dioxide
FORCES 4 CLASSES with more inclusive Good category
"""

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, accuracy_score
import joblib
from pathlib import Path
from datetime import datetime

def train_aqi_classifier():
    """
    Train AQI risk classifier on 5 key air quality features
    Forces 4 classes with more inclusive Good category
    """
    print("=" * 60)
    print("AQI RISK CLASSIFIER TRAINING (INCLUSIVE GOOD)")
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
    significant_features = ['pm2_5', 'pm10', 'ozone', 'nitrogen_dioxide', 'sulphur_dioxide']
    
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
    # 3. Create target variable with MORE INCLUSIVE Good category
    # -------------------------
    print("\n🏷️ Creating AQI risk categories (inclusive Good)...")
    
    if 'us_aqi' not in df.columns:
        print("❌ No AQI column found to create target variable")
        return
    
    # Initialize with default value
    df['aqi_risk'] = 'Unknown'
    
    # Apply conditions in order (first match wins)
    # Unhealthy first (highest risk)
    df.loc[df['us_aqi'] > 150, 'aqi_risk'] = 'Unhealthy'
    
    # Unhealthy for Sensitive
    df.loc[(df['us_aqi'] <= 150) & (df['us_aqi'] > 100), 'aqi_risk'] = 'Unhealthy for Sensitive'
    
    # Moderate
    df.loc[(df['us_aqi'] <= 100) & (df['us_aqi'] > 60), 'aqi_risk'] = 'Moderate'
    
    # Extended Good (AQI 51-60 with low pollutants)
    df.loc[(df['us_aqi'] <= 60) & (df['us_aqi'] > 50) & 
           (df['pm2_5'] <= 15) & (df['pm10'] <= 30), 'aqi_risk'] = 'Good'
    
    # Standard Good (AQI ≤ 50)
    df.loc[df['us_aqi'] <= 50, 'aqi_risk'] = 'Good'
    
    print("✅ Created risk categories with inclusive Good")
    print("\n📊 Risk category distribution:")
    print(df['aqi_risk'].value_counts())
    
    # Force all 4 classes to exist
    all_classes = ['Good', 'Moderate', 'Unhealthy for Sensitive', 'Unhealthy']
    df['aqi_risk'] = pd.Categorical(df['aqi_risk'], categories=all_classes)
    
    print("\n📊 Forced class distribution:")
    for class_name in all_classes:
        count = (df['aqi_risk'] == class_name).sum()
        print(f"   {class_name:25s}: {count:3d} samples")
    
        print("✅ Created risk categories with inclusive Good")
    print("\n📊 Risk category distribution:")
    print(df['aqi_risk'].value_counts())
    
    # Remove any rows where aqi_risk is 'Unknown'
    initial_rows = len(df)
    df = df[df['aqi_risk'] != 'Unknown'].copy()
    removed_rows = initial_rows - len(df)
    if removed_rows > 0:
        print(f"✅ Removed {removed_rows} rows with 'Unknown' category")
    
    print("\n📊 Cleaned distribution:")
    print(df['aqi_risk'].value_counts())
    
    # Force all 4 classes to exist
    all_classes = ['Good', 'Moderate', 'Unhealthy for Sensitive', 'Unhealthy']
    df['aqi_risk'] = pd.Categorical(df['aqi_risk'], categories=all_classes)
    
    # -------------------------
    # 4. Prepare feature matrix and target
    # -------------------------
    print("\n🛠️ Preparing feature matrix...")
    
    X = df[available_features].copy()
    y = df['aqi_risk'].copy()
    
    # CHECK FOR NAN VALUES IN FEATURES
    print(f"\n🔍 Checking for NaN values in features...")
    nan_count = X.isna().sum().sum()
    print(f"   Total NaN values: {nan_count}")
    
    if nan_count > 0:
        # Show which columns have NaN
        nan_per_column = X.isna().sum()
        cols_with_nan = nan_per_column[nan_per_column > 0]
        print(f"   Columns with NaN values:")
        for col, count in cols_with_nan.items():
            print(f"      - {col}: {count} NaN values")
        
        # Drop rows with NaN
        print(f"\n   Dropping rows with NaN values...")
        rows_before = len(X)
        X = X.dropna()
        y = y.loc[X.index]
        rows_after = len(X)
        print(f"   Removed {rows_before - rows_after} rows with NaN values")
    
    # Also check for NaN in target
    y_nan_count = y.isna().sum()
    if y_nan_count > 0:
        print(f"\n⚠️ Warning: {y_nan_count} NaN values found in target variable")
        # Remove corresponding rows
        valid_indices = ~y.isna()
        X = X[valid_indices]
        y = y[valid_indices]
        print(f"   Removed {y_nan_count} rows with NaN target")
    
    # Final check
    print(f"\n✅ Features prepared: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"   Final NaN check - Features: {X.isna().sum().sum()}, Target: {y.isna().sum()}")
    
    # -------------------------
    # 5. Create and train pipeline with class weights
    # -------------------------
    print("\n🤖 Training AQI classifier...")
    
    # Calculate class weights
    class_weights = {}
    total_samples = len(y)
    n_classes = len(y.cat.categories)
    
    for class_name in y.cat.categories:
        count = (y == class_name).sum()
        if count > 0:
            weight = total_samples / (n_classes * count)
        else:
            weight = 0.5  # Weight for empty class
        class_weights[class_name] = weight
    
    print(f"Using class weights: {class_weights}")
    
    # Create pipeline
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', ExtraTreesClassifier(
            n_estimators=300,
            random_state=42,
            class_weight=class_weights,
            min_samples_split=3,
            min_samples_leaf=1,
            max_depth=15
        ))
    ])
    
    # Train the model
    pipeline.fit(X, y)
    print("✅ Model training complete!")
    print(f"   Model classes: {pipeline.classes_}")
    
    # -------------------------
    # 6. Evaluate model
    # -------------------------
    print("\n📊 Evaluating model...")
    
    y_pred = pipeline.predict(X)
    accuracy = accuracy_score(y, y_pred)
    print(f"\nOverall Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y, y_pred, zero_division=0))
    
    # -------------------------
    # 7. Test with edge cases
    # -------------------------
    print("\n🧪 Testing with edge cases:")
    test_cases = [
        # Very clean air (should be Good)
        {'pm2_5': 5, 'pm10': 5, 'ozone': 4, 'nitrogen_dioxide': 5, 'sulphur_dioxide': 5},
        # Borderline Good (AQI around 55-60)
        {'pm2_5': 12, 'pm10': 25, 'ozone': 45, 'nitrogen_dioxide': 35, 'sulphur_dioxide': 15},
        # Moderate pollution
        {'pm2_5': 25, 'pm10': 35, 'ozone': 60, 'nitrogen_dioxide': 50, 'sulphur_dioxide': 25},
        # High pollution
        {'pm2_5': 45, 'pm10': 60, 'ozone': 90, 'nitrogen_dioxide': 80, 'sulphur_dioxide': 40},
        # Extreme pollution
        {'pm2_5': 180, 'pm10': 170, 'ozone': 160, 'nitrogen_dioxide': 150, 'sulphur_dioxide': 100},
    ]
    
    for i, test in enumerate(test_cases):
        test_df = pd.DataFrame([test])
        test_df = test_df[available_features]
        pred = pipeline.predict(test_df)[0]
        if hasattr(pipeline, 'predict_proba'):
            proba = pipeline.predict_proba(test_df)[0]
            confidence = max(proba) * 100
            print(f"\nTest {i+1}: {test}")
            print(f"   → Predicted: {pred} (confidence: {confidence:.1f}%)")
    
    # -------------------------
    # 8. Package the model
    # -------------------------
    print("\n📦 Packaging model with metadata...")
    
    # Get feature importance
    if hasattr(pipeline.named_steps['classifier'], 'feature_importances_'):
        importances = pipeline.named_steps['classifier'].feature_importances_
        feature_importance = dict(zip(available_features, importances))
        print("\n🔑 Feature importance:")
        for feat, imp in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
            print(f"   {feat:20s}: {imp:.3f}")
    else:
        feature_importance = {}
    
    model_package = {
        'pipeline': pipeline,
        'features': available_features,
        'classes': list(pipeline.classes_),
        'feature_importance': feature_importance,
        'training_samples': len(X),
        'accuracy': accuracy,
        'version': 'aqi_inclusive_good_v5',
        'description': '4-class AQI model with more inclusive Good category'
    }
    
    # -------------------------
    # 9. Save the model
    # -------------------------
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    save_path = models_dir / "aqi_risk_classifier_v5.pkl"
    
    print(f"\n💾 Saving model to: {save_path}")
    joblib.dump(model_package, save_path)
    
    # Save backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = models_dir / f"aqi_risk_classifier_v5_{timestamp}.pkl"
    joblib.dump(model_package, backup_path)
    print(f"✅ Backup saved to: {backup_path}")
    
    # -------------------------
    # 10. Verify
    # -------------------------
    if save_path.exists():
        file_size = save_path.stat().st_size / 1024
        print(f"\n✅ Model saved!")
        print(f"   File: {save_path.name}")
        print(f"   Size: {file_size:.2f} KB")
        print(f"   Features: {available_features}")
        print(f"   Classes: {list(pipeline.classes_)}")
        print(f"   Training samples: {len(X)}")
        print(f"   Accuracy: {accuracy:.3f}")
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    
    return model_package

if __name__ == "__main__":
    train_aqi_classifier()