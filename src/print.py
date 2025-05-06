from escpos.printer import Usb
from datetime import datetime
import textwrap

from puzzle import create_puzzle
from util import get_weather, map_weather_code
from rss import NewsType, getRSS
import json

def print_newsletter():

    debug = True
    
    create_puzzle()

    if not debug:
        """ Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
        p = Usb(0x04b8, 0x0e28, 0)
    else:
        p = None

        print_header(p, debug)
        print_news(p, NewsType.LOCAL, debug)
        print_news(p, NewsType.WORLD, debug)
        print_weather(p, debug)
        if not debug:
            print_puzzle(p)
            p.cut()

def print_news(p, url, debug):
    if debug:
        print("World News" if url == NewsType.WORLD else "Local News")
    else:
        p.set(custom_size=True, width=2, height=2)
        p.text("World News" if url == NewsType.WORLD else "Local News")

    response = getRSS(url)
    articles = response["rss"]["channel"]["item"]
    for article in articles[:5]:
        if debug:
            print(article["title"])
            print(article["description"])
        else:
            p.set(invert=True, custom_size=True, width=1, height=1)
            p.text(article["title"])

            p.set(invert=False, custom_size=True, width=1, height=1)
            p.text(article["description"])
    

def print_weather(p, debug):

    if debug:
        print("Weather")
    else:
        p.set(custom_size=True, width=2, height=2)
        p.text("Weather")

    weather_data = get_weather()
    widths = [12, 16, 6, 6, 6]
    aligns = ['left', 'center', 'right', 'right', 'right']

    if debug:
        print(["Date", "Summary", "Precipitation", "High", "Low"])
    else:
        p.software_columns(["Date", "Summary", "Precipitation", "High", "Low"], widths, aligns)

    daily = weather_data['daily']
    units = weather_data['daily_units']
    for i in range(len(daily)):
        weather_line = [
            daily['time'][i],
            map_weather_code(daily['weather_code'][i]),
            f"{daily['precipitation_sum'][i] }{ units['precipitation_sum']}" if daily['precipitation_sum'][i] > 0 else '---',
            f"{daily['temperature_2m_max'][i]}{units['temperature_2m_max']}",
            f"{daily['temperature_2m_min'][i]}{units['temperature_2m_min']}", 
        ]
        if debug:
            print(weather_line)
        else:
            p.software_columns(weather_line, widths, aligns)
    
    if not debug:
        p.set(normal_textsize=True)

def print_header(p, debug):
    today = datetime.today()
    if debug:
        print(today.strftime('%A %-m, %B %Y'))
    else:
        p.set(custom_size=True, width=2, height=2)
        p.image("logo.png")
        p.text(today.strftime('%A %-m, %B %Y'))

def print_puzzle(p):
    title = "How to play:\n"
    desc = "Place a letter into the blank space in such a way that it completes the word. The word can start in any position and could go in either direction."

    p.set(custom_size=True, width=2, height=2)
    p.text("Daily Wordwheel")
    p.image("puzzle.png")
    p.text(title)
    p.print_and_feed(1)
    p.set(normal_textsize=True)
    lines = textwrap.wrap(desc, 48)
    for line in lines :
        p.textln(line)

print_newsletter()