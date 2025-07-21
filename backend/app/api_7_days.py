from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
from scripts.preprocessing import clean_and_engineer_features

# Load model, features, scaler
model = joblib.load('app/model/7_days.joblib')
features = joblib.load('app/model/7_days_features.pkl')
scaler = joblib.load('app/model/7_days_scaler.pkl')

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# class WeatherInput(BaseModel):
#     date: str
#     tavg: float
#     tmax: float
#     tmin: float
#     pres: float
#     prcp: float
#     wspd: float

@app.post("/predict")
def predict_7days_weather(units: str = Query("imperial", description="Units: 'metric' or 'imperial'")):
    try:
        df = pd.read_csv('data/export.csv')
        df = clean_and_engineer_features(df)
        input_row = df[features].tail(1)
        input_scaled = scaler.transform(input_row)

        predictions = model.predict(input_scaled)[0]
        
        if units == "imperial":
            # Convert to Fahrenheit
            pred_converted = predictions * 9 / 5 + 32
        else:
            # Keep as Celsius (original)
            pred_converted = predictions
            
        results = {f"day_{i+1}": round(pred, 1) for i, pred in enumerate(pred_converted)}
        return {"7_day_tmax_prediction": results}

    except Exception as e:
        return {"error": str(e)}
    
@app.get("/today")
def get_today_weather(units: str = Query("imperial", description="Units: 'metric' or 'imperial'")):
    try:
        df = pd.read_csv('data/export.csv')
        today_row = df.tail(1).copy()
        
        if units == "imperial":
            # Convert to Imperial units
            today_row['tavg'] = today_row['tavg'] * 9/5 + 32
            today_row['tmax'] = today_row['tmax'] * 9/5 + 32
            today_row['tmin'] = today_row['tmin'] * 9/5 + 32
            today_row['pres'] = today_row['pres'] * 0.02953  # kPa to inHg
            today_row['prcp'] = today_row['prcp'] * 0.0393701  # mm to inches
            today_row['wspd'] = today_row['wspd'] * 0.621371  # km/h to mph
        # else: keep metric units (original)

        return{
            "date": today_row['date'].values[0],
            "tavg": round(today_row['tavg'].values[0], 1),
            "tmax": round(today_row['tmax'].values[0], 1),
            "tmin": round(today_row['tmin'].values[0], 1),
            "pres": round(today_row['pres'].values[0], 2),
            "prcp": round(today_row['prcp'].values[0], 2),
            "wspd": round(today_row['wspd'].values[0], 2),
            "units": units
        }
    
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def root():
    return {"message": "✅ Weather API is running"}

