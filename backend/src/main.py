import json
import time
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import fakeredis
import joblib
import pandas as pd
import redis
import requests

from prometheus_fastapi_instrumentator import Instrumentator, metrics

from src.config import (
    CACHE_TTL_PREDICT,
    CACHE_TTL_TODAY,
    DAILY_CSV,
    DALLAS_LAT,
    DALLAS_LON,
    EVALUATIONS_LOG,
    MODEL_PATH,
    MODEL_VERSION,
    PREDICTIONS_LOG,
    REDIS_URL,
    logger,
)
from src.preprocessing import clean_and_engineer_features
from src.schemas import HealthStatusResponse, PredictionResponse, TodayWeatherResponse

app = FastAPI(title="Dallas Weather Forecast API", version="1.0.0")

# Custom high-resolution latency buckets for sub-millisecond and fast API responses
CUSTOM_LATENCY_BUCKETS = (
    0.001,
    0.0025,
    0.005,
    0.01,
    0.015,
    0.02,
    0.03,
    0.05,
    0.1,
    0.5,
    1.0,
    float("inf"),
)

# Instrument Prometheus metrics with custom histogram buckets
instrumentator = Instrumentator().add(
    metrics.default(
        latency_highr_buckets=CUSTOM_LATENCY_BUCKETS,
        latency_lowr_buckets=CUSTOM_LATENCY_BUCKETS,
    )
)
instrumentator.instrument(app).expose(app)

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
        cache = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1.0, socket_timeout=1.0)
        cache.ping()
        logger.info("Connected to Redis Cache.")
    except Exception as e:
        logger.warning(f"Redis connection failed ({e}). Fallback to non-cached execution.")
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
    """Updates the log file by keeping the most recent prediction for each 

    (target_date, horizon_days) combination.
    """
    today = datetime.now().date()
    
    logs_map = {}
    if PREDICTIONS_LOG.exists():
        with open(PREDICTIONS_LOG, "r") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    key = (entry["target_date"], entry["horizon_days"])
                    logs_map[key] = entry

    for i, pred_temp in enumerate(predictions_c):
        target_date = str(today + timedelta(days=i + 1))
        horizon = i + 1
        key = (target_date, horizon)
        
        logs_map[key] = {
            "predicted_at": str(today),
            "target_date": target_date,
            "horizon_days": horizon,
            "predicted_tmax_c": round(float(pred_temp), 2),
            "model_version": MODEL_VERSION,
        }

    PREDICTIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PREDICTIONS_LOG, "w") as f:
        for entry in logs_map.values():
            f.write(json.dumps(entry) + "\n")
            
    logger.info(f"Successfully synchronized {len(predictions_c)} predictions to log.")


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

    # In src/main.py inside predict_7days_weather()

    try:
        df = pd.read_csv(DAILY_CSV)
        
        # Compute features over full dataset so expanding means match training
        df_engineered = clean_and_engineer_features(df)

        # Extract the most recent engineered row for live prediction
        X = df_engineered[pipe.feature_names_in_].tail(1)
        if X.isnull().any().any():
            X = X.ffill().fillna(0)

        # Raw prediction in Celsius
        raw_predictions_c = pipe.predict(X)[0]
        log_predictions_to_file(raw_predictions_c)

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

    # 1. Check Redis Cache First
    if cache:
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache HIT for key: {cache_key}")
            return Response(content=cached_response, media_type="application/json")

    # 2. Cache MISS: Fetch live telemetry from Open-Meteo API
    logger.info(f"Cache MISS for key: {cache_key}. Fetching live telemetry from Open-Meteo...")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": DALLAS_LAT,
        "longitude": DALLAS_LON,
        "current": "temperature_2m,precipitation,surface_pressure,wind_speed_10m,wind_direction_10m",
        "timezone": "America/Chicago",
    }

    try:
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
        current = res.json().get("current", {})

        temp = current.get("temperature_2m", 0)
        prcp = current.get("precipitation", 0)
        wspd = current.get("wind_speed_10m", 0)
        wdir = current.get("wind_direction_10m", 0)
        pres = current.get("surface_pressure", 0)

        # Unit Conversion
        if units == "imperial":
            temp = temp * 9 / 5 + 32
            prcp = prcp * 0.0393701
            wspd = wspd * 0.621371
            pres = pres * 0.02953

        response = {
            "datetime": current.get("time", str(datetime.now())),
            "temp": round(float(temp), 1),
            "prcp": round(float(prcp), 2),
            "wspd": round(float(wspd), 2),
            "wdir": round(float(wdir), 0),
            "pres": round(float(pres), 2),
            "units": "°F" if units == "imperial" else "°C",
            "status": "success",
        }

        # 3. Store in Redis Cache
        if cache:
            cache.setex(cache_key, CACHE_TTL_TODAY, json.dumps(response))

        return response

    except Exception as e:
        logger.error(f"Failed to fetch live telemetry: {e}")
        raise HTTPException(status_code=500, detail="Weather telemetry service unavailable.")


@app.get("/health", response_model=HealthStatusResponse)
def get_health_status():
    redis_status = False
    if cache:
        try:
            redis_status = cache.ping()
        except Exception:
            redis_status = False

    live_mae = None
    mae_cache_key = "weather:health:mae"
    
    if cache:
        cached_mae = cache.get(mae_cache_key)
        if cached_mae:
            live_mae = float(cached_mae)

    if live_mae is None and EVALUATIONS_LOG.exists():
        try:
            eval_df = pd.read_json(EVALUATIONS_LOG, lines=True)
            if not eval_df.empty:
                live_mae = round(float(eval_df["absolute_error_c"].mean()), 2)
                if cache and live_mae is not None:
                    cache.setex(mae_cache_key, CACHE_TTL_PREDICT, str(live_mae))
        except Exception as e:
            logger.warning(f"Could not parse evaluations log: {e}")

    redis_type_str = "none"
    if cache:
        redis_type_str = type(cache).__name__ 

    return {
        "status": "healthy" if (pipe is not None and redis_status) else "degraded",
        "redis_connected": redis_status,
        "redis_type": redis_type_str,
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