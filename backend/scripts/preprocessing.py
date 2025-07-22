import pandas as pd
import numpy as np

def clean_and_engineer_features(df):
    df['date'] = pd.to_datetime(df['date'])
    df.set_index(df['date'], inplace=True)
    df.drop(columns=['date', 'snow', 'wdir', 'wpgt', 'tsun'], inplace=True)
    df['prcp'].ffill().bfill()
    df['prcp'] = df['prcp'].fillna(0)

    for i in range(1, 8):
        df[f"target_{i}"] = df['tmax'].shift(-i)
    df = df.ffill()

    def pct_diff(old, new):
        return (new - old) / old

    def compute_rolling(df, horizon, col):
        label = f"rolling_{horizon}_{col}"
        df[label] = df[col].rolling(horizon).mean()
        df[f"{label}_pct"] = pct_diff(df[label], df[col])
        return df

    rolling_horizon = [7, 14]
    for horizon in rolling_horizon:
        for col in ['tavg', 'tmax', 'tmin', 'prcp']:
            df = compute_rolling(df, horizon, col)

    df = df.iloc[14:, :]
    df = df.ffill()

    def expand_mean(df):
        return df.expanding().mean()

    for col in ['tavg', 'tmax', 'tmin', 'prcp']:
        df[f"month_avg_{col}"] = df[col].groupby(df.index.month, group_keys=False).transform(expand_mean)
        df[f"day_avg_{col}"] = df[col].groupby(df.index.day_of_year, group_keys=False).transform(expand_mean)

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    return df
