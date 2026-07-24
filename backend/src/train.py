import joblib
import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import DAILY_CSV, MODEL_PATH, logger
from src.preprocessing import clean_and_engineer_features


def train():
    logger.info("Starting model training pipeline...")
    if not DAILY_CSV.exists():
        raise FileNotFoundError(f"Training dataset missing at {DAILY_CSV}")

    df = pd.read_csv(DAILY_CSV)
    df = clean_and_engineer_features(df)

    target_cols = [f"target_{i}" for i in range(1, 8)]
    X = df.drop(columns=target_cols)
    y = df[target_cols]

    pipe = Pipeline(
        [("scaler", StandardScaler()), ("model", Lasso(alpha=0.1))]
    )
    pipe.fit(X, y)

    # Ensure output model directory exists
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    logger.info(f"Model saved to {MODEL_PATH}")

    # Evaluate
    y_pred = pipe.predict(X)
    for i, target in enumerate(target_cols):
        mae = mean_absolute_error(y[target], y_pred[:, i])
        r2 = r2_score(y[target], y_pred[:, i])
        logger.info(f"Day {i+1}: MAE = {mae:.2f}°C, R² = {r2:.3f}")


if __name__ == "__main__":
    train()