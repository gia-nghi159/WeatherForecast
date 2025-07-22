import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from scripts.preprocessing import clean_and_engineer_features
import joblib

df = pd.read_csv('data/export(1).csv')
df = clean_and_engineer_features(df)

target_cols = [f"target_{i}" for i in range(1,8)]
X = df.drop(columns=target_cols)
y = df[target_cols]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = Lasso(alpha=0.1)
model.feature_names_in_ = X.columns
model.fit(X_scaled, y)

joblib.dump(model, 'app/model/dallas_fw.joblib')
joblib.dump(X.columns.tolist(), 'app/model/7_days_features.pkl')
joblib.dump(scaler, 'app/model/7_days_scaler.pkl')


print("✅ Model retrained and saved.")

y_pred = model.predict(X_scaled)
for i, target in enumerate(target_cols):
    mae = mean_absolute_error(y[target], y_pred[:, i])
    r2 = r2_score(y[target], y_pred[:, i])
    print(f"Day {i+1}: MAE = {mae:.2f}, R² = {r2:.3f}")