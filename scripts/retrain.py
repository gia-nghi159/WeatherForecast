import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_absolute_error
import joblib

df = pd.read_csv('../data/export.csv')
df.set_index('date', inplace=True)
df.drop(columns=['snow','wdir','wpgt','tsun','prcp','wspd'],inplace=True)
df.dropna(subset=['tavg','tmin','tmax','pres'],inplace=True)
df['target'] = df.shift(-1)['tmax']
df = df.ffill()

X = df[['tavg', 'tmax', 'tmin', 'pres']]  # or whatever features you selected
y = df['target']

model = Lasso(alpha=0.1)
model.fit(X, y)

joblib.dump(model, '../app/model/lasso_model.joblib')
print("✅ Model retrained and saved.")

y_pred = model.predict(X)
mae = mean_absolute_error(y, y_pred)
print(f"📈 MAE after retraining: {mae:.2f}")