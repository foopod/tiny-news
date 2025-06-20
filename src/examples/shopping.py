from escpos.printer import Usb

grocerys = [
    "Soy Milk",
    "Jam",
    "Carrots",
    "Eggplant",
    "Lentils",
    "Apples",
    "Rice"
]

p = Usb(0x04b8, 0x0e28, 0)

p.set(custom_size=True, width=2, height=2)
p.textln("Groceries")
p.set(custom_size=False, width=1, height=1)

p.print_and_feed(1)

for g in grocerys:
    p.textln(f'[ ] {g}')
p.cut()
p.close()
