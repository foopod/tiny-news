from PIL import Image, ImageDraw
import cairosvg
import io
from escpos.printer import Usb
import chess
from datetime import datetime, timedelta
import json

def get_piece(file_name, size):
    png_data = cairosvg.svg2png(
        url=f"chess-pieces/{file_name}.svg",
        output_width=size,
        output_height=size,
        background_color=None  # Preserve transparency
    )
    
    # Create PIL Image from bytes
    image = Image.open(io.BytesIO(png_data))
    
    # Ensure RGBA mode for transparency
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    return image


def dither_fill(draw, position, density):
    x1, y1, x2, y2 = position
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    
    for y in range(y1, y2):
        for x in range(x1, x2):
            threshold = ((x & 1) + (y & 1) * 2) / 4.0
            if density > threshold:
                draw.point((x, y), fill='black')

def render_chess(fen, output_file='puzzle.png'):
    size = 575
    image = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(image)

    tile_size = size/8
    for x in range(8):
        for y in range(8):
            if x%2 != y%2:
                # black
                dither_fill(draw, [tile_size * x, tile_size * y, tile_size * x + tile_size, tile_size*y + tile_size], density=0.2)
            else:
                # white
                draw.rectangle([tile_size * x, tile_size * y, tile_size * x + tile_size, tile_size*y + tile_size], fill='white')

    f = fen.split(' ')[0]
    rows = f.split('/')
    for x, row in enumerate(rows):
        col = 0

        while(len(row) > 0):
            val = row[0]
            row = row[1:]
            if val.isnumeric():
                col += int(val)
            else:
                if val.isupper():
                    # w
                    piece = f"w{val}"
                else:
                    # b
                    piece = f"b{val.upper()}"
                piece_image = get_piece(piece, 60)
                image.paste(piece_image, (col * int(tile_size) + 10, x* int(tile_size) + 10), piece_image)

                col += 1


    bw_image = image.convert('1')
    bw_image.save(output_file)


