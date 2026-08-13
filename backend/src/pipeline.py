import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import redis
import fakeredis
import requests

from src.config import (
    DAILY_CSV,
    DALLAS_LAT,
    DALLAS_LON,
    EVALUATIONS_LOG,
    HOURLY_CSV,
    PREDICTIONS_LOG,
    REDIS_URL,
    RETENTION_DAYS,
    logger,
)

def clear_redis_cache(pattern: str = "weather:*"):
    """Flushes matching prediction/hourly caches when fresh telemetry is ingested."""
    try:
        target_url = REDIS_URL or "redis://localhost:6379"
        r = redis.from_url(target_url, decode_responses=True)
        r.ping()
        
        keys = r.keys(pattern)
        if keys:
            r.delete(*keys)
            logger.info(f"Evicted {len(keys)} stale cache key(s) matching '{pattern}'.")
    except Exception as e:
        logger.warning(f"Could not clear Redis cache ({e}). Using FakeRedis fallback.")
        try:
            r = fakeredis.FakeRedis(decode_responses=True)
            keys = r.keys(pattern)
            if keys:
                r.delete(*keys)
        except Exception:
            pass


def evaluate_ground_truth():
    """Prunes predictions older than RETENTION_DAYS, deduplicates repeated same-day runs,
    and matches remaining latest predictions against actual ground truth."""
    if not PREDICTIONS_LOG.exists() or not DAILY_CSV.exists():
        return

    cutoff_date = datetime.now().date() - timedelta(days=RETENTION_DAYS)

    # Load actual daily observations
    daily_df = pd.read_csv(DAILY_CSV)
    daily_df["date"] = pd.to_datetime(daily_df["date"]).dt.strftime("%Y-%m-%d")
    
    # Filter out missing/NaN ground truth observations
    valid_daily = daily_df.dropna(subset=["tmax"])
    actuals = dict(zip(valid_daily["date"], valid_daily["tmax"]))

    valid_predictions = []
    pruned_count = 0

    # 1. Prune logs older than RETENTION_DAYS (90 days)
    with open(PREDICTIONS_LOG, "r") as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                pred_date = datetime.strptime(
                    entry["predicted_at"], "%Y-%m-%d"
                ).date()

                if pred_date >= cutoff_date:
                    valid_predictions.append(entry)
                else:
                    pruned_count += 1

    if pruned_count > 0:
        logger.info(
            f"Log Retention: Pruned {pruned_count} prediction entries older than {RETENTION_DAYS} days."
        )

    # 2. Deduplicate: Keep only the MOST RECENT prediction for each (predicted_at, target_date)
    latest_predictions_map = {}
    for entry in valid_predictions:
        key = (entry["predicted_at"], entry["target_date"])
        latest_predictions_map[key] = entry  # Overwrites earlier runs from the same day

    deduped_predictions = list(latest_predictions_map.values())

    # 3. Clean up predictions_log.jsonl on disk
    with open(PREDICTIONS_LOG, "w") as f:
        for entry in deduped_predictions:
            f.write(json.dumps(entry) + "\n")

    # 4. Match latest predictions against ground truth
    evaluations = []
    for p in deduped_predictions:
        target_date = p["target_date"]
        if target_date in actuals and pd.notna(actuals[target_date]):
            actual_tmax_c = float(actuals[target_date])
            error_c = abs(p["predicted_tmax_c"] - actual_tmax_c)
            evaluations.append(
                {
                    "evaluated_at": str(datetime.now().date()),
                    "target_date": target_date,
                    "horizon_days": p["horizon_days"],
                    "predicted_tmax_c": p["predicted_tmax_c"],
                    "actual_tmax_c": actual_tmax_c,
                    "absolute_error_c": round(error_c, 2),
                    "model_version": p["model_version"],
                }
            )

    # Save evaluation summary
    if evaluations:
        EVALUATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(EVALUATIONS_LOG, "w") as f:
            for ev in evaluations:
                f.write(json.dumps(ev) + "\n")

        avg_mae = sum(e["absolute_error_c"] for e in evaluations) / len(evaluations)
        logger.info(
            f"Ground Truth Evaluation Complete! Evaluated {len(evaluations)} unique target dates. "
            f"Live Production MAE: {avg_mae:.2f}°C"
        )


