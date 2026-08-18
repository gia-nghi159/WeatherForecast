import numpy as np
import pandas as pd


def clean_and_engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocesses raw weather data and generates rolling/expanding historical features."""
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index(df["date"]).copy()
    df.drop(
        columns=["date", "snow", "wdir", "wpgt", "tsun"],
        inplace=True,
        errors="ignore",
    )
    df["prcp"] = df["prcp"].ffill().bfill().fillna(0)

    # Generate 7-day targets
    for i in range(1, 8):
        df[f"target_{i}"] = df["tmax"].shift(-i)
    df = df.ffill()

    def pct_diff(old, new):
        # Safe division: Return 0.0 if old value is 0
        return np.where(old != 0, (new - old) / old, 0.0)

    def compute_rolling(df_in, horizon, col):
        label = f"rolling_{horizon}_{col}"
        df_in[label] = df_in[col].rolling(horizon).mean()
        df_in[f"{label}_pct"] = pct_diff(df_in[label], df_in[col])
        return df_in

    # Rolling averages (7-day and 14-day)
    for horizon in [7, 14]:
        for col in ["tavg", "tmax", "tmin", "prcp"]:
            df = compute_rolling(df, horizon, col)

    df = df.iloc[14:, :]
    df = df.ffill()

    # Monthly and Daily expanding averages
    def expand_mean(group):
        return group.expanding().mean()

    for col in ["tavg", "tmax", "tmin", "prcp"]:
        df[f"month_avg_{col}"] = df[col].groupby(
            df.index.month, group_keys=False
        ).transform(expand_mean)
        df[f"day_avg_{col}"] = df[col].groupby(
            df.index.day_of_year, group_keys=False
        ).transform(expand_mean)

    df = df.replace([np.inf, -np.inf], 0.0).fillna(0.0)
    return df