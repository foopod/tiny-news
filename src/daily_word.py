import requests
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from rss import getRSS
import html
import re
import xmltodict
from util import print_heading
import textwrap

class LANGUAGE:
    TE_REO = "Te Reo"
    RUSSIAN = "Russian"

def create_word_card(word, output_file = 'word.png'):
    width = 575
    height = 200
    margin = 20  # Padding from edges
    
    # Create image
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Load font
    try:
        font_path = "assets/FiraSans-Regular.ttf"
        # Start with a reasonable font size
        font_size = 100
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()
        font_size = 40  # Default font is smaller
    
    # Calculate optimal font size that fits within image bounds
    max_width = width - (2 * margin)
    max_height = height - (2 * margin)
    
    # Get text dimensions and scale down if necessary
    bbox = draw.textbbox((0, 0), word, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Scale font size to fit within bounds
    while (text_width > max_width or text_height > max_height) and font_size > 10:
        font_size -= 2
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), word, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    
    # Calculate position to center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Adjust for any baseline offset
    y -= bbox[1]
    
    # Draw the centered text
    draw.text((x, y), word, font=font, fill='black')
    
    # Convert to black and white for thermal printer
    bw_image = image.convert('1')
    bw_image.save(output_file)
    
    print(f"Created: {output_file} (font size: {font_size})")
    return bw_image

def get_russian_word():
    today = datetime.today()
    date_format = "%Y-%m-%d"
    d = today.strftime(date_format)

    url = f"https://www.russianpod101.com/api/word-day/{d}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0',
        'From': 'https://www.russianpod101.com'
    }

    response = requests.get(url, headers=headers)
    data = response.json()['payload']

    create_word_card(data['word_day']['text'])

    return {
        'text': data['word_day']['text'],
        'meaning': data['word_day']['english'] + ', ' + data['word_day']['meaning'],
        'romanization': data['word_day']['romanization'],
    }

def get_te_reo_word():
    latest = getRSS('https://kupu.maori.nz/feed.xml')['rss']['channel']['item'][0]
    decoded_description = html.unescape(latest['description'])

    # TODO parse this more nicely (this is dumb and will probably break) 
    meaning = decoded_description.split(': ')[1].split('<')[0]

    return {
        'text': latest['title'],
        'meaning': meaning
    }

def print_daily_word(printer):
    now = datetime.today()
    # alternates between TE_REO and RUSSIAN
    language = LANGUAGE.TE_REO if now.weekday()%2 == 0 else LANGUAGE.RUSSIAN

    word_data = None
    if language == LANGUAGE.TE_REO:
        word_data = get_te_reo_word()
    elif language == LANGUAGE.RUSSIAN:
        word_data = get_russian_word()
    
    if not word_data:
        return

    create_word_card(word_data['text'])

    print_heading(printer, f"Daily Word - {language}")
    printer.image('word.png', impl='graphics', center=True)
    if word_data['romanization']:
        printer.textln(f"Romanization: {word_data['romanization']}")
    meaning = f"Meaning: {word_data['meaning']}"

    lines = textwrap.wrap(meaning, 48)
    for line in lines :
        printer.textln(line)
