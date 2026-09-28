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

def extract_pdf_table(contents):
    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                return df
    raise ValueError("No structured table was detected in this PDF.")

def extract_docx_table(contents):
    doc = docx.Document(io.BytesIO(contents))
    if not doc.tables:
        raise ValueError("No structured table was detected in this DOCX.")
    table = doc.tables[0]
    data = [[cell.text for cell in row.cells] for row in table.rows]
    if len(data) < 2:
        raise ValueError("Table is empty.")
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

@app.post("/api/ingest-document")
async def ingest_document(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        filename = file.filename.lower()
        
        df = None
        format_detected = "unknown"
        
        if filename.endswith(".csv") or filename.endswith(".txt"):
            format_detected = "csv/txt"
            df = pd.read_csv(io.BytesIO(contents))
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            format_detected = "excel"
            df = pd.read_excel(io.BytesIO(contents))
        elif filename.endswith(".pdf"):
            format_detected = "pdf"
            df = extract_pdf_table(contents)
        elif filename.endswith(".docx"):
            format_detected = "docx"
            df = extract_docx_table(contents)
        else:
            return {"success": False, "error": "Unsupported file format. Please upload CSV, XLSX, PDF, DOCX, or TXT."}
            
        if df is None or len(df) == 0:
            return {"success": False, "error": "Unable to read this file. Please verify that the file is not corrupted."}
            
        # Clean column names (strip whitespace)
        df.columns = df.columns.str.strip()
        
        # Save extracted dataset internally
        base_dir = os.path.dirname(os.path.abspath(__file__))
        df.to_csv(os.path.join(base_dir, "current_dataset.csv"), index=False)
        
        # Create preview
        preview = df.head(10).to_dict(orient='records')
        
        return {
            "success": True,
            "filename": file.filename,
            "format": format_detected,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": preview
        }
        
    except Exception as e:
        logger.error(f"Extraction Error: {e}", exc_info=True)
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
    return {"status": "online", "message": "Smart Appliance ML Backend API is running."}

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
        base_dir = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(os.path.join(base_dir, "synthetic_smarthome_data.csv"))
        return {
            "rows": len(df),
            "columns": list(df.columns),
            "activities": df['Actual_Activity'].value_counts().to_dict(),
            "time_range": f"{df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/predict/activity")
def predict_activity_sample():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(os.path.join(base_dir, "synthetic_smarthome_data.csv"))
        rf = joblib.load(os.path.join(base_dir, "rf_activity_model.pkl"))
        scaler = joblib.load(os.path.join(base_dir, "activity_scaler.pkl"))
        sample = df.tail(20).copy()
        features = ['motion_bedroom', 'motion_kitchen', 'motion_living', 'door_main', 'power_kitchen', 'power_ac']
        sample['hour'] = pd.to_datetime(sample['timestamp']).dt.hour
        sample['is_weekend'] = pd.to_datetime(sample['timestamp']).dt.dayofweek.isin([5, 6]).astype(int)
        X = sample[features + ['hour', 'is_weekend']]
        X_scaled = scaler.transform(X)
        preds = rf.predict(X_scaled)
        probs = rf.predict_proba(X_scaled)
        results = []
        for i, (_, row) in enumerate(sample.iterrows()):
            top_idx = np.argmax(probs[i])
            results.append({
                "timestamp": row['timestamp'],
                "actual": row['Actual_Activity'],
                "predicted": str(preds[i]),
                "confidence": round(float(probs[i][top_idx]) * 100, 1),
                "features": {f: float(row[f]) for f in features}
            })
        return {"success": True, "predictions": results}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/detect/anomaly")
def get_anomalies():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(os.path.join(base_dir, "synthetic_smarthome_data.csv"))
        iso = joblib.load(os.path.join(base_dir, "isolation_forest.pkl"))
        sample = df.tail(50).copy()
        sample['hour'] = pd.to_datetime(sample['timestamp']).dt.hour
        sample['motion_count'] = sample['motion_bedroom'] + sample['motion_kitchen'] + sample['motion_living']
        features = ['total_power', 'motion_count', 'hour']
        X = sample[features]
        preds = iso.predict(X)
        scores = iso.decision_function(X)
        results = []
        for i, (_, row) in enumerate(sample.iterrows()):
            results.append({
                "timestamp": row['timestamp'],
                "is_anomaly": bool(preds[i] == -1),
                "score": float(scores[i]),
                "power": float(row['total_power']),
                "motion_count": int(row['motion_count']),
                "actual_activity": row['Actual_Activity']
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
