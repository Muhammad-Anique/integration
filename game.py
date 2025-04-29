import pygame
import random
import os
import json
import time

# Initialize Pygame
pygame.init()

# --- Window Settings ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 480
GRID_SIZE = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)  # New color for obstacle
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake and Tic-Tac-Toe Games")
CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(None, 24)
BIG_FONT = pygame.font.Font(None, 48)  # Larger font for menu

# --- Game Logic ---

# --- Snake Game Functions ---
def generate_food(snake_body, obstacle_position):
    """
    Generates the position of the food, ensuring it does not overlap with the snake or the obstacle.
    """
    while True:
        x = random.randrange(0, SCREEN_WIDTH // GRID_SIZE) * GRID_SIZE
        y = random.randrange(0, SCREEN_HEIGHT // GRID_SIZE) * GRID_SIZE
        food_position = (x, y)
        if food_position not in snake_body and food_position != obstacle_position:
            return food_position

def generate_obstacle(snake_body, food_position):
    """
    Generates the position of the obstacle, ensuring it does not overlap with the snake or the food.
    If the snake is too short, don't generate any obstacles.
    """
    if len(snake_body) < 5:  # Don't generate obstacle until snake has some length
        return None

    while True:
        x = random.randrange(0, SCREEN_WIDTH // GRID_SIZE) * GRID_SIZE
        y = random.randrange(0, SCREEN_HEIGHT // GRID_SIZE) * GRID_SIZE
        obstacle_position = (x, y)
        if obstacle_position not in snake_body and obstacle_position != food_position:
            return obstacle_position

def draw_snake(snake_body, color=GREEN):
    """Draws the snake on the screen."""
    for x, y in snake_body:
        pygame.draw.rect(SCREEN, color, (x, y, GRID_SIZE, GRID_SIZE))

def draw_food(food_position, color=RED):
    """Draws the food on the screen."""
    pygame.draw.rect(SCREEN, color, (food_position[0], food_position[1], GRID_SIZE, GRID_SIZE))

def draw_obstacle(obstacle_position, color=BLUE):
    """Draws the obstacle on the screen."""
    if obstacle_position:  # Make sure it's not None
        pygame.draw.rect(SCREEN, color, (obstacle_position[0], obstacle_position[1], GRID_SIZE, GRID_SIZE))

def save_game(snake_body, food_position, direction, score, obstacle_position, game_over, game_type="snake"):
    """Saves the game state to a JSON file, includes game type."""
    game_data = {
        "game_type": game_type,  # Add game type
        "snake_body": snake_body,
        "food_position": food_position,
        "direction": direction,
        "score": score,
        "obstacle_position": obstacle_position,
        "game_over": game_over
    }
    try:
        with open("game_save.json", "w") as f:  #generalized filename
            json.dump(game_data, f)
        print("Game saved successfully!")
    except Exception as e:
        print(f"Error saving game: {e}")

def load_game():
    """Loads the game state from a JSON file."""
    if not os.path.exists("game_save.json"): #generalized filename
        return None
    try:
        with open("game_save.json", "r") as f:
            game_data = json.load(f)
        print("Game loaded successfully!")
        return game_data  # Return the entire game data dictionary
    except Exception as e:
        print(f"Error loading game: {e}")
        return None

def snake_game(screen):
    """Runs the Snake game."""
    # --- Initialize Game Variables ---
    load_data = load_game()
    if load_data and load_data["game_type"] == "snake":
        snake_body, food_position, direction, score, obstacle_position, game_over = (
            load_data["snake_body"],
            load_data["food_position"],
            load_data["direction"],
            load_data["score"],
            load_data["obstacle_position"],
            load_data["game_over"],
        )
    else:
        snake_body = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        food_position = generate_food(snake_body, None)
        direction = random.choice([(0, -GRID_SIZE), (0, GRID_SIZE), (GRID_SIZE, 0), (-GRID_SIZE, 0)])
        score = 0
        obstacle_position = generate_obstacle(snake_body, food_position)
        game_over = False

    game_running = True
    input_queue = []

    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                return  # Exit the game loop, return to main
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction[1] == 0:
                    input_queue.append((0, -GRID_SIZE))
                elif event.key == pygame.K_DOWN and direction[1] == 0:
                    input_queue.append((0, GRID_SIZE))
                elif event.key == pygame.K_LEFT and direction[0] == 0:
                    input_queue.append((-GRID_SIZE, 0))
                elif event.key == pygame.K_RIGHT and direction[0] == 0:
                    input_queue.append((GRID_SIZE, 0))
                elif event.key == pygame.K_s:
                    save_game(snake_body, food_position, direction, score, obstacle_position, game_over, "snake")
                elif event.key == pygame.K_l:
                    load_data = load_game()
                    if load_data and load_data["game_type"] == "snake":
                        snake_body, food_position, direction, score, obstacle_position, game_over = (
                            load_data["snake_body"],
                            load_data["food_position"],
                            load_data["direction"],
                            load_data["score"],
                            load_data["obstacle_position"],
                            load_data["game_over"],
                        )
                    else:
                        display_message("No saved Snake game found!", RED, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
                        pygame.display.update()
                        time.sleep(2)
                elif event.key == pygame.K_r:  # reset
                    game_over = False
                    snake_body = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
                    food_position = generate_food(snake_body, None)
                    direction = random.choice(
                        [(0, -GRID_SIZE), (0, GRID_SIZE), (GRID_SIZE, 0), (-GRID_SIZE, 0)]
                    )
                    score = 0
                    obstacle_position = generate_obstacle(snake_body, food_position)

        if input_queue:
            direction = input_queue.pop(0)

        if not game_over:
            # --- Update Snake Position ---
            head_x, head_y = snake_body[0]
            new_head = (head_x + direction[0], head_y + direction[1])

            # --- Check for Boundaries and Collision with itself ---
            if (
                new_head[0] < 0
                or new_head[0] >= SCREEN_WIDTH
                or new_head[1] < 0
                or new_head[1] >= SCREEN_HEIGHT
                or new_head in snake_body[1:]
            ):
                game_over = True
                continue

            # --- Check for Collision with Obstacle ---
            if obstacle_position and new_head == obstacle_position:
                game_over = True
                continue

            snake_body.insert(0, new_head)

            # --- Check for Eating Food ---
            if new_head == food_position:
                score += 10
                food_position = generate_food(snake_body, obstacle_position)
                obstacle_position = generate_obstacle(snake_body, food_position)
            else:
                snake_body.pop()

            # --- Draw Everything ---
            screen.fill(BLACK)
            draw_snake(snake_body)
            draw_food(food_position)
            draw_obstacle(obstacle_position)
            display_message(f"Score: {score}", WHITE, 10, 10)
            pygame.display.update()

            # --- Control Game Speed ---
            CLOCK.tick(10)

        else:
            game_over_screen(screen, score)
            return  # Return to the main menu after game over

# --- Tic-Tac-Toe Game Functions ---
def draw_board(screen, board):
    """Draws the Tic-Tac-Toe board on the screen."""
    for row in range(3):
        for col in range(3):
            x = col * GRID_SIZE * 3
            y = row * GRID_SIZE * 3
            pygame.draw.rect(screen, WHITE, (x, y, GRID_SIZE * 3, GRID_SIZE * 3), 2)
            if board[row][col] == "X":
                display_message("X", WHITE, x + GRID_SIZE, y + GRID_SIZE)
            elif board[row][col] == "O":
                display_message("O", WHITE, x + GRID_SIZE, y + GRID_SIZE)

def check_win(board):
    """Checks if there is a winner."""
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] != " ":
            return board[row][0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != " ":
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]
    return None

def check_tie(board):
    """Checks if the game is a tie."""
    for row in range(3):
        for col in range(3):
            if board[row][col] == " ":
                return False
    return True

def tic_tac_toe_game(screen):
    """Runs the Tic-Tac-Toe game."""
    board = [[" " for _ in range(3)] for _ in range(3)]
    player = "X"
    game_over = False

    load_data = load_game()
    if load_data and load_data["game_type"] == "tic_tac_toe":
        board = load_data["board"]
        player = load_data["player"]
        game_over = load_data["game_over"]
    else:
        board = [[" " for _ in range(3)] for _ in range(3)]
        player = "X"
        game_over = False

    game_running = True

    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                return  # Exit to main menu
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                col = x // (GRID_SIZE * 3)
                row = y // (GRID_SIZE * 3)
                if board[row][col] == " ":
                    board[row][col] = player
                    if check_win(board):
                        game_over = True
                        winner = check_win(board)
                        print(f"Player {winner} wins!")
                    elif check_tie(board):
                        game_over = True
                        winner = "Tie"
                        print("It's a tie!")
                    else:
                        player = "O" if player == "X" else "X"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_game(board=board, player=player, game_over=game_over, game_type="tic_tac_toe")
                elif event.key == pygame.K_l:
                    load_data = load_game()
                    if load_data and load_data["game_type"] == "tic_tac_toe":
                        board = load_data["board"]
                        player = load_data["player"]
                        game_over = load_data["game_over"]
                    else:
                        display_message("No saved Tic-Tac-Toe game found!", RED, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
                        pygame.display.update()
                        time.sleep(2)
                elif event.key == pygame.K_r:  # reset
                    game_over = False
                    board = [[" " for _ in range(3)] for _ in range(3)]
                    player = "X"

        screen.fill(BLACK)
        draw_board(screen, board)
        if game_over:
            if winner == "Tie":
                display_message("It's a Tie!", WHITE, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3)
            else:
                display_message(f"Player {winner} wins!", WHITE, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3)
        pygame.display.update()
        CLOCK.tick(10)
    return  # Return to the main menu after game over

def display_message(message, color, x, y):
    """Displays a text message on the screen."""
    text = FONT.render(message, True, color)
    SCREEN.blit(text, (x, y))

def main():
    """Main function to run the game."""
    game_running = True
    selected_game = None  # None until a game is selected

    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_game = "snake"
                elif event.key == pygame.K_2:
                    selected_game = "tic_tac_toe"

        SCREEN.fill(BLACK)
        display_message("Select a Game:", WHITE, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3)
        display_message("1. Snake", WHITE, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3 + 30)
        display_message("2. Tic-Tac-Toe", WHITE, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3 + 60)
        pygame.display.update()

        if selected_game == "snake":
            snake_game(SCREEN)  # Pass the screen
            selected_game = None  # Reset after game finishes
        elif selected_game == "tic_tac_toe":
            tic_tac_toe_game(SCREEN)
            selected_game = None
        CLOCK.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()
