from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
import os
from scripts.preprocessing import clean_and_engineer_features

ROOT = os.path.dirname(os.path.dirname(__file__))
DAILY_CSV  = os.path.join(ROOT, "data/export(1).csv")
HOURLY_CSV = os.path.join(ROOT, "data/hourly_data.csv")
MODEL_PATH = os.path.join(ROOT, "app/model/dallas_fw.joblib")

pipe = joblib.load(MODEL_PATH)

app = FastAPI()

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
    "http://weatherforecastfrontend.s3-website.us-east-2.amazonaws.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/predict")
def predict_7days_weather(units: str = Query("imperial", description="Units: 'metric' or 'imperial'")):
    try:
        df = pd.read_csv(DAILY_CSV)
        df_60 = df.tail(60).copy()
        df_60 = clean_and_engineer_features(df_60)

        X = df_60[pipe.feature_names_in_].tail(1)

        # Handle missing values
        if X.isnull().any().any():
            print("Filling missing values")
            X = X.fillna(method='ffill').fillna(0)

        predictions = pipe.predict(X)[0]

        if units == "imperial":
            predictions = predictions * 9 / 5 + 32
            print("Converted to Fahrenheit")

        results = {f"day_{i+1}": float(round(pred, 1)) for i, pred in enumerate(predictions)}

        response = {
            "7_day_tmax_prediction": results,
            "units": "°F" if units == "imperial" else "°C",
            "status": "success"
        }
        
        print(f"Returning prediction: {response}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Prediction error: {str(e)}"
        print(f"{error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    
@app.get("/today")
def get_today_weather(units: str = Query("imperial", description="Units: 'metric' or 'imperial'")):
    df = pd.read_csv(HOURLY_CSV)
    if df.empty:
        return {"message": "No hourly data available"}
    row = df.tail(1).squeeze()        

    temp = row["temp"]
    prcp = row.get("prcp", 0)
    wspd = row.get("wspd", 0)
    wdir = row.get("wdir", 0)
    pres = row.get("pres", 0)

    if units == "imperial":
        temp = temp * 9/5 + 32
        prcp = prcp * 0.0393701 if pd.notna(prcp) else 0
        wspd = wspd * 0.621371  if pd.notna(wspd) else 0
        pres = pres * 0.02953   if pd.notna(pres) else 0

    return {
        "datetime": row["time"],
        "temp": round(float(temp), 1),
        "prcp": round(float(prcp), 2),
        "wspd": round(float(wspd), 2),
        "wdir": round(float(wdir), 0),
        "pres": round(float(pres), 2),
        "units": "°F" if units == "imperial" else "°C",
        "status": "success"
    }

@app.get("/")
def root():
    return {
        "message": "✅ Weather API is running",
        "version": "1.0.0",
        "endpoints": {
            "/predict": "POST - Get 7-day predictions", 
            "/today": "GET - Get today's weather",
        }
    }