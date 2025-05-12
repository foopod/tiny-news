import pygame
import sys
from datetime import datetime
from print_news import print_newsletter
import time

# Initialize pygame
pygame.init()

# Get screen info for fullscreen
infoObject = pygame.display.Info()
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)
pygame.display.set_caption("Fullscreen Blue Background Game")

# Load an image
# Make sure 'image.png' is in the same folder
try:
    image = pygame.image.load('images/jupiter.png')
except pygame.error as e:
    print(f"Unable to load image: {e}")
    pygame.quit()
    sys.exit()

# Set up font and text
# font = pygame.font.SysFont("None", 120)
font_path = pygame.font.match_font("dejavusansbold")
big_font = pygame.font.Font(font_path, 140)
smaller_font = pygame.font.Font(font_path, 80)
tiny_font = pygame.font.Font(font_path, 32)

want_a_newspaper = big_font.render("Want a newspaper?", True, (255, 255, 255))  # White text
but_skinny = smaller_font.render("(but skinny)", True, (255, 255, 255))
today = tiny_font.render(datetime.today().strftime('%A %d, %B %Y'), True, (0, 0, 0))
press_space = tiny_font.render("PRESS SPACE", True, (0, 0, 0))

# Function to call when any key is pressed
def on_key_press(key):
    print_newsletter()
    

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill((135, 206, 235))  # Fill with blue

    # Blit image and text
    # screen.blit(image, (100, 100))  # Position image at (100, 100)
    screen.blit(want_a_newspaper, (250, 50))  # Position text at (100, 300)
    screen.blit(but_skinny, (700, 150))
    pygame.draw.rect(screen, (255,255,255), (550, 300, 300, 600), 0)
    screen.blit(today, (570, 320))
    screen.blit(press_space, (620, 700))

    pygame.display.flip()  # Update the display

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:
                running = False
            else:
                on_key_press(event.key)
            
    clock.tick(60)  # Limit to 60 FPS

# Quit pygame
pygame.quit()
sys.exit()
