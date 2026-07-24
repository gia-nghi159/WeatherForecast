import json
from datetime import datetime, timedelta
import joblib
import pandas as pd
import redis
import fakeredis
import time
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from src.schemas import PredictionResponse, TodayWeatherResponse, HealthStatusResponse
from src.config import (
    CACHE_TTL_PREDICT,
    CACHE_TTL_TODAY,
    DAILY_CSV,
    EVALUATIONS_LOG,
    HOURLY_CSV,
    MODEL_PATH,
    MODEL_VERSION,
    PREDICTIONS_LOG,
    REDIS_URL,
    logger,
)
from src.preprocessing import clean_and_engineer_features

app = FastAPI(title="Dallas Weather Forecast API", version="1.0.0")

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Latency Header Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    
    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    
    print(f"⚡ [{request.method}] {request.url.path} -> {process_time:.2f} ms")
    return response

# 3. Redis Connection (Dual-Mode: Cloud vs. Local In-Memory)
if REDIS_URL:
    try:
        cache = redis.from_url(REDIS_URL, decode_responses=True)
        cache.ping()
        logger.info("Connected to Production Cloud Redis.")
    except Exception as e:
        logger.warning(f"Cloud Redis connection failed ({e}). Fallback to non-cached execution.")
        cache = None
else:
    try:
        cache = fakeredis.FakeRedis(decode_responses=True)
        logger.info("Connected to Local In-Memory FakeRedis instance.")
    except Exception as e:
        logger.warning(f"FakeRedis unavailable ({e}). Fallback to non-cached execution.")
        cache = None

# 4. ML Model Pipeline
try:
    pipe = joblib.load(MODEL_PATH)
    logger.info("Machine learning model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load model from {MODEL_PATH}: {e}")
    pipe = None


def log_predictions_to_file(predictions_c: list):
    """Logs raw prediction output with target dates for ground truth matching."""
    today = datetime.now().date()
    log_entries = []

    for i, pred_temp in enumerate(predictions_c):
        target_date = today + timedelta(days=i + 1)
        log_entries.append(
            {
                "predicted_at": str(today),
                "target_date": str(target_date),
                "horizon_days": i + 1,
                "predicted_tmax_c": round(float(pred_temp), 2),
                "model_version": MODEL_VERSION,
            }
        )

    PREDICTIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PREDICTIONS_LOG, "a") as f:
        for entry in log_entries:
            f.write(json.dumps(entry) + "\n")
    logger.info(f"Logged {len(log_entries)} predictions for ground-truth evaluation.")


@app.post("/predict", response_model=PredictionResponse)
def predict_7days_weather(
    units: str = Query("imperial", description="Units: 'metric' or 'imperial'")
):
    cache_key = f"weather:predict:{units}"

    # Check Redis Cache First
    if cache:
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache HIT for key: {cache_key}")
            return Response(content=cached_response, media_type="application/json")

    logger.info(f"Cache MISS for key: {cache_key}. Computing prediction...")

    if pipe is None:
        raise HTTPException(status_code=500, detail="Model file is not initialized.")

    try:
        df = pd.read_csv(DAILY_CSV)
        df_60 = df.tail(60).copy()
        df_60 = clean_and_engineer_features(df_60)

        X = df_60[pipe.feature_names_in_].tail(1)
        if X.isnull().any().any():
            X = X.ffill().fillna(0)

        # Raw prediction in Celsius
        raw_predictions_c = pipe.predict(X)[0]

        # Log predictions for future ground truth evaluation
        log_predictions_to_file(raw_predictions_c)

        # Unit Conversion
        predictions = raw_predictions_c
        if units == "imperial":
            predictions = predictions * 9 / 5 + 32

        results = {
            f"day_{i+1}": float(round(pred, 1))
            for i, pred in enumerate(predictions)
        }

        response = {
            "7_day_tmax_prediction": results,
            "units": "°F" if units == "imperial" else "°C",
            "model_version": MODEL_VERSION,
            "status": "success",
        }

        # Store Result in Redis Cache
        if cache:
            cache.setex(cache_key, CACHE_TTL_PREDICT, json.dumps(response))

        return response

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/today", response_model=TodayWeatherResponse)
def get_today_weather(
    units: str = Query("imperial", description="Units: 'metric' or 'imperial'")
):
    cache_key = f"weather:today:{units}"

    # Check Cache
    if cache:
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache HIT for key: {cache_key}")
            return Response(content=cached_response, media_type="application/json")

    if not HOURLY_CSV.exists():
        raise HTTPException(status_code=404, detail="Hourly data missing.")

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
        temp = temp * 9 / 5 + 32
        prcp = prcp * 0.0393701 if pd.notna(prcp) else 0
        wspd = wspd * 0.621371 if pd.notna(wspd) else 0
        pres = pres * 0.02953 if pd.notna(pres) else 0

    response = {
        "datetime": row["time"],
        "temp": round(float(temp), 1),
        "prcp": round(float(prcp), 2),
        "wspd": round(float(wspd), 2),
        "wdir": round(float(wdir), 0),
        "pres": round(float(pres), 2),
        "units": "°F" if units == "imperial" else "°C",
        "status": "success",
    }

    if cache:
        cache.setex(cache_key, CACHE_TTL_TODAY, json.dumps(response))

    return response


@app.get("/health", response_model=HealthStatusResponse)
def get_health_status():
    redis_status = False
    if cache:
        try:
            redis_status = cache.ping()
        except Exception:
            redis_status = False

    live_mae = None
    if EVALUATIONS_LOG.exists():
        try:
            eval_df = pd.read_json(EVALUATIONS_LOG, lines=True)
            if not eval_df.empty:
                live_mae = round(float(eval_df["absolute_error_c"].mean()), 2)
        except Exception as e:
            logger.warning(f"Could not parse evaluations log: {e}")

    return {
        "status": "healthy" if (pipe is not None and redis_status) else "degraded",
        "redis_connected": redis_status,
        "model_loaded": pipe is not None,
        "model_version": MODEL_VERSION,
        "live_production_mae_c": live_mae,
    }


@app.get("/")
def root():
    return {
        "status": "success",
        "message": "Weather API is running",
        "version": "1.0.0",
        "endpoints": {
            "/predict": "POST - Get 7-day predictions",
            "/today": "GET - Get today's weather",
            "/health": "GET - System health and MLOps metrics",
        },
    }