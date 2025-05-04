from datetime import datetime, timedelta
import pandas as pd
import requests

DAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]

def letters_day(date):
    date_format = "%Y-%m-%dT%H:%M"
    d = datetime.strptime(date, date_format)
    return DAYS[d.weekday()]

def get_weather():
    now = datetime.today()

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": -37.7833,
        "longitude": 175.2833,
        "hourly": ["temperature_2m", "precipitation"],
        "timezone": "Pacific/Auckland",
        "start_date": now.strftime('%Y-%m-%d'),
        "end_date": (now + timedelta(days=4)).strftime('%Y-%m-%d')
    }
    response = requests.get(url, params=params)
    data = response.json()
    print(data)

    df = pd.DataFrame({
        'temps': data["hourly"]["temperature_2m"],
        'rain': data["hourly"]["precipitation"]
    }, index=data["hourly"]["time"])

    

    print(df)
    df.index.map(letters_day)
    
    chart = df.plot.line()
    chart.figure.savefig('weather.png')