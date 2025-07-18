from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd 

model = joblib.load('app/model/lasso_model.joblib')
df = pd.read_csv('data/meteostat.csv')
features = model.feature_names_in_

app = FastAPI()

class WeatherInput(BaseModel):
    date: str
    tavg: float
    tmax: float
    tmin: float
    pres: float

@app.post("/predict")
def predict_weather(data: WeatherInput):
    try:
        input_row = pd.DataFrame([data.model_dump()])[list(features)]
        prediction = model.predict(input_row)[0]
        return {"predicted tmax": round(prediction, 1)}
    except Exception as e:
        return {"error": str(e)}