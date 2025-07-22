import pandas as pd
from meteostat import Point, Daily
from datetime import datetime, timedelta

location = Point(32.7831, -96.8067) # Dallas, TX

csv_path = 'data/export(1).csv'
df = pd.read_csv(csv_path)

df['date'] = pd.to_datetime(df['date'])
last_date = df['date'].max()

start = last_date + timedelta(days=1)
end = datetime.now()

if start >= end:
    print("Already up to date")
else:
    try:
        new_data = Daily(location, start, end)
        new_data = new_data.fetch().reset_index()
        
    
        if not new_data.empty:
            new_data = new_data.dropna(how='all')
            if not new_data.empty:
                new_data['date'] = pd.to_datetime(new_data['time'].dt.date)
                new_data.drop(columns=['time'], inplace=True) 
                df = pd.concat([df, new_data]).drop_duplicates(subset='date').sort_values('date')
                df = df[df['date'] >= (df['date'].max() - pd.Timedelta(days=1095))]
                df.to_csv(csv_path, index=False)
                print(f"Appended {len(new_data)} new rows to export.csv")
            else:
                print("New data was all-NA, nothing to append.")
        else:
            print("No new data to append")
    except Exception as e:
        print("❌ Error fetching data:", e)
        exit()

