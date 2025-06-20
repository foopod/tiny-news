from escpos.printer import Usb

p = Usb(0x04b8, 0x0e28, 0)
p.text("Te Pāti Māori")
p.cut()
p.close()
