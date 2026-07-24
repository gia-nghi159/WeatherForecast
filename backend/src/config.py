import logging
import os
from pathlib import Path
from meteostat import Point

# Paths
SRC_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SRC_DIR.parent

DATA_DIR = BACKEND_DIR / "data"
MODELS_DIR = BACKEND_DIR / "models"

DAILY_CSV = DATA_DIR / "meteostat_export.csv"
HOURLY_CSV = DATA_DIR / "hourly_data.csv"
MODEL_PATH = MODELS_DIR / "dallas_fw.joblib"

# MLOps & Evaluation Logs
PREDICTIONS_LOG = DATA_DIR / "predictions_log.jsonl"
EVALUATIONS_LOG = DATA_DIR / "evaluations_log.jsonl"
RETENTION_DAYS = 90  # Keep a 90-day window for active log evaluation

# Redis Configuration
# If REDIS_URL is set (in Production), use it. Otherwise, None signals main.py to use fakeredis!
REDIS_URL = os.getenv("REDIS_URL", None)

CACHE_TTL_TODAY = 3600     # 1 hour (3,600 seconds)
CACHE_TTL_PREDICT = 86400  # 24 Hours (86,400 seconds)

# Location Settings (Dallas, TX)
DALLAS_LAT = 32.7831
DALLAS_LON = -96.8067
DALLAS_POINT = Point(DALLAS_LAT, DALLAS_LON)

# Model Metadata
MODEL_VERSION = "lasso_v1.0"

# Centralized Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("weather_api")