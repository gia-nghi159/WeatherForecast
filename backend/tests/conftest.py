import pytest
import pandas as pd
from fastapi.testclient import TestClient
from src.main import app
from src.config import DAILY_CSV

@pytest.fixture(scope="module")
def client():
    """Provides a reusable FastAPI TestClient instance across all test modules."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
def sample_daily_df():
    """Dynamically loads a 60-row slice of actual CSV data for preprocessing tests."""
    if DAILY_CSV.exists():
        return pd.read_csv(DAILY_CSV).head(60)
    # Fallback mock data if CSV isn't present
    return pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=60, freq="D"),
        "tavg": [20.0] * 60,
        "tmax": [25.0] * 60,
        "tmin": [15.0] * 60,
        "prcp": [0.0] * 60,
    })