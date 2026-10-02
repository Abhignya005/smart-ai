import io
import os
import json
import joblib
import logging
import xgboost as xgb
import pandas as pd
import numpy as np
import pdfplumber
import docx
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart Appliance AI ML Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def safe_float(val, default: float = 0.0) -> float:
    try:
        if val is None or pd.isna(val):
            return default
        f = float(val)
        return default if (np.isnan(f) or np.isinf(f)) else f
    except Exception:
        return default

def safe_parse_datetime(series: pd.Series) -> pd.Series:
    if series is None or len(series) == 0:
        return pd.Series(dtype="datetime64[ns]")
    try:
        dt = pd.to_datetime(series, errors='coerce')
    except Exception:
        dt = pd.Series([pd.NaT] * len(series))
    
    # If all values are NaT (e.g. numeric codes like 23898 or text)
    if dt.isnull().all():
        dt = pd.date_range(start="2026-09-01 08:00:00", periods=len(series), freq="15min")
    else:
        # Fill any partial NaT with forward/backward fill
        dt = dt.ffill().bfill()
        if dt.isnull().any():
            base = dt.dropna().iloc[-1] if len(dt.dropna()) > 0 else pd.Timestamp("2026-09-01 08:00:00")
            dt = dt.fillna(base)
    return pd.Series(dt)

def parse_dataset_file(contents: bytes, filename: str) -> tuple[pd.DataFrame, str]:
    lower = filename.lower()
    
    # Check max file size (e.g., 50MB)
    if len(contents) > 50 * 1024 * 1024:
        raise ValueError("File size exceeds 50MB limit.")
        
    # Security check: disallow binary executable/archive extensions
    disallowed = ['.exe', '.zip', '.tar', '.gz', '.mp3', '.mp4', '.avi', '.mov', '.jpg', '.png', '.jpeg', '.pdf', '.bin', '.iso', '.sh', '.bat']
    for d in disallowed:
        if lower.endswith(d):
            raise ValueError(f"File format '{d}' is not supported. Supported formats: CSV, Excel (.xlsx, .xls), JSON, Parquet, TSV, TXT.")
            
    if lower.endswith(".parquet"):
        try:
            return pd.read_parquet(io.BytesIO(contents)), "Parquet"
        except Exception as e:
            raise ValueError(f"Unable to read Parquet file: {str(e)}")
            
    elif lower.endswith(".tsv"):
        try:
            return pd.read_csv(io.BytesIO(contents), sep="\t"), "TSV"
        except Exception as e:
            raise ValueError(f"Unable to read TSV file: {str(e)}")
            
    elif lower.endswith(".csv"):
        try:
            return pd.read_csv(io.BytesIO(contents)), "CSV"
        except Exception as e:
            raise ValueError(f"Unable to read CSV file: {str(e)}")
            
    elif lower.endswith(".xlsx") or lower.endswith(".xls"):
        try:
            return pd.read_excel(io.BytesIO(contents)), "Excel"
        except Exception as e:
            raise ValueError(f"Unable to read Excel file: {str(e)}")
            
    elif lower.endswith(".json"):
        try:
            return pd.read_json(io.BytesIO(contents)), "JSON"
        except Exception:
            try:
                parsed_json = json.loads(contents.decode("utf-8"))
                if isinstance(parsed_json, list):
                    return pd.DataFrame(parsed_json), "JSON"
                elif isinstance(parsed_json, dict):
                    for k in ["data", "records", "rows", "items"]:
                        if k in parsed_json and isinstance(parsed_json[k], list):
                            return pd.DataFrame(parsed_json[k]), "JSON"
                    return pd.DataFrame([parsed_json]), "JSON"
                raise ValueError("JSON file does not contain a list or table.")
            except Exception as e:
                raise ValueError(f"Unable to parse JSON file: {str(e)}")
                
    elif lower.endswith(".txt"):
        try:
            sample = contents[:4096].decode("utf-8", errors="ignore")
            sep = ","
            if "\t" in sample and sample.count("\t") > sample.count(","):
                sep = "\t"
            elif ";" in sample and sample.count(";") > sample.count(","):
                sep = ";"
            elif "|" in sample and sample.count("|") > sample.count(","):
                sep = "|"
            return pd.read_csv(io.BytesIO(contents), sep=sep), "TXT (Tabular)"
        except Exception as e:
            raise ValueError(f"Unable to parse structured TXT file: {str(e)}")
            
    else:
        raise ValueError(f"Unsupported file format '{filename}'. Supported formats: CSV, Excel (.xlsx, .xls), JSON, Parquet, TSV, TXT.")

def inspect_dataset_metadata(df: pd.DataFrame, filename: str, format_name: str) -> dict:
    cols = [str(c).strip() for c in df.columns]
    df.columns = cols
    
    person_candidates = ['person_id', 'user_id', 'member_id', 'occupant_id', 'user', 'person', 'subject', 'individual']
    person_col = None
    for c in cols:
        if c.lower() in person_candidates or any(p in c.lower() for p in ['person', 'member', 'occupant']):
            person_col = c
            break
            
    detected_members_list = []
    if person_col:
        detected_members_list = [str(x) for x in df[person_col].dropna().unique().tolist()][:20]
        members_count = len(df[person_col].dropna().unique())
    else:
        members_count = 1
        
    time_candidates = ['timestamp', 'datetime', 'date_time', 'time', 'date']
    time_col = None
    for c in cols:
        if c.lower() in time_candidates or 'timestamp' in c.lower() or 'datetime' in c.lower() or 'time' in c.lower():
            time_col = c
            break
            
    time_range = "Not available"
    if time_col:
        try:
            dt_series = pd.to_datetime(df[time_col], errors='coerce').dropna()
            if len(dt_series) > 0:
                time_range = f"{dt_series.min().strftime('%d/%m/%Y')} – {dt_series.max().strftime('%d/%m/%Y')}"
        except Exception:
            time_range = f"{df[time_col].iloc[0]} – {df[time_col].iloc[-1]}"
            
    act_candidates = ['actual_activity', 'activity', 'label', 'action', 'task', 'target']
    act_col = None
    for c in cols:
        if c.lower() in act_candidates or 'activity' in c.lower():
            act_col = c
            break
            
    detected_activities = []
    if act_col:
        detected_activities = [str(x) for x in df[act_col].dropna().unique().tolist()][:15]
        
    room_candidates = ['room', 'location', 'zone', 'area', 'space']
    room_col = None
    for c in cols:
        if c.lower() in room_candidates:
            room_col = c
            break
            
    motion_sensors = [c for c in cols if 'motion' in c.lower() or 'pir' in c.lower()]
    power_sensors = [c for c in cols if any(p in c.lower() for p in ['power', 'energy', 'watt', 'kw', 'voltage', 'current'])]
    appliance_sensors = [c for c in cols if any(a in c.lower() for a in ['tv', 'ac', 'fridge', 'microwave', 'oven', 'door'])]
    
    missing_count = int(df.isnull().sum().sum())
    total_cells = df.shape[0] * df.shape[1]
    quality_score = round(max(0, (total_cells - missing_count) / total_cells * 100), 1) if total_cells > 0 else 0
    
    suitability = {
        "activity_recognition": {
            "supported": act_col is not None,
            "status": "Activity label detected" if act_col else "No activity label column detected"
        },
        "routine_discovery": {
            "supported": time_col is not None,
            "status": "Timestamp detected" if time_col else "No timestamp column detected"
        },
        "family_analysis": {
            "supported": person_col is not None or members_count > 1,
            "status": f"Person ID detected ({members_count} members)" if person_col else "No person ID detected (Defaulting to Single Household)"
        },
        "room_analysis": {
            "supported": room_col is not None or len(motion_sensors) > 0,
            "status": "Room column/sensors detected" if (room_col or motion_sensors) else "No spatial room features detected"
        }
    }
    
    preview_df = df.head(10).copy()
    preview = json.loads(preview_df.to_json(orient='records', date_format='iso'))
    
    result = {
        "filename": filename,
        "format": format_name,
        "rows": len(df),
        "columns_count": len(cols),
        "columns": cols,
        "person_column": person_col,
        "timestamp_column": time_col,
        "activity_column": act_col,
        "room_column": room_col,
        "sensor_features": motion_sensors + power_sensors + appliance_sensors,
        "detected_members": {
            "count": members_count,
            "members": detected_members_list
        },
        "time_range": time_range,
        "missing_values": missing_count,
        "quality_score": quality_score,
        "detected_activities": detected_activities,
        "suitability": suitability,
        "preview": preview
    }
    
    return json.loads(json.dumps(result, default=str).replace('NaN', 'null').replace('Infinity', 'null'))

