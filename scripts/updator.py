import pandas as pd
from meteostat import Point, Daily
from datetime import datetime, timedelta

location = Point(32.9537, -96.8903) #Carrollton, TX

csv_path = '../data/export.csv'
df = pd.read_csv(csv_path)

df['date'] = pd.to_datetime(df['date'])
last_date = df['date'].max()

start = last_date + timedelta(days=1)
end = datetime.now()

if start >= end:
    print("Already up to date")
else:
    new_data = Daily(location, start, end)
    new_data = new_data.fetch().reset_index()
 
    if not new_data.empty:
        new_data['date'] = pd.to_datetime(new_data['time'].dt.date)
        new_data.drop(columns=['time'], inplace=True) 
        new_df = pd.concat([df, new_data], ignore_index=True)
        new_df.to_csv(csv_path, index=False)
        print(f"Appended {len(new_data)} new rows to meteostat.csv")
    else:
        print("No new data to append")

