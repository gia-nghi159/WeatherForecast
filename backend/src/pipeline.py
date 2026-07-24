import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import redis
import fakeredis
from meteostat import Daily, Hourly

from src.config import (
    DAILY_CSV,
    DALLAS_POINT,
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
        if REDIS_URL:
            r = redis.from_url(REDIS_URL, decode_responses=True)
        else:
            # Use fakeredis locally if REDIS_URL isn't set
            r = fakeredis.FakeRedis(decode_responses=True)

        keys = r.keys(pattern)
        if keys:
            r.delete(*keys)
            logger.info(f"Evicted {len(keys)} stale cache key(s) matching '{pattern}'.")
    except Exception as e:
        logger.warning(f"Could not clear Redis cache: {e}")


def evaluate_ground_truth():
    """Prunes predictions older than RETENTION_DAYS, deduplicates repeated same-day runs,
    and matches remaining latest predictions against actual ground truth."""
    if not PREDICTIONS_LOG.exists() or not DAILY_CSV.exists():
        return

    cutoff_date = datetime.now().date() - timedelta(days=RETENTION_DAYS)

    # Load actual daily observations
    daily_df = pd.read_csv(DAILY_CSV)
    daily_df["date"] = pd.to_datetime(daily_df["date"]).dt.strftime("%Y-%m-%d")
    actuals = dict(zip(daily_df["date"], daily_df["tmax"]))

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
    # Using a dictionary keyed by (predicted_at, target_date) keeps the last seen entry
    latest_predictions_map = {}
    for entry in valid_predictions:
        key = (entry["predicted_at"], entry["target_date"])
        latest_predictions_map[key] = entry  # Overwrites earlier runs from the same day!

    deduped_predictions = list(latest_predictions_map.values())

    # 3. Clean up predictions_log.jsonl on disk to remove duplicates
    with open(PREDICTIONS_LOG, "w") as f:
        for entry in deduped_predictions:
            f.write(json.dumps(entry) + "\n")

    # 4. Match latest predictions against ground truth
    evaluations = []
    for p in deduped_predictions:
        target_date = p["target_date"]
        if target_date in actuals:
            actual_tmax_c = actuals[target_date]
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
        with open(EVALUATIONS_LOG, "w") as f:
            for ev in evaluations:
                f.write(json.dumps(ev) + "\n")

        avg_mae = sum(e["absolute_error_c"] for e in evaluations) / len(evaluations)
        logger.info(
            f"Ground Truth Evaluation Complete! Evaluated {len(evaluations)} unique target dates. "
            f"Live Production MAE: {avg_mae:.2f}°C"
        )

def update_daily_data():
    """Fetches missing daily weather observations and triggers evaluation + cache invalidation."""
    if not DAILY_CSV.exists():
        logger.error(f"File not found: {DAILY_CSV}")
        return

    evaluate_ground_truth()

    df = pd.read_csv(DAILY_CSV)
    df["date"] = pd.to_datetime(df["date"])
    last_date = df["date"].max()

    start = last_date + timedelta(days=1)
    end = pd.Timestamp(datetime.today().date() - timedelta(days=1))

    if start >= end:
        logger.info("Daily data is already up to date.")
        return

    try:
        new_data = Daily(DALLAS_POINT, start, end).fetch().reset_index()
        if not new_data.empty:
            new_data = new_data.dropna(how="all")
            new_data["date"] = pd.to_datetime(new_data["time"].dt.date)
            new_data.drop(columns=["time"], inplace=True)

            df = (
                pd.concat([df, new_data])
                .drop_duplicates(subset="date")
                .sort_values("date")
            )
            df = df[df["date"] >= (df["date"].max() - pd.Timedelta(days=1095))]
            df.to_csv(DAILY_CSV, index=False)
            logger.info(f"Appended {len(new_data)} new daily rows.")

            # Invalidate Forecast Cache
            clear_redis_cache("weather:predict:*")
    except Exception as e:
        logger.error(f"Error fetching daily data: {e}")


def update_hourly_data():
    """Fetches latest hourly observation and evicts current weather cache."""
    local_now = datetime.now(ZoneInfo("America/Chicago")).replace(
        minute=0, second=0, microsecond=0
    )
    end_utc = local_now.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    start_utc = end_utc - timedelta(hours=1)

    try:
        df = Hourly(DALLAS_POINT, start_utc, end_utc).fetch().reset_index()
        if not df.empty:
            latest = df.tail(1)
            latest.to_csv(HOURLY_CSV, index=False)
            logger.info(f"Saved latest hourly observation: {latest.iloc[0]['time']}")
            
            # Evict current weather cache so users get the fresh reading
            clear_redis_cache("weather:today:*")
    except Exception as e:
        logger.error(f"Error fetching hourly data: {e}")


if __name__ == "__main__":
    # Read the argument passed from GitHub Actions command line
    command = sys.argv[1] if len(sys.argv) > 1 else "all"

    if command == "hourly":
        logger.info("Executing hourly telemetry fetch...")
        update_hourly_data()

    elif command == "daily":
        logger.info("Executing daily data update & ground-truth evaluation...")
        update_daily_data()  # Calls evaluate_ground_truth() inside it!

    else:
        logger.info("Executing full pipeline update...")
        update_daily_data()
        update_hourly_data()