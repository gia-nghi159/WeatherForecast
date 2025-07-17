from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd 
from app.preprocessing import preprocess_input  

model = joblib.load('app/model/ridge_model.joblib')
original_df = pd.read_csv('data/weather_training_data.csv')

app = FastAPI()

class WeatherInput(BaseModel):
    date: str
    tmax: float
    tmin: float
    prcp: float = 0
    snow: float = 0
    snwd: float = 0

@app.post("/predict")
def predict_weather(data: WeatherInput):
    try:
        # convert input data to DataFrame
        new_row = pd.DataFrame([data.model_dump()])  # model_dump() converts Pydantic model to dict
        # combine with original data
        df_combined = pd.concat([original_df, new_row], ignore_index=True)
        # preprocess the combined data
        preprocessed_df = preprocess_input(df_combined)
        # pick the input row for prediction
        input_row = preprocessed_df.iloc[-1:]
        # define predictor variables
        X = model.feature_names_in_
        # make prediction
        prediction = model.predict(input_row[X])[0]
        return {"predicted tmax": int(prediction)}
    except Exception as e:
        return {"error": str(e)}