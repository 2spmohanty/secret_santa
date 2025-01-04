import pygame
import random
import sys
from collections import Counter
import math
import requests

# Initialize PyGame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800  # Adjusted height for input box positioning
GRID_ROWS = 4  # Set grid rows to 4
GRID_COLS = 3
CELL_WIDTH, CELL_HEIGHT = 125, 125
FPS = 60
FONT_SIZE = 32

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
SHADOW = (50, 50, 50)
HIGHLIGHT = (200, 200, 200)
GOLDEN_RED = (255, 223, 186)  # Gradient color for None case
GLOSSY_RED = (220, 20, 60)
INPUT_BOX_COLOR = (255, 232, 198)
# Names and Images
# Extended names to 30 elements
TOTAL_REQUESTS = 0

names = []


def get_person_names():
    global names
    response = requests.get('http://127.0.0.1:8000/person')
    if response.status_code == 200:
        data = response.json()
        print(data)
        names = data.get('names', [])
    else:
        print(f"Error: {response.status_code}")
        return []


get_person_names()

images = [pygame.image.load(f"images/{person.lower()}.png") for person in names]



# Initialize Pygame mixer
pygame.mixer.init()

# Load multiple sounds for each category
spin_sounds = [
    pygame.mixer.Sound("music/rolling1.wav"),
    pygame.mixer.Sound("music/rolling2.wav"),
    pygame.mixer.Sound("music/rolling3.wav")
]

winner_sounds = [
    pygame.mixer.Sound("music/winner1.wav"),
    pygame.mixer.Sound("music/winner2.wav"),
    pygame.mixer.Sound("music/winner3.wav")
]

loser_sounds = [
    pygame.mixer.Sound("music/loser2.wav"),
    pygame.mixer.Sound("music/loser3.wav"),
    pygame.mixer.Sound("music/loser4.wav")
]


def play_random_sound(sound_list):
    random.choice(sound_list).play()


# Load Background Image
background_image = pygame.image.load("images/bg.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Secret Santa's Slot Machine")

# Fonts
font = pygame.font.Font(None, FONT_SIZE)

# Text Input Variables
input_active = True
input_text = ""

