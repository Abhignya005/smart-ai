import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, mean_squared_error
import xgboost as xgb

def generate_synthetic_data(days=30):
    print("Generating Synthetic SmartHome Dataset...")
    np.random.seed(42)
    start_time = datetime(2026, 1, 1, 0, 0, 0)
    intervals = days * 24 * 4 # 15 min intervals
    
    timestamps = [start_time + timedelta(minutes=15*i) for i in range(intervals)]
    hours = np.array([t.hour for t in timestamps])
    
    # Initialize features
    motion_bedroom = np.zeros(intervals)
    motion_kitchen = np.zeros(intervals)
    motion_living = np.zeros(intervals)
    door_main = np.zeros(intervals)
    power_kitchen = np.zeros(intervals)
    power_ac = np.zeros(intervals)
    activities = []
    
    for i in range(intervals):
        h = hours[i]
        # Basic routine logic for generating plausible synthetic data
        if 0 <= h < 7:
            activity = "Sleeping"
            motion_bedroom[i] = np.random.choice([0, 1], p=[0.9, 0.1])
            power_ac[i] = 1.0 + np.random.normal(0, 0.1)
        elif 7 <= h < 8:
            activity = "Cooking"
            motion_kitchen[i] = 1
            power_kitchen[i] = 2.5 + np.random.normal(0, 0.5)
            power_ac[i] = 1.2
        elif 8 <= h < 17:
            activity = "Leaving Home"
            if h == 8: door_main[i] = 1
            power_ac[i] = 0.1
        elif 17 <= h < 19:
            activity = "Cooking"
            motion_kitchen[i] = 1
            power_kitchen[i] = 3.0 + np.random.normal(0, 0.5)
            power_ac[i] = 1.5
        else:
            activity = "Watching TV"
            motion_living[i] = 1
            power_ac[i] = 1.5
            
        # Add random anomalies (1% chance)
        if np.random.rand() < 0.01:
            activity = "Anomalous Activity"
            power_kitchen[i] = 5.0
            motion_kitchen[i] = 1
            motion_living[i] = 1
            
        activities.append(activity)
        
    total_power = power_kitchen + power_ac + np.random.normal(0.5, 0.1, intervals)
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'motion_bedroom': motion_bedroom,
        'motion_kitchen': motion_kitchen,
        'motion_living': motion_living,
        'door_main': door_main,
        'power_kitchen': power_kitchen,
        'power_ac': power_ac,
        'total_power': total_power,
        'Actual_Activity': activities
    })
    
    df.to_csv('synthetic_smarthome_data.csv', index=False)
    print("Dataset saved to synthetic_smarthome_data.csv")
    return df

def feature_engineering(df):
    print("Performing Feature Engineering...")
    df['hour'] = df['timestamp'].dt.hour
    df['is_weekend'] = df['timestamp'].dt.dayofweek.isin([5, 6]).astype(int)
    df['motion_count'] = df['motion_bedroom'] + df['motion_kitchen'] + df['motion_living']
    
    # Time series features
    df['lag_power_1'] = df['total_power'].shift(1).bfill()
    df['rolling_mean_power'] = df['total_power'].rolling(4).mean().bfill()
    
    # Energy Forecasting Target (Next 15m)
    df['target_power_next'] = df['total_power'].shift(-1)
    df = df.dropna()
    return df

def train_activity_model(df):
    print("Training Human Activity Recognition Model...")
    # Filter out anomalous class for normal training
    train_df = df[df['Actual_Activity'] != "Anomalous Activity"]
    
    features = ['motion_bedroom', 'motion_kitchen', 'motion_living', 'door_main', 'power_kitchen', 'power_ac', 'hour', 'is_weekend']
    X = train_df[features]
    y = train_df['Actual_Activity']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Model 1: Logistic Regression
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train_scaled, y_train)
    lr_preds = lr.predict(X_test_scaled)
    
    # Model 2: Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train_scaled, y_train)
    rf_preds = rf.predict(X_test_scaled)
    
    metrics = {
        "Logistic Regression": {
            "Accuracy": round(accuracy_score(y_test, lr_preds), 3),
            "F1_Weighted": round(f1_score(y_test, lr_preds, average='weighted'), 3)
        },
        "Random Forest": {
            "Accuracy": round(accuracy_score(y_test, rf_preds), 3),
            "F1_Weighted": round(f1_score(y_test, rf_preds, average='weighted'), 3)
        }
    }
    
    # Save best model (RF)
    joblib.dump(rf, 'rf_activity_model.pkl')
    joblib.dump(scaler, 'activity_scaler.pkl')
    joblib.dump(list(rf.classes_), 'activity_classes.pkl')
    
    # Feature Importance
    importance = dict(zip(features, np.round(rf.feature_importances_, 3)))
    
    return metrics, importance

def train_energy_model(df):
    print("Training Energy Forecasting Model...")
    features = ['total_power', 'hour', 'is_weekend', 'lag_power_1', 'rolling_mean_power']
    X = df[features]
    y = df['target_power_next']
    
    # Chronological Split
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # RF Regressor
    rf_reg = RandomForestRegressor(n_estimators=50, random_state=42)
    rf_reg.fit(X_train, y_train)
    rf_preds = rf_reg.predict(X_test)
    
    # XGBoost
    xgb_reg = xgb.XGBRegressor(n_estimators=50, random_state=42)
    xgb_reg.fit(X_train, y_train)
    xgb_preds = xgb_reg.predict(X_test)
    
    metrics = {
        "Random Forest": {
            "MAE": round(mean_absolute_error(y_test, rf_preds), 3),
            "RMSE": round(np.sqrt(mean_squared_error(y_test, rf_preds)), 3)
        },
        "XGBoost": {
            "MAE": round(mean_absolute_error(y_test, xgb_preds), 3),
            "RMSE": round(np.sqrt(mean_squared_error(y_test, xgb_preds)), 3)
        }
    }
    
    xgb_reg.save_model('xgboost_forecaster.json')
    return metrics

def train_anomaly_model(df):
    print("Training Anomaly Detection Model (Isolation Forest)...")
    features = ['total_power', 'motion_count', 'hour']
    X = df[features]
    
    iso = IsolationForest(contamination=0.02, random_state=42)
    iso.fit(X)
    
    joblib.dump(iso, 'isolation_forest.pkl')
    return "Isolation Forest Trained successfully."

def main():
    base_dir = os.path.dirname(os.path.abspath(__name__))
    ml_dir = os.path.join(base_dir, "ml_backend")
    os.chdir(ml_dir)
    
    df = generate_synthetic_data(days=30)
    df = feature_engineering(df)
    
    act_metrics, act_importance = train_activity_model(df)
    nrg_metrics = train_energy_model(df)
    train_anomaly_model(df)
    
    final_metrics = {
        "Activity_Recognition": act_metrics,
        "Feature_Importance": act_importance,
        "Energy_Forecasting": nrg_metrics
    }
    
    with open('model_metrics.json', 'w') as f:
        json.dump(final_metrics, f, indent=4)
        
    print("\n--- ML PIPELINE COMPLETE ---")
    print("Saved Models:")
    print("- rf_activity_model.pkl")
    print("- activity_scaler.pkl")
    print("- xgboost_forecaster.json")
    print("- isolation_forest.pkl")
    print("- model_metrics.json")
    print("\nAll models and metrics are now available for the ML Dashboard.")

if __name__ == "__main__":
    main()
