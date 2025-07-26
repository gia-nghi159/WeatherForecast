#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from scripts.preprocessing import clean_and_engineer_features
import joblib

df = pd.read_csv('data/export(1).csv')
df = clean_and_engineer_features(df)

target_cols = [f"target_{i}" for i in range(1,8)]
X = df.drop(columns=target_cols)
y = df[target_cols]

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', Lasso(alpha=0.1))
])
pipe.fit(X, y)

joblib.dump(pipe, 'app/model/dallas_fw.joblib')
print("✅ Model retrained and saved.")

y_pred = pipe.predict(X)
for i, target in enumerate(target_cols):
    mae = mean_absolute_error(y[target], y_pred[:, i])
    r2 = r2_score(y[target], y_pred[:, i])
    print(f"Day {i+1}: MAE = {mae:.2f}, R² = {r2:.3f}")