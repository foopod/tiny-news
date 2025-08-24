import pygame
import sys
from datetime import datetime
from tiny_news import print_newsletter, print_rick_roll,print_weather_only, print_puzzle_only, word_only
import time

# Initialize pygame
pygame.init()

# Get screen info for fullscreen
infoObject = pygame.display.Info()
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)

# Set up font and text
# font = pygame.font.SysFont("None", 120)
font_path = pygame.font.match_font("dejavusansbold")
arial_font_path = pygame.font.match_font("arial")
big_font = pygame.font.Font(font_path, 140)
smaller_font = pygame.font.Font(font_path, 80)
tiny_font = pygame.font.Font(font_path, 32)
normal_font = pygame.font.Font(arial_font_path, 18)

black = (0,0,0)
grey = (100, 100, 100)
white = (255, 255, 255)

want_a_newspaper = big_font.render("Free Newspapers!", True, white)  # White text
but_skinny = smaller_font.render("(but tiny)", True, white)
press_space = big_font.render("Space", True, white)
to_print = smaller_font.render("hit                      to print", True, white)
today = tiny_font.render(datetime.today().strftime('%A %d, %B %Y'), True, black)

local = tiny_font.render("Local News", True, white)
local2 = normal_font.render("On print from Radio NZ RSS", True, grey)

world = tiny_font.render("World News", True, white)
world2 = normal_font.render("On print from BBC World News RSS", True, grey)

weather = tiny_font.render("Weather", True, white)
weather2 = normal_font.render("On print from Open Meteo API", True, grey)

puzzle = tiny_font.render("Puzzle", True, white)
puzzle2 = normal_font.render("Hand chosen daily by Jono", True, grey)

# Function to call when any key is pressed
def on_key_press(key):
    print_newsletter()
    

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill((135, 206, 235))  # Fill with blue
    today = tiny_font.render(datetime.today().strftime('%A %d, %B %Y'), True, black)
    

    # Blit image and text
    # screen.blit(image, (100, 100))  # Position image at (100, 100)
    screen.blit(want_a_newspaper, (50, 50))  # Position text at (100, 300)
    screen.blit(but_skinny, (500, 150))
    pygame.draw.rect(screen, white, (950, 000, 380, 800), 0)
    screen.blit(today, (970, 20))
    screen.blit(press_space, (140, 600))
    screen.blit(to_print, (50, 630))

    pygame.draw.rect(screen, black, (970, 95, 340, 30), 0)
    screen.blit(local, (1080, 100))
    screen.blit(local2, (970, 150))

    pygame.draw.rect(screen, black, (970, 270, 340, 30), 0)
    screen.blit(weather, (1080, 275))
    screen.blit(weather2, (970, 325))

    pygame.draw.rect(screen, black, (970, 445, 340, 30), 0)
    screen.blit(puzzle, (1080, 450))
    screen.blit(puzzle2, (970, 500))

    # pygame.draw.rect(screen, black, (970, 620, 340, 30), 0)
    # screen.blit(puzzle, (1080, 625))
    # screen.blit(puzzle2, (970, 675))

    pygame.display.flip()  # Update the display

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:
                running = False
            elif event.key == pygame.K_w:
                print_weather_only()
            elif event.key == pygame.K_ESCAPE:
                print_rick_roll()
            elif event.key == pygame.K_p:
                print_puzzle_only()
            elif event.key == pygame.K_d:
                word_only()
            else:
                on_key_press(event.key)
            
    clock.tick(60)  # Limit to 60 FPS

# Quit pygame
pygame.quit()
sys.exit()
