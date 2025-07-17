import pandas as pd

def pct_diff(old,new):
    return (new - old) / old 

def compute_rolling(df,horizon,col):
    label = f"rolling_{horizon}_{col}"
    df[label] = df[col].rolling(horizon).mean()
    df[f"{label}_pct"] = pct_diff(df[label], df[col])
    return df

def expand_mean(df):
    return df.expanding().mean()

def preprocess_input(df):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # Compute rolling means and percentage differences
    for horizon in [3, 14]:
        for col in ['tmax', 'tmin','prcp']:
            df = compute_rolling(df, horizon, col)
    
    df = df.iloc[14:]  # Drop the first 14 rows to avoid NaN values from rolling calculations
    df = df.fillna(0)
    
    # Compute expanding means
    for col in ['tmax', 'tmin','prcp']:
        df[f"month_avg_{col}"] = df[col].groupby(df.index.month, group_keys=False).transform(expand_mean)
        df[f"day_avg_{col}"] = df[col].groupby(df.index.day_of_year, group_keys=False).transform(expand_mean)
    return df
