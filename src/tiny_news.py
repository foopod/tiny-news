from escpos.printer import Usb
from datetime import datetime
import textwrap

from puzzles import puzzle_from_api
from util import get_weather, map_weather_code, center_pad, print_heading, escpos_row, date_to_weekday, left_pad_strings, unicode_to_ascii
from rss import NewsType, getRSS
from daily_word import print_daily_word
import json

def print_rick_roll():
    p = Usb(0x04b8, 0x0e28, 0)
    # https://www.youtube.com/watch?v=dQw4w9WgXcQ
    p.qr("https://www.youtube.com/watch?v=dQw4w9WgXcQ", size=16)
    p.cut()
    p.close()

def print_weather_only():
    p = Usb(0x04b8, 0x0e28, 0)
    print_weather(p)
    p.cut()
    p.close()

def print_puzzle_only():
    p = Usb(0x04b8, 0x0e28, 0)
    puzzle_from_api(p)
    p.cut()
    p.close()

def print_newsletter():

    """ Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
    p = Usb(0x04b8, 0x0e28, 0)

    print_header(p)
    print_news(p, NewsType.LOCAL)
    print_weather(p)
    try:
        puzzle_from_api(p)
    except Exception as e:
        print(e)
        print('oh no')
    print_daily_word(p)
    p.print_and_feed(1)
    print_heading(p, f"Feedback")
    p.textln('Raise an Issue or Pull Request on Github')
    p.textln('https://github.com/foopod/tiny-news')
    p.qr("https://github.com/foopod/tiny-news", size=8)
    p.cut()
    p.close()

def print_news(p, newsType, print_title = True):
    if newsType == NewsType.WORLD:
        print_heading(p, "More News")
        p.print_and_feed(2)
        lines = textwrap.wrap("Help me find more sources of news. RSS feeds are best, but APIs could also work.", 48)
        for line in lines :
            p.textln(line)
        p.print_and_feed(1)
        return

    if print_title:
        p.set(custom_size=True, width=2, height=2, invert=True)
        p.textln(center_pad(f"{newsType} News", 24))

    url = NewsType.NewsMap[newsType]
    response = getRSS(url)
    articles = response["rss"]["channel"]["item"]
    for article in articles[:5]:
        p.set(bold=True, custom_size=True, width=1, height=1, invert=False)
        lines = textwrap.wrap(unicode_to_ascii(article["title"]), 48)
        for line in lines :
            p.textln(line)
        p.set(bold=False, custom_size=True, width=1, height=1)
        lines = textwrap.wrap(unicode_to_ascii(article["description"]), 48)
        for line in lines :
            p.textln(line)
    

def print_weather(p):
    print_heading(p, "Weather")

    weather_data = get_weather()
    widths = [8, 14, 10, 8, 8]
    aligns = ['left', 'center', 'right', 'right', 'right']
    headers = ["Day", "Summary", "Rain", "Low", "High"]

    # p.software_columns(headers, widths, aligns)
    p.set(bold=True, underline=1)
    p.text(escpos_row(headers, widths) + "\n")
    p.set(bold=False, underline=0, custom_size=False, width=1, height=1)

    daily = weather_data['daily']
    units = weather_data['daily_units']
    # units["temperature_2m_max"] = "°C"
    # units["temperature_2m_min"] = chr(248)
    daily["temperature_2m_max"] = left_pad_strings(daily["temperature_2m_max"])
    daily["temperature_2m_min"] = left_pad_strings(daily["temperature_2m_min"])
    for i in range(len(daily["temperature_2m_max"])):
        weather_line = [
            date_to_weekday(daily['time'][i]),
            map_weather_code(daily['weather_code'][i]),
            f"{daily['precipitation_sum'][i] }{ units['precipitation_sum']}" if daily['precipitation_sum'][i] > 0 else '---',
            f"{daily['temperature_2m_min'][i]}{units['temperature_2m_min']}", 
            f"{daily['temperature_2m_max'][i]}{units['temperature_2m_max']}",
        ]
        # p.software_columns(weather_line, widths, aligns)
        p.text(escpos_row(weather_line, widths) + "\n")

def print_header(p):
    today = datetime.today()
    p.set(align="center")
    p.textln(today.strftime('%A %d, %B %Y'))
    p.set(align="left")

if __name__ == "__main__":
    print_newsletter()