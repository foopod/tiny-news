from escpos.printer import Usb
import textwrap

title = "How to play:\n"
desc = "Place a letter into the blank space in such a way that it completes the word. The word can start in any position and could go in either direction."


def print_puzzle():
    """ Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
    p = Usb(0x04b8, 0x0e28, 0)
    p.set(custom_size=True, width=2, height=2)
    p.image("logo.png")
    p.image("puzzle.png")
    p.text(title)
    p.print_and_feed(1)
    p.set(normal_textsize=True)
    lines = textwrap.wrap(desc, 48)
    for line in lines :
        p.textln(line)
    p.cut()