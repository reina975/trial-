import pygame
import random
import numpy as np

# Initialize pygame
pygame.init()

# Game Constants - based on original 2048 game dimensions
GRID_SIZE = 4
TILE_SIZE = 106  # Original uses close to 107px
GRID_SPACING = 15  # Original uses ~15px spacing
BOARD_SIZE = GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * GRID_SPACING
PADDING = 15
HEADER_HEIGHT = 130
WINDOW_WIDTH = BOARD_SIZE + 2 * PADDING
WINDOW_HEIGHT = BOARD_SIZE + HEADER_HEIGHT + 2 * PADDING

# Exact colors from original 2048 CSS
BACKGROUND_COLOR = (250, 248, 239)  # #faf8ef - Page background
GRID_COLOR = (187, 173, 160)        # #bbada0 - Game container background
EMPTY_TILE_COLOR = (205, 193, 180)  # #cdc1b4 - Empty tile background
TEXT_DARK = (119, 110, 101)         # #776e65 - Main text color
TEXT_LIGHT = (249, 246, 242)        # #f9f6f2 - Light text color (for dark tiles)

# Extract exact tile colors from original CSS
TILE_COLORS = {
    0: {"bg": (205, 193, 180), "text": TEXT_DARK},  # Empty tile
    2: {"bg": (238, 228, 218), "text": TEXT_DARK},  # #eee4da
    4: {"bg": (237, 224, 200), "text": TEXT_DARK},  # #ede0c8
    8: {"bg": (242, 177, 121), "text": TEXT_LIGHT}, # #f2b179
    16: {"bg": (245, 149, 99), "text": TEXT_LIGHT}, # #f59563
    32: {"bg": (246, 124, 95), "text": TEXT_LIGHT}, # #f67c5f
    64: {"bg": (246, 94, 59), "text": TEXT_LIGHT},  # #f65e3b
    128: {"bg": (237, 207, 114), "text": TEXT_LIGHT}, # #edcf72
    256: {"bg": (237, 204, 97), "text": TEXT_LIGHT},  # #edcc61
    512: {"bg": (237, 200, 80), "text": TEXT_LIGHT},  # #edc850
    1024: {"bg": (237, 197, 63), "text": TEXT_LIGHT}, # #edc53f
    2048: {"bg": (237, 194, 46), "text": TEXT_LIGHT}  # #edc22e
}

# Font sizes (following original 2048 font sizes as closely as possible)
# Original uses "Clear Sans" font which we'll approximate with default fonts
TITLE_FONT_SIZE = 80
SCORE_LABEL_SIZE = 13
SCORE_VALUE_SIZE = 25
BUTTON_FONT_SIZE = 18
INSTRUCTION_FONT_SIZE = 18

# Original 2048 uses different font sizes for different tile numbers
# Exact font sizes from the CSS
TILE_FONT_SIZES = {
    2: 53,
    4: 53,
    8: 53,
    16: 50,
    32: 50,
    64: 50,
    128: 45,
    256: 45,
    512: 45,
    1024: 35,
    2048: 35,
    4096: 30,    # Additional sizes for larger numbers
    8192: 30,
    16384: 25,
    32768: 25,
    65536: 25
}

# Initialize fonts
TITLE_FONT = pygame.font.SysFont('arial', TITLE_FONT_SIZE, bold=True)
SCORE_LABEL_FONT = pygame.font.SysFont('arial', SCORE_LABEL_SIZE, bold=True)
SCORE_VALUE_FONT = pygame.font.SysFont('arial', SCORE_VALUE_SIZE, bold=True)
BUTTON_FONT = pygame.font.SysFont('arial', BUTTON_FONT_SIZE, bold=True)
INSTRUCTION_FONT = pygame.font.SysFont('arial', INSTRUCTION_FONT_SIZE)
TILE_FONTS = {value: pygame.font.SysFont('arial', size, bold=True) for value, size in TILE_FONT_SIZES.items()}

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("2048")

grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
score = 0
best_score = 0

