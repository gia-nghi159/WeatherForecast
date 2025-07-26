import pandas as pd
from meteostat import Point, Hourly
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo 

DALLAS = Point(32.7831, -96.8067)

local_now = datetime.now(ZoneInfo("America/Chicago")).replace(
    minute=0, second=0, microsecond=0
)
end_utc   = local_now.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
start_utc = end_utc - timedelta(hours=1)

df = Hourly(DALLAS, start_utc, end_utc).fetch().reset_index()

if df.empty:
    print("No hourly data available")
else:
    latest = df.tail(1)  # Keep only the most recent hour
    latest.to_csv('data/hourly_data.csv', index=False)
    print(f"✅ Saved {latest.iloc[0]['time']} to data/hourly_data.csv")