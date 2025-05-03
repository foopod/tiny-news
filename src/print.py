# from escpos.printer import Usb
from datetime import datetime, timedelta
# import textwrap
import requests
import json
import pandas as pd


from puzzle import create_puzzle

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
        'temps': data.hourly.temperature_2m,
        'rain': data.hourly.precipitation
        }, index=data.hourly.time)

    print(df)
    df.plot.line()

    return json.loads(response)

def print_newsletter():
    today = datetime.today()

    create_puzzle()

    """ Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
    p = Usb(0x04b8, 0x0e28, 0)
    
    p.cut()

def print_header():
    p.set(custom_size=True, width=2, height=2)
    p.image("logo.png")
    p.text(today.strftime('%d-%m-%Y'))

def print_puzzle():
    title = "How to play:\n"
    desc = "Place a letter into the blank space in such a way that it completes the word. The word can start in any position and could go in either direction."

    p.set(custom_size=True, width=2, height=2)
    p.image("puzzle.png")
    p.text(title)
    p.print_and_feed(1)
    p.set(normal_textsize=True)
    lines = textwrap.wrap(desc, 48)
    for line in lines :
        p.textln(line)