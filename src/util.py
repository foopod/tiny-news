from datetime import datetime, timedelta
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
        "daily": ["precipitation_sum", "temperature_2m_max", "temperature_2m_min", "weather_code"],
        "timezone": "Pacific/Auckland"
    }
    response = requests.get(url, params=params)
    data = response.json()

    return data
    
def map_weather_code(code):
    weather_mapping = {
        0: "Clear",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Fog",
        51: "Light Drizzle",
        53: "Drizzle",
        55: "Dense Drizzle",
        56: "Freezing Drizzle",
        57: "Freezing Drizzle",
        61: "Slight Rain",
        63: "Rain",
        65: "Heavy Rain",
        66: "Freezing Rain",
        67: "Freezing Rain",
        71: "Slight Snow",
        73: "Snow",
        75: "Heavy Snow",
        77: "Snow Grains",
        80: "Showers",
        81: "Showers",
        82: "Violent Showers",
        85: "Slight Snow",
        86: "Heavy Snow",
        95: "Thunderstorm",
        96: "Thunderstorm",
        99: "Thunderstorm"
    }
    
    return weather_mapping.get(code, "Unknown weather code")
