import pygame
import random
import sys
from collections import Counter

# Initialize PyGame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 900  # Adjusted height for input box
GRID_ROWS = 4
GRID_COLS = 3
CELL_WIDTH, CELL_HEIGHT = 150, 150
FPS = 60
FONT_SIZE = 32
SPARKLE_DURATION = 3  # Seconds for sparkles/fireworks

# Colors
GOLDEN = (255, 215, 0)
RED = (255, 0, 0)
DARK_RED_SHADOW = (139, 0, 0)
BLACK = (0, 0, 0)
SPARKLE_COLOR = (255, 223, 0)
INPUT_BOX_COLOR = (240, 248, 255)  # Snow White
ELF_GREEN = (0, 255, 0)

# Names and Images
names = ["A", "B", "C", "D", "E"] + ["X" + str(i) for i in range(25)]
images = [
    pygame.image.load("images/santa.png"),
    pygame.image.load("images/elf.png"),
    pygame.image.load("images/rudolph.png"),
    pygame.image.load("images/snowman.png"),
    pygame.image.load("images/grinch.png"),
] + [pygame.Surface((100, 100)) for _ in range(25)]  # Placeholder images

# Sounds
spin_sound = pygame.mixer.Sound("music/rolling1.wav")
winner_sound = pygame.mixer.Sound("music/winner2.wav")
loser_sound = pygame.mixer.Sound("music/loser1.wav")

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slot Machine")

# Fonts
font = pygame.font.Font(None, FONT_SIZE)

# Game State
input_text = ""
input_active = True
matrix = [[random.choice(names) for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
winner_row = -1
sparkles = []

# Helper Functions
def get_winner(input_text):
    return input_text if input_text in names else None

def draw_sparkles():
    global sparkles
    for sparkle in sparkles[:]:
        pygame.draw.circle(screen, SPARKLE_COLOR, sparkle[:2], sparkle[2])
        sparkle[2] -= 1
        if sparkle[2] <= 0:
            sparkles.remove(sparkle)

def create_sparkles():
    global sparkles
    for _ in range(50):  # Create sparkles
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(2, 5)
        sparkles.append([x, y, size])

def draw_grid():
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            rect_x = col * CELL_WIDTH + (WIDTH - GRID_COLS * CELL_WIDTH) // 2
            rect_y = row * CELL_HEIGHT + 50

            # Shadow Effect
            shadow_rect = pygame.Rect(rect_x + 5, rect_y + 5, CELL_WIDTH, CELL_HEIGHT)
            pygame.draw.rect(screen, DARK_RED_SHADOW, shadow_rect, border_radius=10)

            # Grid Cell
            cell_color = GOLDEN
            if winner_row == row:
                cell_color = GOLDEN
            elif winner_row != -1:
                cell_color = BLACK

            pygame.draw.rect(
                screen, cell_color, (rect_x, rect_y, CELL_WIDTH, CELL_HEIGHT), border_radius=10
            )
            pygame.draw.rect(
                screen, RED, (rect_x, rect_y, CELL_WIDTH, CELL_HEIGHT), 4, border_radius=10
            )

            # Draw Image
            name = matrix[row][col]
            img_index = names.index(name)
            img = images[img_index]
            img = pygame.transform.scale(img, (CELL_WIDTH - 20, CELL_HEIGHT - 70))
            img_rect = img.get_rect(center=(rect_x + CELL_WIDTH // 2, rect_y + CELL_HEIGHT // 3))
            screen.blit(img, img_rect)

            # Draw Name
            text = font.render(name, True, BLACK)
            text_rect = text.get_rect(center=(rect_x + CELL_WIDTH // 2, rect_y + 2 * CELL_HEIGHT // 3))
            screen.blit(text, text_rect)

def spin_columns():
    pygame.mixer.Sound.play(spin_sound)
    for _ in range(10):  # Simulate spin
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                matrix[row][col] = random.choice(names)
        screen.fill(BLACK)
        draw_grid()
        pygame.display.flip()
        pygame.time.delay(50)

def update_matrix_with_winner(winner):
    global winner_row, sparkles
    if winner:
        winner_row = random.randint(0, GRID_ROWS - 1)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                matrix[row][col] = winner if row == winner_row else random.choice(
                    [n for n in names if n != winner]
                )
        pygame.mixer.Sound.play(winner_sound)
        create_sparkles()
        pygame.time.delay(SPARKLE_DURATION * 1000)
    else:
        pygame.mixer.Sound.play(loser_sound)

# Main Game Loop
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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
                input_active = True
                winner_row = -1
                input_text = ""

    # Draw Background and Grid
    draw_grid()
    draw_sparkles()

    # Input Box
    input_rect = pygame.Rect((WIDTH - 300) // 2, HEIGHT - 70, 300, 50)
    pygame.draw.rect(screen, INPUT_BOX_COLOR, input_rect, border_radius=15)
    pygame.draw.rect(screen, BLACK, input_rect, 2, border_radius=15)
    input_surface = font.render(input_text, True, BLACK)
    screen.blit(input_surface, (input_rect.x + 10, input_rect.y + 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
