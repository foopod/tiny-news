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
        "timezone": "Pacific/Auckland",
        "forecast_days": 7,
        "past_days": 0
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


def print_heading(p, header):
    p.set(custom_size=True, width=2, height=2, invert=True)
    p.text(center_pad(header, 24))
    p.set(custom_size=True, width=1, height=1, invert=False)

def center_pad(text, column_width):
    if column_width <= len(text):
        return text  # No padding needed or possible

    total_padding = column_width - len(text)
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding

    return ' ' * left_padding + text + ' ' * right_padding

def escpos_row(row, widths):
    padded = [str(col)[:w].ljust(w) for col, w in zip(row, widths)]
    return "".join(padded)

def date_to_weekday(date_str: str) -> str:
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%a %d")

def left_pad_strings(strings: list[str], pad_char: str = " ") -> list[str]:
    max_len = max(len(f"{s}") for s in strings)
    return [f"{s}".rjust(max_len, pad_char) for s in strings]