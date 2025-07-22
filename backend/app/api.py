from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
import os
from scripts.preprocessing import clean_and_engineer_features

# Load model, features, scaler with error handling
try:
    model = joblib.load('app/model/dallas_fw.joblib')
    features = joblib.load('app/model/7_days_features.pkl')
    scaler = joblib.load('app/model/7_days_scaler.pkl')
    print("Models loaded successfully")
except Exception as e:
    print(f"Error loading models: {e}")
    raise

app = FastAPI()

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Alternative Vite port
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:5173", # Alternative localhost format
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/predict")
def predict_7days_weather(units: str = Query("imperial", description="Units: 'metric' or 'imperial'")):
    try:
        df = pd.read_csv('data/export(1).csv')
        df = clean_and_engineer_features(df)
        
        if len(df) < 1:
            raise HTTPException(status_code=500, detail="Insufficient processed data")
        
        input_row = df[features].tail(1)
        
        # Handle missing values
        if input_row.isnull().any().any():
            print("Filling missing values")
            input_row = input_row.fillna(method='ffill').fillna(0)
        
        input_scaled = scaler.transform(input_row)
        predictions = model.predict(input_scaled)[0]

        print(f"Raw predictions: {predictions}")

        if units == "imperial":
            pred_converted = predictions * 9 / 5 + 32
            print("Converted to Fahrenheit")
        else:
            pred_converted = predictions
            print("Keeping Celsius")

        results = {f"day_{i+1}": round(pred, 1) for i, pred in enumerate(pred_converted)}
        
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
    try:
        print(f"Today's weather request with units: {units}")
        
        csv_path = 'data/export(1).csv'
        if not os.path.exists(csv_path):
            print(f"CSV file not found at: {csv_path}")
            raise HTTPException(status_code=500, detail=f"Data file not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        
        if df.empty:
            raise HTTPException(status_code=500, detail="Weather data is empty")
        
        today_row = df.tail(1).copy()
        print(f"Latest date: {today_row['date'].values[0]}")

        if units == "imperial":
            # Convert to Imperial units
            today_row['tavg'] = today_row['tavg'] * 9/5 + 32
            today_row['tmax'] = today_row['tmax'] * 9/5 + 32
            today_row['tmin'] = today_row['tmin'] * 9/5 + 32
            today_row['pres'] = today_row['pres'] * 0.02953  # kPa to inHg
            today_row['prcp'] = today_row['prcp'] * 0.0393701  # mm to inches
            today_row['wspd'] = today_row['wspd'] * 0.621371  # km/h to mph
            print("Converted to Imperial units")

        # Safe value extraction with NaN handling
        def safe_value(series, decimals=1):
            val = series.values[0]
            if pd.isna(val):
                return 0.0
            return round(float(val), decimals)

        response = {
            "date": today_row['date'].values[0],
            "tavg": safe_value(today_row['tavg'], 1),
            "tmax": safe_value(today_row['tmax'], 1),
            "tmin": safe_value(today_row['tmin'], 1),
            "pres": safe_value(today_row['pres'], 2),
            "prcp": safe_value(today_row['prcp'], 2),
            "wspd": safe_value(today_row['wspd'], 2),
            "units": units,
            "status": "success"
        }
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Today's weather error: {str(e)}"
        print(f"{error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


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