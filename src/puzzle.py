import random
import math
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Word list
words = [
    "sunshine", "backpack", "midnight", "elephant", "notebook", "triangle", "calendar",
    "dolphins", "mountain", "chocolate", "sandwich", "marathon", "painting", "keyboard",
    "bicycles", "magazine", "campfire", "pineapple", "airplane", "umbrella", "vacation",
    "laughter", "snowfall", "reindeer", "necklace", "treasure", "avocados", "baseball",
    "skylight", "password", "birthday", "storybook", "volcanoes", "headphones", "telescope",
    "drifting", "brilliant", "mystical", "gardener", "spectrum", "abdominal", "abrasive", "abundance",
    "accident", "activate", "adjacent", "aircraft", "alligator", "ambition", "amphibian", "amusement",
    "analogy", "ancestral", "androgyny", "annotate", "accusation", "relevancy", "companion", "sedative",
    "marinate", "redirection", "perambulate", "benevolence", "complaint", "reschedule", "aneurism",
    "backstage", "badminton", "balcony", "beguiling", "blemish", "bribery", "brutalism", "chocolate",
    "cabinet", "cabaret", "caffeine", "cannibal", "capitalism", "cardiology", "cavernous", "circumvent",
    "collapse", "corduroy", "crucible", "cumulative", "dalmatian", "daydream", "debatable", "declassified",
    "denomination", "deprecation", "descendant", "dietitian", "digression", "dreadful", "dungeon",
    "eccentric", "editorial", "education", "egomania", "emphatic", "emporium", "endemic", "endorsement",
    "enhancement", "equation", "expiry", "familiar", "feminism", "fermented", "fierceness", "firmament",
    "flamboyant", "floatation", "florist", "fogginess", "foreboding", "fundamental", "galavant", 
    "galvanised", "gardener", "gazebo", "gelatinous", "glimmered", "glucose", "gorgeous", "governance",
    "haunting", "hairspray", "hallucinate", "heftiness", "herbalism", "hindrance", "historian",
    "identity", "idyllic", "ignorant", "illegitimate", "imbalance", "immersion", "incognito"
]

# Scrabble scores
scrabble_scores = {
    'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1,
    'f': 4, 'g': 2, 'h': 4, 'i': 1, 'j': 8,
    'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1,
    'p': 3, 'q': 10, 'r': 1, 's': 1, 't': 1,
    'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4,
    'z': 10
}

def get_random_word(word_list):
    return random.choice(word_list)

def top_scoring_letter(word):
    return max(word.lower(), key=lambda letter: scrabble_scores.get(letter, 0))

def shuffle(word):
    word = word.lower()
    top_letter = top_scoring_letter(word)
    index = word.find(top_letter)
    word = word[:index] + ' ' + word[index + 1:]

    # 50% chance to reverse
    if random.random() < 0.5:
        word = word[::-1]

    # "Shuffle" using slice rearrangement
    r_index = random.randint(0, len(word))
    word = word[r_index:] + word[:r_index]

    return word

def draw(word, output_file='puzzle.png'):
    shuffled = shuffle(word)
    size = 500
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

def create_puzzle():
    today_date = datetime.now().strftime('%d-%m-%Y')
    random.seed(today_date)
    word = get_random_word(words)
    draw(word)

if __name__ == '__main__':
    import math
    create_puzzle()
    print("done")
