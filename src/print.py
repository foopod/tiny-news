from escpos.printer import Usb
from datetime import datetime
import textwrap

from puzzle import create_puzzle

def print_newsletter():
    
    create_puzzle()

    """ Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
    p = Usb(0x04b8, 0x0e28, 0)
    print_header(p)
    print_puzzle(p)
    p.cut()

def print_news():
    pass

def print_weather():
    pass

def print_header(p):
    today = datetime.today()
    p.set(custom_size=True, width=2, height=2)
    p.image("logo.png")
    p.text(today.strftime('%d-%m-%Y'))

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