def get_active_dataset_info() -> tuple[str, str, bool]:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    current_csv = os.path.join(base_dir, "current_dataset.csv")
    synthetic_csv = os.path.join(base_dir, "synthetic_smarthome_data.csv")
    meta_file = os.path.join(base_dir, "dataset_meta.json")
    
    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r", encoding="utf-8") as mf:
                meta_info = json.load(mf)
                if meta_info.get("is_uploaded") and os.path.exists(current_csv):
                    return current_csv, meta_info.get("filename", "Uploaded Dataset"), True
        except Exception:
            pass
            
    if os.path.exists(current_csv):
        return current_csv, "current_dataset.csv", True
    return synthetic_csv, "synthetic_smarthome_data.csv", False

@app.post("/api/ingest-document")
async def ingest_document(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        filename = file.filename
        
        df, format_name = parse_dataset_file(contents, filename)
        
        if df is None or len(df) == 0:
            return {"success": False, "error": "Dataset is empty. Please upload a file containing data."}
            
        base_dir = os.path.dirname(os.path.abspath(__file__))
        current_csv = os.path.join(base_dir, "current_dataset.csv")
        df.to_csv(current_csv, index=False)
        
        meta = inspect_dataset_metadata(df, filename, format_name)
        if not isinstance(meta, dict):
            meta = {
                "filename": filename,
                "format": format_name,
                "rows": len(df),
                "columns_count": len(df.columns),
                "columns": list(df.columns)
            }
            
        meta_file = os.path.join(base_dir, "dataset_meta.json")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump({"is_uploaded": True, **meta}, f, indent=2)
            
        # Automatically retrain ML model on the newly ingested dataset
        try:
            train_result = train_model_from_dataset()
            logger.info(f"Auto-training on {filename}: {train_result}")
        except Exception as te:
            logger.warning(f"Auto-training notice: {te}")
        
        return {
            "success": True,
            **meta
        }
        
    except ValueError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        logger.error(f"Ingestion Error: {e}", exc_info=True)
        return {"success": False, "error": f"Dataset processing failed: {str(e)}"}

class ColumnMappingRequest(BaseModel):
    person_id: Optional[str] = None
    timestamp: Optional[str] = None
    activity: Optional[str] = None
    room: Optional[str] = None

@app.post("/api/map-columns")
def map_columns(req: ColumnMappingRequest):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        current_csv = os.path.join(base_dir, "current_dataset.csv")
        if not os.path.exists(current_csv):
            return {"success": False, "error": "No uploaded dataset found."}
            
        df = pd.read_csv(current_csv)
        rename_map = {}
        if req.person_id and req.person_id in df.columns:
            rename_map[req.person_id] = "person_id"
        if req.timestamp and req.timestamp in df.columns:
            rename_map[req.timestamp] = "timestamp"
        if req.activity and req.activity in df.columns:
            rename_map[req.activity] = "Actual_Activity"
        if req.room and req.room in df.columns:
            rename_map[req.room] = "room"
            
        if rename_map:
            df.rename(columns=rename_map, inplace=True)
            df.to_csv(current_csv, index=False)
            
        meta_file = os.path.join(base_dir, "dataset_meta.json")
        if os.path.exists(meta_file):
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            meta = inspect_dataset_metadata(df, meta.get("filename", "uploaded_dataset.csv"), meta.get("format", "CSV"))
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump({"is_uploaded": True, **meta}, f, indent=2)
        else:
            meta = inspect_dataset_metadata(df, "uploaded_dataset.csv", "CSV")
            
        return {"success": True, "message": "Columns mapped successfully.", "metadata": meta}
    except Exception as e:
        logger.error(f"Mapping error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

@app.get("/api/current-dataset-meta")
def get_current_dataset_meta():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        meta_file = os.path.join(base_dir, "dataset_meta.json")
        if os.path.exists(meta_file):
            with open(meta_file, "r", encoding="utf-8") as f:
                return {"success": True, "metadata": json.load(f)}
        # Default to synthetic
        synthetic_csv = os.path.join(base_dir, "synthetic_smarthome_data.csv")
        if os.path.exists(synthetic_csv):
            df = pd.read_csv(synthetic_csv)
            meta = inspect_dataset_metadata(df, "synthetic_smarthome_data.csv", "CSV")
            return {"success": True, "metadata": {"is_uploaded": False, **meta}}
        return {"success": False, "error": "No dataset found."}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/current-dataset-raw")
def get_current_dataset_raw():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        current_csv = os.path.join(base_dir, "current_dataset.csv")
        synthetic_csv = os.path.join(base_dir, "synthetic_smarthome_data.csv")
        meta_file = os.path.join(base_dir, "dataset_meta.json")
        
        target_csv = current_csv if os.path.exists(current_csv) else synthetic_csv
        if not os.path.exists(target_csv):
            return {"success": False, "error": "No dataset found."}
            
        filename = "synthetic_smarthome_data.csv"
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    filename = meta.get("filename", os.path.basename(target_csv))
            except Exception:
                pass
                
        df = pd.read_csv(target_csv)
        preview_df = df.head(5000).fillna("")
        headers = df.columns.tolist()
        data = preview_df.to_dict(orient="records")
        
        return {
            "success": True,
            "dataset": {
                "filename": filename,
                "headers": headers,
                "data": data
            }
        }
    except Exception as e:
        logger.error(f"Error serving raw dataset: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


class MLTaskRequest(BaseModel):
    task: str
    filename: str

@app.post("/api/run-ml-task")
async def run_ml_task(req: MLTaskRequest):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dataset_path = os.path.join(base_dir, "current_dataset.csv")
        
        if not os.path.exists(dataset_path):
            return {"success": False, "error": "No dataset found. Please upload again."}
            
        df = pd.read_csv(dataset_path)
        
        # --- COLUMN MAPPING / NORMALIZATION ---
        col_map = {
            "date and time": "timestamp",
            "date_time": "timestamp",
            "time": "timestamp",
            "power consumption": "total_power",
            "energy": "total_power",
            "power": "total_power",
            "electricity": "total_power",
            "global_active_power": "total_power",
            "global active power": "total_power",
            "sub_metering_1": "power_kitchen",
            "sub_metering_2": "power_laundry",
            "sub_metering_3": "power_ac",
            "activity label": "Actual_Activity",
            "activity": "Actual_Activity"
        }
        
        # Case insensitive mapping
        df.columns = [str(c).strip() for c in df.columns]
        df.rename(columns=lambda x: col_map.get(str(x).lower().strip(), x), inplace=True)
        
        # If timestamp is missing but date and time exist, combine them
        if 'timestamp' not in df.columns and 'date' in [c.lower() for c in df.columns]:
             pass
        
        # Map sub-meters to motion for dummy data mapping if needed (as fallback)
        if 'power_kitchen' in df.columns and 'motion_kitchen' not in df.columns:
             df['motion_kitchen'] = (df['power_kitchen'] > 1.0).astype(int)
        if 'power_ac' in df.columns and 'motion_living' not in df.columns:
             df['motion_living'] = (df['power_ac'] > 1.0).astype(int)
        
        # Fill NA
        df = df.ffill().bfill()
        
        results = {}
        
        if req.task == "activity":
            req_cols = ['motion_bedroom', 'motion_kitchen', 'motion_living', 'door_main', 'power_kitchen', 'power_ac']
            
            # Gracefully impute missing sensors with 0 (inactive) so the model doesn't crash on pure energy datasets
            for c in req_cols:
                if c not in df.columns:
                    df[c] = 0.0
                
            rf = joblib.load(os.path.join(base_dir, "rf_activity_model.pkl"))
            scaler = joblib.load(os.path.join(base_dir, "activity_scaler.pkl"))
            
            # Simple feature engineering if timestamp exists
            if 'timestamp' in df.columns:
                df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
                df['is_weekend'] = pd.to_datetime(df['timestamp']).dt.dayofweek.isin([5, 6]).astype(int)
            else:
                df['hour'] = 12
                df['is_weekend'] = 0
                
            X = df[req_cols + ['hour', 'is_weekend']]
            X_scaled = scaler.transform(X)
            preds = rf.predict(X_scaled)
            results = {"predictions": preds[:20].tolist(), "message": f"Successfully classified {len(preds)} rows of activities."}
            
        elif req.task == "energy":
            if 'total_power' not in df.columns:
                return {"success": False, "error": "Missing 'total_power' column for Energy Forecasting."}
                
            xgb_model = xgb.XGBRegressor()
            xgb_model.load_model(os.path.join(base_dir, "xgboost_forecaster.json"))
            # Construct features
            df['lag_power_1'] = df['total_power'].shift(1).bfill()
            df['rolling_mean_power'] = df['total_power'].rolling(4).mean().bfill()
            if 'timestamp' in df.columns:
                df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
                df['is_weekend'] = pd.to_datetime(df['timestamp']).dt.dayofweek.isin([5, 6]).astype(int)
            else:
                df['hour'] = 12
                df['is_weekend'] = 0
                
            features = ['total_power', 'hour', 'is_weekend', 'lag_power_1', 'rolling_mean_power']
            X = df[features]
            preds = xgb_model.predict(X)
            results = {"forecast_next_15m": preds[:20].tolist()}
            
        elif req.task == "anomaly":
            if 'total_power' not in df.columns:
                 return {"success": False, "error": "Missing 'total_power' column."}
                 
            iso = joblib.load(os.path.join(base_dir, "isolation_forest.pkl"))
            if 'timestamp' in df.columns:
                df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            else:
                df['hour'] = 12
                
            # Compute motion count if available
            motion_cols = [c for c in df.columns if 'motion' in c.lower()]
            if motion_cols:
                df['motion_count'] = df[motion_cols].sum(axis=1)
            else:
                df['motion_count'] = 0
                
            X = df[['total_power', 'motion_count', 'hour']]
            preds = iso.predict(X)
            anomalies = int(np.sum(preds == -1))
            results = {"anomalies_detected": anomalies, "total_samples": len(df)}
            
        elif req.task == "routine":
            if 'total_power' not in df.columns:
                 return {"success": False, "error": "Missing 'total_power' column."}
            
            if 'timestamp' in df.columns:
                df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            else:
                df['hour'] = 12
                
            from sklearn.cluster import KMeans
            
            # Simple 3-cluster routine learning
            X = df[['total_power', 'hour']].dropna()
            
            if len(X) < 3:
                return {"success": False, "error": "Not enough data points for routine learning."}
                
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            df['Routine_Cluster'] = kmeans.fit_predict(X)
            
            cluster_centers = kmeans.cluster_centers_
            
            # Formulate human-readable routines
            routines = []
            for i, center in enumerate(cluster_centers):
                power = center[0]
                hour = int(center[1])
                
                time_of_day = "Morning" if 5 <= hour < 12 else "Afternoon" if 12 <= hour < 17 else "Evening" if 17 <= hour < 22 else "Night"
                intensity = "High Activity" if power > 3.0 else "Medium Activity" if power > 1.0 else "Low Activity"
                
                routines.append({
                    "cluster_id": i,
                    "typical_time": f"{hour}:00",
                    "time_of_day": time_of_day,
                    "average_power": round(power, 2),
                    "behavior_profile": f"{time_of_day} - {intensity}"
                })
                
            results = {
                "discovered_routines": routines,
                "message": "Successfully clustered historical behaviors."
            }
            
        else:
            return {"success": False, "error": "Task not implemented yet."}
            
        return {"success": True, "results": results}
        
    except Exception as e:
        logger.error(f"ML Task Error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

# Include the previous endpoints for the dashboard views
@app.get("/")
def read_root():
    return {"status": "online", "message": "HabitSense-Activity Analyser Backend API is running."}

@app.get("/api/metrics")
def get_metrics():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, "model_metrics.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/dataset-summary")
def dataset_summary():
    try:
        target_csv, filename, _ = get_active_dataset_info()
        df = pd.read_csv(target_csv)
        time_cols = [c for c in df.columns if 'time' in c.lower() or 'date' in c.lower()]
        time_col = time_cols[0] if time_cols else df.columns[0]
        act_cols = [c for c in df.columns if 'activity' in c.lower() or 'label' in c.lower()]
        act_col = act_cols[0] if act_cols else None
        
        return {
            "rows": len(df),
            "columns": list(df.columns),
            "activities": df[act_col].value_counts().to_dict() if act_col else {},
            "time_range": f"{df[time_col].iloc[0]} to {df[time_col].iloc[-1]}" if len(df) > 0 else "N/A"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/predict/activity")
def predict_activity_sample():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        target_csv, _, _ = get_active_dataset_info()
        df = pd.read_csv(target_csv)
        rf = joblib.load(os.path.join(base_dir, "rf_activity_model.pkl"))
        scaler = joblib.load(os.path.join(base_dir, "activity_scaler.pkl"))
        sample = df.tail(20).copy()
        
        req_features = ['motion_bedroom', 'motion_kitchen', 'motion_living', 'door_main', 'power_kitchen', 'power_ac']
        for f in req_features:
            if f not in sample.columns:
                sample[f] = 0.0
                
        time_cols = [c for c in sample.columns if 'time' in c.lower() or 'date' in c.lower()]
        time_col = time_cols[0] if time_cols else 'timestamp'
        if time_col in sample.columns:
            sample['hour'] = pd.to_datetime(sample[time_col]).dt.hour
            sample['is_weekend'] = pd.to_datetime(sample[time_col]).dt.dayofweek.isin([5, 6]).astype(int)
        else:
            sample['hour'] = 12
            sample['is_weekend'] = 0
            
        act_cols = [c for c in sample.columns if 'activity' in c.lower() or 'label' in c.lower()]
        act_col = act_cols[0] if act_cols else None
        
        X = sample[req_features + ['hour', 'is_weekend']].fillna(0)
        X_scaled = scaler.transform(X)
        preds = rf.predict(X_scaled)
        probs = rf.predict_proba(X_scaled)
        results = []
        for i, (_, row) in enumerate(sample.iterrows()):
            top_idx = np.argmax(probs[i])
            results.append({
                "timestamp": str(row.get(time_col, "")),
                "actual": str(row.get(act_col, "")) if act_col else "",
                "predicted": str(preds[i]),
                "confidence": round(float(probs[i][top_idx]) * 100, 1),
                "features": {f: float(row.get(f, 0)) for f in req_features}
            })
        return {"success": True, "predictions": results}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/detect/anomaly")
def get_anomalies():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        target_csv, _, _ = get_active_dataset_info()
        df = pd.read_csv(target_csv)
        iso = joblib.load(os.path.join(base_dir, "isolation_forest.pkl"))
        sample = df.tail(50).copy()
        
        time_cols = [c for c in sample.columns if 'time' in c.lower() or 'date' in c.lower()]
        time_col = time_cols[0] if time_cols else 'timestamp'
        if time_col in sample.columns:
            sample['hour'] = pd.to_datetime(sample[time_col]).dt.hour
        else:
            sample['hour'] = 12
            
        if 'total_power' not in sample.columns:
            sample['total_power'] = sample.get('power_kw', 0.0)
            
        motion_cols = [c for c in sample.columns if 'motion' in c.lower()]
        if motion_cols:
            sample['motion_count'] = sample[motion_cols].sum(axis=1)
        else:
            sample['motion_count'] = 0
            
        features = ['total_power', 'motion_count', 'hour']
        X = sample[features].fillna(0)
        preds = iso.predict(X)
        scores = iso.decision_function(X)
        
        act_cols = [c for c in sample.columns if 'activity' in c.lower() or 'label' in c.lower()]
        act_col = act_cols[0] if act_cols else None
        
        results = []
        for i, (_, row) in enumerate(sample.iterrows()):
            results.append({
                "timestamp": str(row.get(time_col, "")),
                "is_anomaly": bool(preds[i] == -1),
                "score": float(scores[i]),
                "power": float(row.get('total_power', 0.0)),
                "motion_count": int(row.get('motion_count', 0)),
                "actual_activity": str(row.get(act_col, "")) if act_col else ""
            })
        return {"success": True, "anomalies": results}
    except Exception as e:
        return {"error": str(e)}


from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class ChatRequest(BaseModel):
    messages: list
    context: dict

@app.post("/api/chat")
async def chat_with_groq(req: ChatRequest):
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "YOUR_GROQ_API_KEY":
        return {"success": False, "error": "GROQ_API_KEY is missing or invalid in backend .env file."}
        
    try:
        client = Groq(api_key=groq_api_key)
        
        system_prompt = f"""You are the AI Assistant for a Privacy-Preserving Personal Routine & Activity Intelligence platform.
You are helping the user understand their dataset and Machine Learning results.
Do NOT invent values. ONLY use the provided context below to answer questions. If the answer isn't in the context, say "Insufficient data to determine this."
Keep answers concise, helpful, and focused on data science / ML insights.

CURRENT ML CONTEXT:
- Total Dataset Rows: {req.context.get('rows', 'Unknown')}
- Routine Consistency Score: {req.context.get('consistency', 'Unknown')}
- Current Detected Activity: {req.context.get('currentActivity', 'Unknown')} ({req.context.get('currentConf', 'Unknown')})
- Predicted Next Activity: {req.context.get('nextActivity', 'Unknown')} ({req.context.get('nextConf', 'Unknown')})
- Anomalies Detected: {req.context.get('anomalies', 'Unknown')}
- Peak Energy: {req.context.get('peakEnergy', 'Unknown')}
- Routine Drift Status: {req.context.get('driftInfo', {}).get('status', 'Unknown')} - {req.context.get('driftInfo', {}).get('text', 'Unknown')}
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add user conversation history
        for msg in req.messages:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.3,
            max_completion_tokens=512
        )
        
        reply = completion.choices[0].message.content
        return {"success": True, "reply": reply}
    except Exception as e:
        logger.error(f"Groq API Error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


# --- DYNAMIC MULTI-USER & SINGLE OCCUPANT SYSTEM ---
from typing import List, Optional, Dict, Any
import copy
import numpy as np

HOUSEHOLD_STATE = {
    "mode": "family" # "single" or "family"
}

USER_FEEDBACK = []

def get_active_dataset_occupants(df: Optional[pd.DataFrame] = None) -> tuple[bool, Optional[str], List[dict], bool]:
    """
    Dynamically detects unique occupants from the active dataset.
    Returns (has_person_id, person_col, occupants_list, is_multi_occupant)
    """
    if df is None:
        csv_file, _, _ = get_active_dataset_info()
        try:
            df = pd.read_csv(csv_file)
        except Exception:
            return False, None, [{
                "id": "Household",
                "name": "Single Activity Stream",
                "typical_rooms": ["Living Room", "Kitchen", "Bedroom"],
                "is_undifferentiated": True
            }], False

    cols = df.columns.tolist()
    person_candidates = ['person_id', 'user_id', 'member_id', 'occupant_id', 'user', 'person', 'subject', 'individual']
    person_col = None
    for c in cols:
        if c.lower() in person_candidates or any(p in c.lower() for p in ['person', 'member', 'occupant']):
            person_col = c
            break

    if person_col:
        unique_vals = [str(x).strip() for x in df[person_col].dropna().unique().tolist() if str(x).strip() != ""]
        if len(unique_vals) > 0:
            is_multi = len(unique_vals) > 1
            profiles = []
            for pid in unique_vals:
                pname = f"Person {pid}" if str(pid).isdigit() else str(pid)
                profiles.append({
                    "id": pid,
                    "name": pname,
                    "typical_rooms": ["Living Room", "Kitchen", "Bedroom"],
                    "is_undifferentiated": False
                })
            return True, person_col, profiles, is_multi

    # If no person_id column is present or empty:
    # Do NOT invent occupants. Treat dataset as a single undifferentiated activity stream.
    return False, None, [{
        "id": "Single Activity Stream",
        "name": "Single Activity Stream",
        "typical_rooms": ["Living Room", "Kitchen", "Bedroom"],
        "is_undifferentiated": True
    }], False

class ProfileUpdate(BaseModel):
    name: str
    age_group: str
    typical_rooms: List[str]

@app.get("/api/settings/mode")
def get_mode():
    return {"success": True, "mode": HOUSEHOLD_STATE["mode"]}

@app.post("/api/settings/mode")
def set_mode(mode: dict):
    if mode.get("mode") in ["single", "family"]:
        HOUSEHOLD_STATE["mode"] = mode["mode"]
        return {"success": True, "mode": HOUSEHOLD_STATE["mode"]}
    return {"success": False, "error": "Invalid mode"}

@app.get("/api/profiles")
def get_profiles():
    has_person_id, person_col, profiles, is_multi = get_active_dataset_occupants()
    return {
        "success": True,
        "has_person_id": has_person_id,
        "is_multi_occupant": is_multi,
        "occupant_count": len(profiles),
        "profiles": profiles
    }

@app.get("/api/routine/{person_id}")
def get_person_routine(person_id: str):
    _, _, profiles, _ = get_active_dataset_occupants()
    person = next((p for p in profiles if p["id"] == person_id), None)
    if not person and len(profiles) > 0:
        person = profiles[0]
        
    pname = person["name"] if person else person_id
    routines = [
        {"time": "07:00 - 08:30", "activity": "Breakfast / Morning Routine", "status": "Normal"},
        {"time": "12:30 - 13:30", "activity": "Lunch / Kitchen", "status": "Normal"},
        {"time": "19:00 - 20:30", "activity": "Dinner / Cooking", "status": "Normal"},
        {"time": "20:30 - 22:30", "activity": "Relaxing / Watching TV", "status": "Normal"},
        {"time": "23:00 - 06:30", "activity": "Sleeping", "status": "Normal"}
    ]
    return {"success": True, "person": pname, "routine": routines}

class SensorEvent(BaseModel):
    motion_bedroom: float = 0
    motion_kitchen: float = 0
    motion_living: float = 0
    door_main: float = 0
    power_kitchen: float = 0
    power_ac: float = 0
    total_power: float = 0
    hour: int = 12
    timestamp: str = ""
    actual_activity: str = "" 

def _predict_single_activity(rf, scaler, iso, event_dict, features):
    x_data = [[event_dict.get(f, 0) for f in features] + [event_dict.get('hour', 12), 0]]
    x_scaled = scaler.transform(x_data)
    activity_pred = rf.predict(x_scaled)[0]
    probs = rf.predict_proba(x_scaled)[0]
    confidence = round(float(np.max(probs)) * 100, 1)
    
    motion_count = event_dict.get('motion_bedroom',0) + event_dict.get('motion_kitchen',0) + event_dict.get('motion_living',0)
    iso_x = [[event_dict.get('total_power',0), motion_count, event_dict.get('hour',12)]]
    is_anomaly_global = iso.predict(iso_x)[0] == -1
    anomaly_score = round(float(iso.decision_function(iso_x)[0]), 3)
    
    transitions = {
        "Cooking": "Eating", "Eating": "Kitchen Cleanup", "Watching TV": "Sleeping",
        "Leaving Home": "Unknown", "Sleeping": "Leaving Home", "Anomalous Activity": "Unknown",
        "Working": "Taking Break", "Exercising": "Resting"
    }
    
    return {
        "activity": str(activity_pred),
        "confidence": confidence,
        "is_anomaly_global": is_anomaly_global,
        "anomaly_score": anomaly_score,
        "next_activity": transitions.get(str(activity_pred), "Unknown")
    }

@app.post("/api/predict/multi_user")
def predict_multi_user(event: SensorEvent):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        rf = joblib.load(os.path.join(base_dir, "rf_activity_model.pkl"))
        scaler = joblib.load(os.path.join(base_dir, "activity_scaler.pkl"))
        iso = joblib.load(os.path.join(base_dir, "isolation_forest.pkl"))
        features = ['motion_bedroom', 'motion_kitchen', 'motion_living', 'door_main', 'power_kitchen', 'power_ac']
        
        has_person_id, person_col, profiles, is_multi = get_active_dataset_occupants()
        
        if not is_multi or HOUSEHOLD_STATE["mode"] == "single":
            # Single Person Mode: One prediction for the entire house or single person
            res = _predict_single_activity(rf, scaler, iso, event.dict(), features)
            
            is_personalized_anomaly = False
            reason = "Normal activity."
            if res["activity"] == "Cooking" and (event.hour < 5 or event.hour > 22):
                is_personalized_anomaly = True
                reason = "Occurred significantly outside normal activity period."
            elif res["is_anomaly_global"]:
                is_personalized_anomaly = True
                reason = "High power/motion combination detected compared to baseline."
                
            lead_occupant = profiles[0] if len(profiles) > 0 else {"id": "Single Stream", "name": "Single Activity Stream"}
            return {
                "success": True,
                "mode": "single",
                "activities": [{
                    "person": lead_occupant["name"],
                    "person_id": lead_occupant["id"],
                    "activity": res["activity"],
                    "actual_activity": event.actual_activity if event.actual_activity else None,
                    "is_correct": (event.actual_activity == res["activity"]) if event.actual_activity else None,
                    "location": "Whole House",
                    "confidence": res["confidence"],
                    "anomaly_score": res["anomaly_score"],
                    "next_activity": res["next_activity"],
                    "next_confidence": 82.5 if res["next_activity"] != "Unknown" else 0.0,
                    "anomaly_status": "Unusual" if is_personalized_anomaly else "Normal",
                    "anomaly_reason": reason,
                    "is_demo_attribution": False,
                    "timestamp": event.timestamp if event.timestamp else "Unknown"
                }]
            }
            
        else:
            # Multi-Person Mode: Break down simultaneous activities
            active_rooms = []
            if event.motion_kitchen > 0 or event.power_kitchen > 0: active_rooms.append("Kitchen")
            if event.motion_living > 0 or event.power_ac > 0: active_rooms.append("Living Room")
            if event.motion_bedroom > 0: active_rooms.append("Bedroom")
            
            if not active_rooms:
                active_rooms = ["Living Room"]
                
            activities = []
            used_persons = set()
            
            for idx, room in enumerate(active_rooms):
                sub_event = event.dict()
                if room == "Kitchen":
                    sub_event['motion_living'] = 0; sub_event['motion_bedroom'] = 0
                elif room == "Living Room":
                    sub_event['motion_kitchen'] = 0; sub_event['motion_bedroom'] = 0; sub_event['power_kitchen'] = 0
                elif room == "Bedroom":
                    sub_event['motion_kitchen'] = 0; sub_event['motion_living'] = 0; sub_event['power_kitchen'] = 0
                
                res = _predict_single_activity(rf, scaler, iso, sub_event, features)
                
                # Attribute to detected occupants
                candidates = [p for p in profiles if p["id"] not in used_persons]
                if not candidates:
                    candidates = profiles
                
                person_obj = candidates[0] if candidates else {"name": f"Occupant {idx+1}", "id": f"P{idx+1}"}
                used_persons.add(person_obj["id"])
                
                is_personalized_anomaly = False
                reason = "Normal activity."
                if res["activity"] == "Cooking" and (event.hour < 5 or event.hour > 22):
                    is_personalized_anomaly = True
                    reason = f"Occurred outside normal cooking window."
                elif res["is_anomaly_global"]:
                    is_personalized_anomaly = True
                    reason = "Unusual sensor pattern."
                    
                actual_act = event.actual_activity if event.actual_activity else None
                activities.append({
                    "person": person_obj["name"],
                    "person_id": person_obj["id"],
                    "activity": res["activity"],
                    "actual_activity": actual_act,
                    "is_correct": (actual_act == res["activity"]) if actual_act else None,
                    "location": room,
                    "confidence": res["confidence"],
                    "anomaly_score": res["anomaly_score"],
                    "next_activity": res["next_activity"],
                    "next_confidence": 82.5 if res["next_activity"] != "Unknown" else 0.0,
                    "anomaly_status": "Unusual" if is_personalized_anomaly else "Normal",
                    "anomaly_reason": reason,
                    "is_demo_attribution": True,
                    "timestamp": event.timestamp if event.timestamp else "Unknown"
                })
                
            return {
                "success": True,
                "mode": "family",
                "activities": activities
            }
            
    except Exception as e:
        import traceback
        logger.error(f"Prediction error: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

class FeedbackRequest(BaseModel):
    person: str
    predicted_activity: str
    actual_activity: str
    timestamp: str

@app.post("/api/feedback")
def submit_feedback(req: FeedbackRequest):
    USER_FEEDBACK.append(req.dict())
    return {"success": True, "message": "Feedback recorded."}


@app.get("/api/family/dashboard")
def get_family_dashboard(inactivity_window_mins: int = 30):
    try:
        csv_file, data_source_name, is_uploaded = get_active_dataset_info()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        df = pd.read_csv(csv_file)
        if len(df) == 0:
            return {"success": False, "error": "Dataset is empty"}
            
        has_person_id, person_col, profiles_list, is_multi = get_active_dataset_occupants(df)
        occupant_count = len(profiles_list) if has_person_id else 1
        
        cols = df.columns.tolist()
        time_cols = [c for c in cols if 'time' in c.lower() or 'date' in c.lower()]
        time_col = time_cols[0] if len(time_cols) > 0 else 'timestamp'
        
        act_cols = [c for c in cols if 'activity' in c.lower() or 'label' in c.lower()]
        act_col = act_cols[0] if len(act_cols) > 0 else None
        
        room_cols = [c for c in cols if 'room' in c.lower() or 'location' in c.lower()]
        has_room_col = len(room_cols) > 0
        room_col = room_cols[0] if has_room_col else None
        
        # Missing values check & quality note
        missing_count = int(df.isnull().sum().sum())
        if has_person_id:
            data_quality = f"Good ({occupant_count} occupant{'s' if occupant_count != 1 else ''} detected)" if missing_count == 0 else f"Limited ({missing_count} missing values)"
        else:
            data_quality = "Single undifferentiated stream (No person_id column detected in dataset)"
            
        # Parse datetime safely
        df['dt'] = safe_parse_datetime(df[time_col])
        df = df.sort_values('dt').reset_index(drop=True)
        latest_dt = df['dt'].iloc[-1] if len(df) > 0 else pd.Timestamp.now()
        threshold_dt = latest_dt - pd.Timedelta(minutes=inactivity_window_mins)
        
        # Load models
        rf = joblib.load(os.path.join(base_dir, "rf_activity_model.pkl"))
        scaler = joblib.load(os.path.join(base_dir, "activity_scaler.pkl"))
        iso = joblib.load(os.path.join(base_dir, "isolation_forest.pkl"))
        req_features = ['motion_bedroom', 'motion_kitchen', 'motion_living', 'door_main', 'power_kitchen', 'power_ac']
        for f in req_features:
            if f not in df.columns:
                df[f] = 0.0
        if 'total_power' not in df.columns:
            df['total_power'] = 0.0
            
        room_sensor_map = {
            "Kitchen": ["motion_kitchen", "power_kitchen"],
            "Living Room": ["motion_living", "power_ac"],
            "Bedroom": ["motion_bedroom"],
            "Main Door": ["door_main"]
        }
        
        transitions = {
            "Cooking": "Eating", "Eating": "Kitchen Cleanup", "Watching TV": "Sleeping",
            "Leaving Home": "Unknown", "Sleeping": "Leaving Home", "Anomalous Activity": "Unknown",
            "Working": "Taking Break", "Exercising": "Resting"
        }
        
        member_cards = []
        active_now_count = 0
        unusual_count = 0
        
        for prof in profiles_list:
            pid = prof["id"]
            pname = prof["name"]
            typical = prof.get("typical_rooms", ["Living Room", "Kitchen", "Bedroom"])
            
            # If dataset has person_id, filter strictly to this occupant
            if has_person_id and person_col:
                member_df = df[df[person_col].astype(str).str.strip() == str(pid)].copy()
            else:
                member_df = df.copy()
                
            if len(member_df) > 0:
                latest_member_row = member_df.iloc[-1]
                rec_time = latest_member_row['dt']
                is_active = (rec_time >= threshold_dt)
            else:
                latest_member_row = None
                rec_time = None
                is_active = False
                
            # Collect member-specific recent events history strictly for this occupant
            m_events = []
            if len(member_df) > 0:
                for _, mr in member_df.tail(10).iloc[::-1].iterrows():
                    m_events.append({
                        "time": mr['dt'].strftime("%I:%M %p").lstrip("0") if pd.notna(mr['dt']) else "Recent",
                        "timestamp_raw": str(mr['dt']),
                        "activity": str(mr.get(act_col, "Active")) if act_col and act_col in mr and pd.notna(mr[act_col]) else "Active",
                        "room": str(mr.get(room_col, "Living Room")) if (has_room_col and room_col and room_col in mr and pd.notna(mr[room_col])) else "Living Room",
                        "person_id": pid
                    })
                
            # Identify active room
            active_room_found = "Living Room"
            if latest_member_row is not None:
                if has_room_col and room_col and room_col in latest_member_row and pd.notna(latest_member_row[room_col]):
                    active_room_found = str(latest_member_row[room_col])
                else:
                    for r in typical:
                        sensors = room_sensor_map.get(r, [])
                        if any(safe_float(latest_member_row.get(s, 0)) > 0 for s in sensors):
                            active_room_found = r
                            break
                        
            if latest_member_row is not None:
                hour = rec_time.hour if (rec_time is not None and hasattr(rec_time, 'hour')) else 12
                is_weekend = int(rec_time.dayofweek in [5, 6]) if (rec_time is not None and hasattr(rec_time, 'dayofweek')) else 0
                
                curr_room = active_room_found.lower()
                feat_dict = {f: safe_float(latest_member_row.get(f, 0)) for f in req_features}
                if 'motion' in latest_member_row:
                    m_val = safe_float(latest_member_row.get('motion', 0))
                    if 'bedroom' in curr_room: feat_dict['motion_bedroom'] = m_val
                    elif 'kitchen' in curr_room: feat_dict['motion_kitchen'] = m_val
                    elif 'living' in curr_room: feat_dict['motion_living'] = m_val
                if 'power_kw' in latest_member_row:
                    p_val = safe_float(latest_member_row.get('power_kw', 0))
                    if 'kitchen' in curr_room: feat_dict['power_kitchen'] = p_val
                    elif 'living' in curr_room: feat_dict['power_ac'] = p_val
                if 'door' in latest_member_row:
                    feat_dict['door_main'] = safe_float(latest_member_row.get('door', 0))
                
                x_data = [[feat_dict.get(f, 0.0) for f in req_features] + [hour, is_weekend]]
                x_scaled = scaler.transform(x_data)
                ml_pred = str(rf.predict(x_scaled)[0])
                probs = rf.predict_proba(x_scaled)[0]
                conf = round(float(np.max(probs)) * 100, 1)
                conf_level = "High" if conf >= 80 else "Medium" if conf >= 50 else "Low"
                
                actual_act = str(latest_member_row.get(act_col, "")) if act_col and act_col in latest_member_row and pd.notna(latest_member_row[act_col]) else None
                is_correct = (actual_act.strip().lower() == ml_pred.strip().lower()) if (actual_act and actual_act.strip()) else None
                
                total_power = safe_float(latest_member_row.get('total_power', latest_member_row.get('power_kw', 0)))
                motion_count = sum(safe_float(latest_member_row.get(s, 0)) for s in ['motion_bedroom', 'motion_kitchen', 'motion_living', 'motion'] if s in latest_member_row)
                iso_x = [[total_power, motion_count, hour]]
                iso_res = iso.predict(iso_x)[0]
                iso_score = round(float(iso.decision_function(iso_x)[0]), 3)
                
                status_eval = "Unusual" if iso_res == -1 else "Normal"
                if ml_pred == "Cooking" and (hour < 5 or hour > 22):
                    status_eval = "Unusual"
                if status_eval == "Unusual":
                    unusual_count += 1
                    
                time_display = rec_time.strftime("%I:%M %p").lstrip("0") if (rec_time is not None and pd.notna(rec_time)) else "Recent"
                next_act = transitions.get(ml_pred, "Unknown")
                next_conf = 82.5 if next_act != "Unknown" else 0.0
                
                if is_active:
                    active_now_count += 1
                    reason_msg = None
                    mem_status = "Active"
                else:
                    mem_status = "Idle"
                    reason_msg = f"Inactive for > {inactivity_window_mins} mins (Last event at {time_display})"
                    
                # Calculate member-specific activity breakdown & room breakdown
                mem_act_counts = {}
                if act_col and act_col in member_df:
                    for a, c in member_df[act_col].value_counts().items():
                        mem_act_counts[str(a)] = int(c)
                else:
                    mem_act_counts[ml_pred] = len(member_df)
                    
                mem_room_counts = {}
                if has_room_col and room_col and room_col in member_df:
                    for r, c in member_df[room_col].value_counts().items():
                        mem_room_counts[str(r)] = int(c)
                else:
                    mem_room_counts[active_room_found] = len(member_df)

                member_cards.append({
                    "id": pid,
                    "name": pname,
                    "status": mem_status,
                    "current_activity": ml_pred,
                    "actual_activity": actual_act if (actual_act and actual_act.strip()) else None,
                    "prediction_accuracy": "Correct" if is_correct is True else "Incorrect" if is_correct is False else "N/A",
                    "room": active_room_found,
                    "confidence": conf,
                    "confidence_level": conf_level,
                    "routine_status": status_eval,
                    "anomaly_score": iso_score,
                    "last_updated": time_display,
                    "next_activity": next_act,
                    "next_confidence": next_conf,
                    "recent_events": m_events,
                    "activity_breakdown": mem_act_counts,
                    "room_breakdown": mem_room_counts,
                    "records_count": len(member_df),
                    "is_undifferentiated": prof.get("is_undifferentiated", False),
                    "reason": reason_msg
                })
            else:
                member_cards.append({
                    "id": pid,
                    "name": pname,
                    "status": "Idle",
                    "current_activity": "Unknown",
                    "actual_activity": None,
                    "prediction_accuracy": "N/A",
                    "room": "Not available",
                    "confidence": None,
                    "confidence_level": None,
                    "routine_status": "Normal",
                    "anomaly_score": 0.12,
                    "last_updated": "No records",
                    "next_activity": "Unknown",
                    "next_confidence": None,
                    "recent_events": [],
                    "activity_breakdown": {},
                    "room_breakdown": {},
                    "records_count": 0,
                    "is_undifferentiated": prof.get("is_undifferentiated", False),
                    "reason": "No activity data found for this occupant."
                })
                
        # Calculate COMBINED / HOUSEHOLD level stats across ALL records in dataset
        household_activities = {}
        if act_col and act_col in df:
            for a, c in df[act_col].value_counts().items():
                household_activities[str(a)] = int(c)
        else:
            for m in member_cards:
                if m["current_activity"] != "Unknown":
                    household_activities[m["current_activity"]] = household_activities.get(m["current_activity"], 0) + 1

        room_occupancy = {}
        if has_room_col and room_col and room_col in df:
            for r, c in df[room_col].value_counts().items():
                room_occupancy[str(r)] = int(c)
        else:
            for m in member_cards:
                if m["room"] != "Not available":
                    room_occupancy[m["room"]] = room_occupancy.get(m["room"], 0) + 1

        # Activity timeline from actual recent rows across dataset
        recent_df = df.tail(12).iloc[::-1]
        timeline = []
        for _, row in recent_df.iterrows():
            r_time = row['dt'].strftime("%I:%M %p").lstrip("0") if pd.notna(row['dt']) else "Recent"
            r_act = str(row.get(act_col, "Active")) if (act_col and act_col in row and pd.notna(row[act_col])) else "Active"
            r_room = str(row[room_col]) if (has_room_col and room_col and room_col in row and pd.notna(row[room_col])) else "Living Room"
            assigned_p = str(row[person_col]) if (has_person_id and person_col and person_col in row and pd.notna(row[person_col])) else ("Single Stream" if not has_person_id else profiles_list[0]["id"])
            timeline.append({
                "time": r_time,
                "person_id": assigned_p,
                "activity": r_act,
                "room": r_room
            })
            
        idle_now_count = max(0, len(profiles_list) - active_now_count)
        
        return {
            "success": True,
            "data_source": data_source_name,
            "data_quality": data_quality,
            "has_person_id": has_person_id,
            "occupant_count": occupant_count,
            "is_multi_occupant": is_multi,
            "mode_supported": "multi_and_individual" if is_multi else "single_only",
            "person_column": person_col,
            "summary": {
                "members_total": len(profiles_list),
                "active_now": active_now_count,
                "idle_now": idle_now_count,
                "unusual_count": unusual_count
            },
            "members": member_cards,
            "household_activities": household_activities,
            "room_occupancy": room_occupancy,
            "timeline": timeline,
            "anomaly_summary": {
                "normal": max(0, len(profiles_list) - unusual_count),
                "unusual": unusual_count,
                "unknown": 0
            }
        }
    except Exception as e:
        logger.error(f"Family dashboard error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

@app.post("/api/train-model")
def train_model_from_dataset():
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, f1_score
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        current_csv = os.path.join(base_dir, "current_dataset.csv")
        synthetic_csv = os.path.join(base_dir, "synthetic_smarthome_data.csv")
        meta_file = os.path.join(base_dir, "dataset_meta.json")
        
        target_csv = current_csv if os.path.exists(current_csv) else synthetic_csv
        df = pd.read_csv(target_csv)
        if len(df) == 0:
            return {"success": False, "error": "Dataset is empty"}
            
        time_cols = [c for c in df.columns if 'time' in c.lower() or 'date' in c.lower()]
        time_col = time_cols[0] if len(time_cols) > 0 else 'timestamp'
        
        act_cols = [c for c in df.columns if 'activity' in c.lower() or 'label' in c.lower()]
        if not act_cols:
            return {"success": False, "error": "No activity ground-truth column found to train the model."}
        act_col = act_cols[0]
        
        df['dt'] = safe_parse_datetime(df[time_col])
        df['hour'] = df['dt'].dt.hour.fillna(12).astype(int)
        df['is_weekend'] = df['dt'].dt.dayofweek.isin([5, 6]).astype(int)
        
        req_features = ['motion_bedroom', 'motion_kitchen', 'motion_living', 'door_main', 'power_kitchen', 'power_ac']
        for f in req_features:
            if f not in df.columns:
                df[f] = 0.0
            else:
                df[f] = df[f].apply(safe_float)
                
        if 'room' in df.columns:
            for idx, row in df.iterrows():
                room = str(row.get('room', '')).lower()
                m_val = safe_float(row.get('motion', 0))
                p_val = safe_float(row.get('power_kw', 0))
                d_val = safe_float(row.get('door', 0))
                if 'bedroom' in room and 'motion' in row: df.at[idx, 'motion_bedroom'] = m_val
                elif 'kitchen' in room:
                    if 'motion' in row: df.at[idx, 'motion_kitchen'] = m_val
                    if 'power_kw' in row: df.at[idx, 'power_kitchen'] = p_val
                elif 'living' in room:
                    if 'motion' in row: df.at[idx, 'motion_living'] = m_val
                    if 'power_kw' in row: df.at[idx, 'power_ac'] = p_val
                if 'door' in row: df.at[idx, 'door_main'] = d_val
                
        all_features = req_features + ['hour', 'is_weekend']
        X = df[all_features].fillna(0)
        y = df[act_col].astype(str)
        
        if len(df) >= 20 and len(np.unique(y)) > 1:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        else:
            X_train, X_test, y_train, y_test = X, X, y, y
            
        scaler = StandardScaler()
        X_tr_sc = scaler.fit_transform(X_train)
        X_te_sc = scaler.transform(X_test)
        
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_tr_sc, y_train)
        preds = rf.predict(X_te_sc)
        
        acc = round(float(accuracy_score(y_test, preds)) * 100, 1)
        f1 = round(float(f1_score(y_test, preds, average='weighted')) * 100, 1)
        
        joblib.dump(rf, os.path.join(base_dir, "rf_activity_model.pkl"))
        joblib.dump(scaler, os.path.join(base_dir, "activity_scaler.pkl"))
        joblib.dump(list(rf.classes_), os.path.join(base_dir, "activity_classes.pkl"))
        
        metrics_file = os.path.join(base_dir, "model_metrics.json")
        training_meta = {
            "trained_on": os.path.basename(target_csv),
            "records": len(df),
            "classes": [str(c) for c in rf.classes_],
            "accuracy": acc,
            "f1_score": f1,
            "trained_at": pd.Timestamp.now().isoformat()
        }
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(training_meta, f, indent=2)
            
        return {
            "success": True,
            "message": f"Successfully trained Random Forest model on {len(df)} records.",
            "metrics": training_meta
        }
    except Exception as e:
        logger.error(f"Model training error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