def draw_rounded_rect(surface, rect, color, radius=0.4):
    """Draw a rounded rectangle"""
    rect = pygame.Rect(rect)
    color = pygame.Color(*color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = 0, 0
    rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)

    circle = pygame.Surface([min(rect.size) * 2] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)

    radius = rectangle.blit(circle, (0, 0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle, radius)
    radius.topright = rect.topright
    rectangle.blit(circle, radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle, radius)

    rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))

    rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MIN)

    surface.blit(rectangle, pos)

def draw_grid():
    screen.fill(BACKGROUND_COLOR)
    
    # Draw header with game title (large "2048" text)
    title_text = TITLE_FONT.render("2048", True, TEXT_DARK)
    screen.blit(title_text, (PADDING, PADDING))
    
    # Draw score boxes (following original 2048 layout)
    # Score containers have specific dimensions from the CSS
    score_box_width = 95
    score_box_height = 55
    score_box_margin = 5
    score_box_y = PADDING + 10
    
    # Best score box - positioned first (rightmost)
    best_box_x = WINDOW_WIDTH - score_box_width - PADDING
    best_box_rect = pygame.Rect(best_box_x, score_box_y, score_box_width, score_box_height)
    draw_rounded_rect(screen, best_box_rect, GRID_COLOR, 0.1)
    
    # Current score box - positioned left of best score
    score_box_x = best_box_x - score_box_width - score_box_margin - 5
    score_box_rect = pygame.Rect(score_box_x, score_box_y, score_box_width, score_box_height)
    draw_rounded_rect(screen, score_box_rect, GRID_COLOR, 0.1)
    
    # Draw "New Game" button like the original
    button_width = 130
    button_height = 40
    button_x = WINDOW_WIDTH - button_width - PADDING
    button_y = score_box_y + score_box_height + 10  # Position below score boxes
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    draw_rounded_rect(screen, button_rect, GRID_COLOR, 0.1)
    
    # Draw button text
    new_game_text = BUTTON_FONT.render("New Game", True, TEXT_LIGHT)
    new_game_rect = new_game_text.get_rect(center=button_rect.center)
    screen.blit(new_game_text, new_game_rect)
    
    # Score labels - positioned at top of boxes with proper spacing
    score_label = SCORE_LABEL_FONT.render("SCORE", True, EMPTY_TILE_COLOR)
    best_label = SCORE_LABEL_FONT.render("BEST", True, EMPTY_TILE_COLOR)
    
    # Position labels in the upper part of the boxes
    screen.blit(score_label, (score_box_rect.centerx - score_label.get_width()//2, 
                             score_box_rect.top + 8))
    screen.blit(best_label, (best_box_rect.centerx - best_label.get_width()//2, 
                            best_box_rect.top + 8))
    
    # Score values - positioned in the bottom part of the boxes
    score_value = SCORE_VALUE_FONT.render(str(score), True, TEXT_LIGHT)
    best_value = SCORE_VALUE_FONT.render(str(best_score), True, TEXT_LIGHT)
    
    # Position values in the lower part of the boxes
    screen.blit(score_value, (score_box_rect.centerx - score_value.get_width()//2, 
                            score_box_rect.top + 25))
    screen.blit(best_value, (best_box_rect.centerx - best_value.get_width()//2, 
                           best_box_rect.top + 25))
    
    # Game instructions
    instruction1 = INSTRUCTION_FONT.render(
        "Join the numbers and get to the 2048 tile!", True, TEXT_DARK)
    instruction2 = INSTRUCTION_FONT.render(
        "HOW TO PLAY: Use your arrow keys to move the tiles.", True, TEXT_DARK)
    
    # Position instructions below the title
    screen.blit(instruction1, (PADDING, PADDING + title_text.get_height() + 5))
    screen.blit(instruction2, (PADDING, PADDING + title_text.get_height() + 5 + instruction1.get_height() + 5))
    
    # Draw game board background - matches original dimensions and style
    board_rect = pygame.Rect(PADDING, HEADER_HEIGHT, BOARD_SIZE, BOARD_SIZE)
    draw_rounded_rect(screen, board_rect, GRID_COLOR, 0.02)
    
    # Draw tiles with original 2048 styling
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            # Calculate tile position - matching original grid spacing
            x = PADDING + GRID_SPACING + col * (TILE_SIZE + GRID_SPACING)
            y = HEADER_HEIGHT + GRID_SPACING + row * (TILE_SIZE + GRID_SPACING)
            
            # Draw tile
            value = grid[row][col]
            tile_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            tile_color = TILE_COLORS.get(value, TILE_COLORS[2048])["bg"]
            draw_rounded_rect(screen, tile_rect, tile_color, 0.05)  # Original has smaller corner radius
            
            # If the tile has a value, draw the number with correct font size
            if value:
                text_color = TILE_COLORS.get(value, TILE_COLORS[2048])["text"]
                
                # Get font based on tile value
                font = TILE_FONTS.get(value, TILE_FONTS[2048])
                
                text_surface = font.render(str(value), True, text_color)
                text_rect = text_surface.get_rect(center=tile_rect.center)
                screen.blit(text_surface, text_rect)
                
    pygame.display.flip()