def fetch_open_meteo_daily(start_date: str, end_date: str) -> pd.DataFrame:
    """Queries Open-Meteo Historical Archive API and returns a structured DataFrame."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": DALLAS_LAT,
        "longitude": DALLAS_LON,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum",
        "timezone": "America/Chicago",
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    daily_data = data.get("daily", {})
    if not daily_data or "time" not in daily_data:
        return pd.DataFrame()

    df = pd.DataFrame({
        "date": pd.to_datetime(daily_data["time"]),
        "tmax": daily_data["temperature_2m_max"],
        "tmin": daily_data["temperature_2m_min"],
        "tavg": daily_data["temperature_2m_mean"],
        "prcp": daily_data["precipitation_sum"],
    })
    return df


def update_daily_data():
    """Fetches missing daily weather observations from Open-Meteo,
    updates DAILY_CSV, and triggers evaluation + cache invalidation.
    """
    end_date = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Step 1: Self-Healing Bootstrap if DAILY_CSV is missing
    if not DAILY_CSV.exists():
        logger.info(f"{DAILY_CSV} not found. Bootstrapping 3 years of historical data from Open-Meteo API...")
        start_date = (datetime.now().date() - timedelta(days=1095)).strftime("%Y-%m-%d")
        try:
            df = fetch_open_meteo_daily(start_date, end_date)
            if not df.empty:
                DAILY_CSV.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(DAILY_CSV, index=False)
                logger.info(f"Successfully bootstrapped {DAILY_CSV} with {len(df)} rows from Open-Meteo API.")
            else:
                logger.error("Open-Meteo returned empty data during bootstrap.")
                return
        except Exception as e:
            logger.error(f"Error bootstrapping daily data: {e}")
            return

    # Step 2: Incremental Fetch for Existing CSV
    df = pd.read_csv(DAILY_CSV)
    df["date"] = pd.to_datetime(df["date"])
    last_date = df["date"].max().date()
    start_date_obj = last_date + timedelta(days=1)
    end_date_obj = datetime.now().date() - timedelta(days=1)

    if start_date_obj <= end_date_obj:
        try:
            s_str = start_date_obj.strftime("%Y-%m-%d")
            e_str = end_date_obj.strftime("%Y-%m-%d")
            logger.info(f"Fetching missing observations from {s_str} to {e_str} via Open-Meteo API...")
            
            new_data = fetch_open_meteo_daily(s_str, e_str)
            if not new_data.empty:
                df = (
                    pd.concat([df, new_data])
                    .drop_duplicates(subset="date")
                    .sort_values("date")
                )
                # Apply 3-year sliding retention window (1,095 days)
                df = df[df["date"] >= (df["date"].max() - pd.Timedelta(days=1095))]
                df.to_csv(DAILY_CSV, index=False)
                logger.info(f"Appended {len(new_data)} new daily row(s).")

                # Invalidate Forecast Cache
                clear_redis_cache("weather:predict:*")
        except Exception as e:
            logger.error(f"Error fetching daily data from Open-Meteo: {e}")
    else:
        logger.info("Daily data is already up to date.")

    # Step 3: Run Evaluation AFTER ground truth data is updated
    evaluate_ground_truth()


def update_hourly_data():
    """Evicts stale current weather cache so users get a fresh reading on the next request."""
    logger.info("Evicting current weather cache...")
    clear_redis_cache("weather:today:*")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "all"

    if command == "hourly":
        logger.info("Executing hourly telemetry fetch...")
        update_hourly_data()

    elif command == "daily":
        logger.info("Executing daily data update & ground-truth evaluation...")
        update_daily_data()

    else:
        logger.info("Executing full pipeline update...")
        update_daily_data()
        update_hourly_data()