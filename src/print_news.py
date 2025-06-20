from escpos.printer import Usb
from datetime import datetime
import textwrap

from puzzle_api import puzzle_from_api
from print_ships import print_ship
from puzzle import create_puzzle
from util import get_weather, map_weather_code, center_pad, print_heading
from rss import NewsType, getRSS
import json

def print_rick_roll():
    p = Usb(0x04b8, 0x0e28, 0)
    # https://www.youtube.com/watch?v=dQw4w9WgXcQ
    p.qr("https://www.youtube.com/watch?v=dQw4w9WgXcQ", size=16)
    p.cut()
    p.close()

def print_weather_only():
    p = Usb(0x04b8, 0x0e28, 0)
    # https://www.youtube.com/watch?v=dQw4w9WgXcQ
    print_weather(p)
    p.cut()
    p.close()

def puzzle_only():
    p = Usb(0x04b8, 0x0e28, 0)
    # https://www.youtube.com/watch?v=dQw4w9WgXcQ
    puzzle_from_api(p)
    p.cut()
    p.close()

def ship_only():
    p = Usb(0x04b8, 0x0e28, 0)
    print_ship(p)
    p.cut()
    p.close()


def print_newsletter():
    debug = False
    create_puzzle()
    

    if not debug:
        """ Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
        p = Usb(0x04b8, 0x0e28, 0)
        # p._raw(b'\x1B\x74\x00') 
    else:
        p = None

    # p.text("Temp: 25°C\n")
    # print_ship(p)
    print_header(p, debug)
    print_news(p, NewsType.LOCAL)
    # print_news(p, NewsType.WORLD)
    # print_news_combined(p, [NewsType.SCIENCE, NewsType.TECH])
    print_weather(p, debug)
    puzzle_from_api(p)
    if not debug:
        # print_puzzle(p)
        p.print_and_feed(1)
        print_heading(p, f"Feedback")
        p.text('    ')
        p.qr("https://forms.gle/FJkGxqHVShBy3kD27", size=8)
        p.cut()
        p.close()
    
def escpos_row(row, widths):
    padded = [str(col)[:w].ljust(w) for col, w in zip(row, widths)]
    return "".join(padded)

def date_to_weekday(date_str: str) -> str:
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%a %d")

def left_pad_strings(strings: list[str], pad_char: str = " ") -> list[str]:
    max_len = max(len(f"{s}") for s in strings)
    return [f"{s}".rjust(max_len, pad_char) for s in strings]

def print_news_combined(p, newsList):
    p.set(custom_size=True, width=2, height=2, invert=True)
    p.textln(center_pad(f"{' & '.join(newsList)} News", 24))
    for news in newsList:
        print_news(p, news, False)

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
        lines = textwrap.wrap(article["title"], 48)
        for line in lines :
            p.textln(line)
        p.set(bold=False, custom_size=True, width=1, height=1)
        lines = textwrap.wrap(article["description"], 48)
        for line in lines :
            p.textln(line)
    

def print_weather(p, debug = False):
    if debug:
        print("Weather")
    else:
        print_heading(p, "Weather")

    weather_data = get_weather()
    widths = [8, 14, 10, 8, 8]
    aligns = ['left', 'center', 'right', 'right', 'right']
    headers = ["Day", "Summary", "Rain", "Low", "High"]

    if debug:
        print(headers)
    else:
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
        if debug:
            print(weather_line)
        else:
            # p.software_columns(weather_line, widths, aligns)
            p.text(escpos_row(weather_line, widths) + "\n")

def print_header(p, debug):
    today = datetime.today()
    if debug:
        print(today.strftime('%A %d, %B %Y'))
    else:
        # p.image("images/logo.png")
        p.set(align="center")
        p.textln(today.strftime('%A %d, %B %Y'))
        p.set(align="left")

def print_puzzle(p):
    title = "How to play:\n"
    desc = "Place a letter into the blank space in such a way that it completes the word. The word can start in any position and could go in either direction."

    print_heading(p, "Daily Wordwheel")
    p.image("puzzle.png", impl='bitImageRaster')
    p.set(bold=True)
    p.text(title)
    p.set(bold=False)
    lines = textwrap.wrap(desc, 48)
    for line in lines :
        p.textln(line)

if __name__ == "__main__":
    print_newsletter()