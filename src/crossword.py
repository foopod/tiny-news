from PIL import Image, ImageDraw, ImageFont
import math

def dither_fill(draw, position, density):
    x1, y1, x2, y2 = position
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    
    for y in range(y1, y2):
        for x in range(x1, x2):
            threshold = ((x & 1) + (y & 1) * 2) / 4.0
            if density > threshold:
                draw.point((x, y), fill='black')

def render_crossword(width, height, empties, labels, output_file='puzzle.png'):
    size = 575
    image = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(image)
    tile_size = size/width
    
    for i in range(width + 1): # 0 to 9 for 10 lines
        line_width = 2
        pos = i * tile_size
        # Vertical lines
        draw.line([(pos, 0), (pos, size)], fill='black', width=line_width)
        # Horizontal lines
        draw.line([(0, pos), (size, pos)], fill='black', width=line_width)
    
    # Try to load a font, fall back to default if not available
    font_size = int(tile_size * 0.3)
    font = None
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/AdwaitaSans/AdwaitaSans-Regular.ttf", font_size)  # probook
        except:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", font_size)  # Linux
            except:
                try:
                    # Try Windows fonts
                    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()  # Last resort
    
    for cell in empties:
        x = cell % width
        y = math.floor(cell / width)
        dither_fill(draw, [tile_size * x, tile_size * y, tile_size * x + tile_size, tile_size * y + tile_size], density=0.2)

    for cell in labels:
        x = cell[0] % width
        y = math.floor(cell[0] / width)

        # Calculate position for top-left corner with small padding
        label_x = tile_size * x + 3  # 3 pixel padding from left edge
        label_y = tile_size * y + 0  # 2 pixel padding from top edge
        
        # Draw the label number
        if font != ImageFont.load_default():
            draw.text((label_x, label_y), cell[1], fill='black', font=font)
        else:
            # If using default font, draw it multiple times to make it bolder/larger
            label_text = str(cell[1])
            for dx in range(2):
                for dy in range(2):
                    draw.text((label_x + dx, label_y + dy), label_text, fill='black', font=font)
    
    bw_image = image.convert('1')
    bw_image.save(output_file)

render_crossword(5,5,[4, 20], [(0, '1'), (1, '2'), (2, '3'), (3, '4'), (5, '5'), (9, '6'), (10, '7'), (15, '8'), (21, '9')])