def add_new_tile():
    empty_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] == 0]
    if empty_cells:
        r, c = random.choice(empty_cells)
        grid[r][c] = 2 if random.random() < 0.9 else 4

def move_grid(direction):
    global score
    moved = False
    for _ in range(direction):
        grid[:] = np.rot90(grid)
    
    for row in range(GRID_SIZE):
        filtered = [num for num in grid[row] if num != 0]
        new_row = []
        skip = False
        for i in range(len(filtered)):
            if skip:
                skip = False
                continue
            if i < len(filtered) - 1 and filtered[i] == filtered[i + 1]:
                new_row.append(filtered[i] * 2)
                score += filtered[i] * 2
                skip = True
            else:
                new_row.append(filtered[i])
        new_row += [0] * (GRID_SIZE - len(new_row))
        if not np.array_equal(grid[row], new_row):
            moved = True
        grid[row] = new_row
    
    for _ in range(4 - direction):
        grid[:] = np.rot90(grid)
    
    if moved:
        add_new_tile()

def check_game_over():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col] == 0:
                return False
            if col < GRID_SIZE - 1 and grid[row][col] == grid[row][col + 1]:
                return False
            if row < GRID_SIZE - 1 and grid[row][col] == grid[row + 1][col]:
                return False
    return True

def game_over_screen():
    # First draw the game state in the background
    draw_grid()
    
    # Create semi-transparent overlay (matching original style)
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.fill((250, 248, 239))
    overlay.set_alpha(200)
    screen.blit(overlay, (0, 0))
    
    # Create a game over message panel
    message_width = 300
    message_height = 100
    message_rect = pygame.Rect(
        (WINDOW_WIDTH - message_width) // 2, 
        (WINDOW_HEIGHT - message_height) // 2 - 20,
        message_width, message_height
    )
    
    # Game over text
    game_over_text = TITLE_FONT.render("Game Over!", True, TEXT_DARK)
    game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, message_rect.centery))
    
    # Try again button (matching original style)
    button_width = 130
    button_height = 40
    button_rect = pygame.Rect(
        (WINDOW_WIDTH - button_width) // 2,
        message_rect.bottom + 20,
        button_width, button_height
    )
    draw_rounded_rect(screen, button_rect, GRID_COLOR, 0.1)
    
    try_again_text = BUTTON_FONT.render("Try again", True, TEXT_LIGHT)
    try_again_rect = try_again_text.get_rect(center=button_rect.center)
    
    # Display elements
    screen.blit(game_over_text, game_over_rect)
    screen.blit(try_again_text, try_again_rect)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    return True
    return True

def check_win():
    """Check if the player has reached 2048 tile"""
    return 2048 in grid

