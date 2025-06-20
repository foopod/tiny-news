from escpos.printer import Usb

p = Usb(0x04b8, 0x0e28, 0)
for g in range(20):
    p.print_and_feed(1)
    p.cut()
p.close()