# Game State
matrix = [[random.choice(names) for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
shadow = False
winner_name = ""
winner_row = -1
highlight_row = -1
highlight_item = None
error_case = False
sparkles = []


# Functions
def get_winner(sticker_name):
    # Decide whether to call the API or return None
    global TOTAL_REQUESTS
    TOTAL_REQUESTS += 1
    if sticker_name == "twin":
        return random.choice(names)
    if sticker_name == "tlost":
        return None
    if random.random() < 0.3:  # 30% chance to return None

        print("Returning None before calling REST API.")
        return None

    # 70% chance to call the REST API
    url = f"http://localhost:8000/selectWinner/{sticker_name}"

    try:
        response = requests.get(url)

        # Check if the response was successful
        if response.status_code == 200:
            data = response.json()
            print(f"Successfully got winner: {data.get("winner")}")
            return data.get("winner")  # Return the "winner" key from the response
        else:
            print(f"Error: Received status code {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while calling REST API: {e}")
        return None


def draw_sparkles():
    global sparkles
    for sparkle in sparkles[:]:
        pygame.draw.circle(screen, sparkle[3], (int(sparkle[0]), int(sparkle[1])), int(sparkle[2]))
        sparkle[2] -= 0.2
        if sparkle[2] <= 0:
            sparkles.remove(sparkle)


def create_sparkles(rect_x, rect_y):
    global sparkles
    for _ in range(20):
        x = random.randint(rect_x, rect_x + CELL_WIDTH)
        y = random.randint(rect_y, rect_y + CELL_HEIGHT)
        size = random.uniform(1, 3)
        color = (random.randint(200, 255), random.randint(200, 255), random.randint(0, 100))
        sparkles.append([x, y, size, color])


def draw_grid():
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            rect_x = col * CELL_WIDTH + (WIDTH - CELL_WIDTH * GRID_COLS) // 2
            rect_y = row * CELL_HEIGHT + 150  # Adjusted position for better layout

            # Shadow with dark reddish color
            shadow_rect = pygame.Rect(rect_x + 5, rect_y + 5, CELL_WIDTH, CELL_HEIGHT)
            pygame.draw.rect(screen, (139, 0, 0), shadow_rect, border_radius=10)

            # Golden cells
            cell_color = (255, 223, 0)  # Glossy golden
            pygame.draw.rect(screen, cell_color, (rect_x, rect_y, CELL_WIDTH, CELL_HEIGHT), border_radius=10)

            # Draw fine dark red border
            pygame.draw.rect(screen, (139, 0, 0), (rect_x, rect_y, CELL_WIDTH, CELL_HEIGHT), 2, border_radius=10)

            # Draw image and name
            name = matrix[row][col]
            img_index = names.index(name)
            img = images[img_index]
            img = pygame.transform.scale(img, (CELL_WIDTH - 20, CELL_HEIGHT - 70))
            img_rect = img.get_rect(center=(rect_x + CELL_WIDTH // 2, rect_y + CELL_HEIGHT // 3))
            screen.blit(img, img_rect)

            text = font.render(name, True, BLACK)
            text_rect = text.get_rect(center=(rect_x + CELL_WIDTH // 2, rect_y + 2 * CELL_HEIGHT // 3))
            screen.blit(text, text_rect)

            # Overlay the loser cell with translucent green
            if error_case and matrix[row][col] == highlight_item:
                overlay = pygame.Surface((CELL_WIDTH, CELL_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 255, 0, 128))  # Green with 50% opacity
                screen.blit(overlay, (rect_x, rect_y))

            # Overlay non-winning cells with translucent grey when a winner is identified
            if shadow and row != winner_row:
                overlay = pygame.Surface((CELL_WIDTH, CELL_HEIGHT), pygame.SRCALPHA)
                overlay.fill((128, 128, 128, 128))  # Grey with 50% opacity
                screen.blit(overlay, (rect_x, rect_y))


def update_matrix_with_winner(winner):
    global winner_row, shadow, highlight_item, error_case
    if winner:
        winner_row = random.randint(0, GRID_ROWS - 1)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                matrix[row][col] = winner if row == winner_row else random.choice([n for n in names if n != winner])
        shadow = True
        error_case = False
        play_random_sound(winner_sounds)
        # pygame.mixer.Sound.play(winner_sound)
        # Create sparkles and fireworks for winner row
        for col in range(GRID_COLS):
            rect_x = col * CELL_WIDTH + (WIDTH - CELL_WIDTH * GRID_COLS) // 2
            rect_y = winner_row * CELL_HEIGHT + 50
            create_sparkles(rect_x, rect_y)
            create_fireworks(rect_x, rect_y)
    else:
        winner_row = -1

        visible_counts = Counter([matrix[row][col] for row in range(GRID_ROWS) for col in range(GRID_COLS)])
        most_common = visible_counts.most_common(1)[0][0]
        highlight_item = most_common
        error_case = True
        shadow = False
        # pygame.mixer.Sound.play(loser_sound)
        play_random_sound(loser_sounds)


def create_fireworks(rect_x, rect_y, is_winner_cell=False):
    num_particles = 100 if is_winner_cell else 50
    for _ in range(num_particles):
        angle = random.uniform(0, 360)
        radius = random.randint(20, 100 if is_winner_cell else 50)
        x = int(rect_x + CELL_WIDTH // 2 + radius * math.cos(math.radians(angle)))
        y = int(rect_y + CELL_HEIGHT // 2 + radius * math.sin(math.radians(angle)))
        size = random.randint(2, 6 if is_winner_cell else 4)
        color = (255, random.randint(150, 255), random.randint(0, 50))
        sparkles.append([x, y, size, color])


def spin_columns():
    # pygame.mixer.Sound.play(spin_sound)
    play_random_sound(spin_sounds)
    for col in range(GRID_COLS):
        for _ in range(10):  # Simulate spin effect
            for row in range(GRID_ROWS):
                matrix[row][col] = random.choice(names)
            screen.blit(background_image, (0, 0))
            draw_grid()
            pygame.display.flip()
            pygame.time.delay(50)


# Main Loop

clock = pygame.time.Clock()
run = True
while run:
    screen.blit(background_image, (0, 0))

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    spin_columns()
                    winner_name = get_winner(input_text)
                    update_matrix_with_winner(winner_name)
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
            elif event.key == pygame.K_DOWN:
                shadow = False
                highlight_item = None
                input_text = ""
                error_case = False
                input_active = True

    # Draw Grid
    draw_grid()

    # Draw Sparkles
    draw_sparkles()

    # Draw Input Box
    input_rect = pygame.Rect((WIDTH - 300) // 2, HEIGHT - 70, 300, 50)
    pygame.draw.rect(screen, INPUT_BOX_COLOR, input_rect, border_radius=15)
    pygame.draw.rect(screen, INPUT_BOX_COLOR, input_rect, 1, border_radius=15)
    input_surface = font.render(input_text, True, (121, 80, 80))
    input_rect_inner = input_surface.get_rect(center=input_rect.center)
    screen.blit(input_surface, input_rect_inner)

    # Display Update
    pygame.display.flip()
    clock.tick(FPS)

# Quit
print(f"Total User Request {TOTAL_REQUESTS}")
pygame.quit()
sys.exit()
