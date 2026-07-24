from typing import Dict, Optional
from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    prediction_7day_tmax: Dict[str, float] = Field(
        ...,
        alias="7_day_tmax_prediction",
        description="7-day maximum temperature forecast",
    )
    units: str
    model_version: str
    status: str = "success"

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "7_day_tmax_prediction": {"day_1": 98.6, "day_2": 97.5},
                "units": "°F",
                "model_version": "lasso_v1.0",
                "status": "success",
            }
        },
    }


class TodayWeatherResponse(BaseModel):
    datetime: str
    temp: float
    prcp: float
    wspd: float
    wdir: float
    pres: float
    units: str
    status: str = "success"


class HealthStatusResponse(BaseModel):
    status: str
    redis_connected: bool
    model_loaded: bool
    model_version: str
    live_production_mae_c: Optional[float] = None