from escpos.printer import Usb

p = Usb(0x04b8, 0x0e28, 0)

for i in range(5):
    p.qr("https://www.youtube.com/watch?v=dQw4w9WgXcQ", size=16)
    p.cut()
p.close()
