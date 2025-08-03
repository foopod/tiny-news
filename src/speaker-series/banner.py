from escpos.printer import Usb
from PIL import Image, ImageDraw, ImageFont


text = "IT IS YOUR BIRTHDAY."

p = Usb(0x04b8, 0x0e28, 0)
for letter in text:
    font_size = 500
    image_size=(570, 570)
    image = Image.new('RGB', (570,350), color='white')
    output_file = 'letter.png'
    try:
        font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    temp_image = Image.new('RGBA', image_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(temp_image)

    # Use textbbox to calculate text size
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_position = ((image_size[0] - text_width) // 2 - 100, (image_size[1] - text_height) // 2 - 100)
    
    # Draw the letter
    draw.text(text_position, letter, font=font, fill=(0, 0, 0, 255))

    # Rotate the image 90 degrees clockwise
    rotated = temp_image.rotate(-90, expand=True)

    # Paste rotated letter onto the final image
    image.paste(rotated, ((image_size[0] - rotated.width) // 2, (image_size[1] - rotated.height) // 2), rotated)

    # Save the final image
    image.save(output_file)
    p.image('letter.png')

p.cut()
p.close()