def you_win_screen():
    # First draw the game state in the background
    draw_grid()
    
    # Create semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.fill((250, 248, 239))
    overlay.set_alpha(200)
    screen.blit(overlay, (0, 0))
    
    # Create a win message panel
    message_width = 300
    message_height = 150
    message_rect = pygame.Rect(
        (WINDOW_WIDTH - message_width) // 2, 
        (WINDOW_HEIGHT - message_height) // 2 - 20,
        message_width, message_height
    )
    
    # Win text
    win_text = TITLE_FONT.render("You Win!", True, TEXT_DARK)
    win_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, message_rect.centery - 20))
    
    # Instructions text
    continue_text = INSTRUCTION_FONT.render("Keep going to reach higher scores!", True, TEXT_DARK)
    continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH // 2, message_rect.centery + 20))
    
    # Continue button
    continue_button_width = 130
    continue_button_height = 40
    continue_button_rect = pygame.Rect(
        (WINDOW_WIDTH - continue_button_width) // 2 - 75,
        message_rect.bottom + 20,
        continue_button_width, continue_button_height
    )
    draw_rounded_rect(screen, continue_button_rect, GRID_COLOR, 0.1)
    
    continue_button_text = BUTTON_FONT.render("Continue", True, TEXT_LIGHT)
    continue_button_text_rect = continue_button_text.get_rect(center=continue_button_rect.center)
    
    # New game button
    new_game_button_width = 130
    new_game_button_height = 40
    new_game_button_rect = pygame.Rect(
        (WINDOW_WIDTH - new_game_button_width) // 2 + 75,
        message_rect.bottom + 20,
        new_game_button_width, new_game_button_height
    )
    draw_rounded_rect(screen, new_game_button_rect, GRID_COLOR, 0.1)
    
    new_game_button_text = BUTTON_FONT.render("New Game", True, TEXT_LIGHT)
    new_game_button_text_rect = new_game_button_text.get_rect(center=new_game_button_rect.center)
    
    # Display elements
    screen.blit(win_text, win_rect)
    screen.blit(continue_text, continue_rect)
    screen.blit(continue_button_text, continue_button_text_rect)
    screen.blit(new_game_button_text, new_game_button_text_rect)
    pygame.display.flip()
    
    # Handle user input
    waiting = True
    start_new_game = False
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_c:
                    waiting = False
                elif event.key == pygame.K_n:
                    waiting = False
                    start_new_game = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if continue_button_rect.collidepoint(mouse_pos):
                    waiting = False
                if new_game_button_rect.collidepoint(mouse_pos):
                    waiting = False
                    start_new_game = True
    
    if start_new_game:
        # Reset the game
        global grid, score
        grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        score = 0
        add_new_tile()
        add_new_tile()
    
    return True  # Continue playing

def main():
    global grid, score, best_score
    
    # Reset the game
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    score = 0
    
    # Track if the win screen has been shown
    win_shown = False
    
    # Add initial tiles
    add_new_tile()
    add_new_tile()
    
    running = True
    while running:
        draw_grid()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                moved = False
                
                if event.key == pygame.K_LEFT:
                    move_grid(0)
                    moved = True
                elif event.key == pygame.K_UP:
                    move_grid(1)
                    moved = True
                elif event.key == pygame.K_RIGHT:
                    move_grid(2)
                    moved = True
                elif event.key == pygame.K_DOWN:
                    move_grid(3)
                    moved = True
                
                # Update best score
                if score > best_score:
                    best_score = score
                
                # Check for win
                if moved and check_win() and not win_shown:
                    win_shown = True
                    if not you_win_screen():
                        running = False
                
                # Check for game over
                if check_game_over():
                    if game_over_screen():
                        # Reset game
                        grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
                        score = 0
                        win_shown = False
                        add_new_tile()
                        add_new_tile()
                    else:
                        running = False
            
            # Check for mouse clicks on the "New Game" button
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                button_width = 130
                button_height = 40
                button_x = WINDOW_WIDTH - button_width - PADDING
                button_y = PADDING + 10 + 55 + 10
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                
                if button_rect.collidepoint(mouse_pos):
                    # Reset game
                    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
                    score = 0
                    win_shown = False
                    add_new_tile()
                    add_new_tile()

# Start the game
if __name__ == "__main__":
    main()
    pygame.quit()