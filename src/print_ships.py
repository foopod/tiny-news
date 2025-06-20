from PIL import Image, ImageDraw, ImageFont
from escpos.printer import Usb
import random

def print_ship(printer):
    draw([random.randint(1, 9),random.randint(1, 9),random.randint(1, 9)])
    printer.image('ship.png', impl='graphics', center=True)
    
def draw(parts_list, output_file='ship.png'):
    w = 72
    h = 48
    image = Image.new('RGBA', (w, h), color='white')
    draw = ImageDraw.Draw(image)

    folders = ['front', 'mid', 'rear']

    for part, folder in zip(parts_list, folders):
        path = f'images/parts/{folder}/{part}.png'
        try:
            part_img = Image.open(path).convert('RGBA')
            image.alpha_composite(part_img.resize((w, h)))  # Resize if needed
        except FileNotFoundError:
            print(f"Warning: File not found: {path}")
        except Exception as e:
            print(f"Error loading {path}: {e}")
        

    bw_image = image.convert('1')
    bw_image.save(output_file)
    print(f"Created: {output_file}")

if __name__ == '__main__':
    p = Usb(0x04b8, 0x0e28, 0)
    print_ship(p)
    p.cut()
    p.close()