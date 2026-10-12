import math
from PIL import Image, ImageDraw, ImageFont

# Scrabble scores
scrabble_scores = {
    'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1,
    'f': 4, 'g': 2, 'h': 4, 'i': 1, 'j': 8,
    'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1,
    'p': 3, 'q': 10, 'r': 1, 's': 1, 't': 1,
    'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4,
    'z': 10
}

def top_scoring_letter(word):
    return max(word.lower(), key=lambda letter: scrabble_scores.get(letter, 0))

def shuffle(word, reverse=False, rotation=0):
    """Blank the top scoring letter, then lay the word out for the wheel."""
    word = word.lower()
    top_letter = top_scoring_letter(word)
    index = word.find(top_letter)
    word = word[:index] + ' ' + word[index + 1:]

    if reverse:
        word = word[::-1]

    # rotate so the word doesn't always start at the same point on the wheel
    return word[rotation:] + word[:rotation]

def draw_wordwheel(word, output_file='puzzle.png', reverse=False, rotation=0):
    shuffled = shuffle(word, reverse, rotation)
    size = 575
    font_size = 56
    image = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(image)

    # Load font (fallback to default if 'Impact' is not available)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    angle_step = 360 / len(shuffled)
    radius = len(word) * 18

    bbox = [size / 2 - radius, size / 2 - radius, size / 2 + radius, size / 2 + radius]
    draw.ellipse(bbox, outline='black', width=2, fill='white')

    for i, letter in enumerate(shuffled):
        theta = angle_step * i * (math.pi / 180)
        x = int(size / 2 + radius * math.cos(theta))
        y = int(size / 2 + radius * math.sin(theta))
        
        bbox = font.getbbox(letter)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Correct vertical offset by shifting based on bbox center
        offset_x = text_width / 2
        offset_y = (bbox[3] + bbox[1]) / 2  # Average of top and bottom

        bbox = [x - 40, y  - 40, x  + 40, y  + 40]
        draw.ellipse(bbox, outline='black', width=2, fill='white')

        draw.text((x - offset_x, y - offset_y), letter, font=font, fill='black')

    bw_image = image.convert('1')
    bw_image.save(output_file)
    print(f"Created: {output_file}")
