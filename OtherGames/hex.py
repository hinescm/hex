import pygame
import math
import random
import sys

# --- Global Game Constants (can be adjusted for both modes if desired, or passed as args) ---
BOARD_SIZE = 5 # Example board size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CAPTION = "Hex Game"
HEX_RADIUS = 30 # pixels

# --- Global Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GRAY = (50, 50, 50)
HEX_OUTLINE_COLOR = BLACK
EMPTY_HEX_COLOR = (180, 180, 180)

# --- Global Fonts (for GUI) ---
FONT_SMALL = None # Initialized after pygame.init()
FONT_MEDIUM = None
FONT_LARGE = None

# --- Common Game Logic Functions (accessible by both GUI and Terminal) ---
def initialize_board(board_size):
    """Initializes an empty Hex board of a given size."""
    return [[0] * board_size for _ in range(board_size)]

def get_neighbors(board, r, c):
    """
    Returns a list of valid neighboring cell coordinates (r, c) for a given cell.
    A Hex cell has 6 neighbors. Checks for board boundaries are performed.
    """
    board_size = len(board)
    neighbors = []
    directions = [
        (0, -1), (0, 1),   # Left, Right
        (-1, 0), (1, 0),   # Top-left, Bottom-right
        (-1, 1), (1, -1)   # Top-right, Bottom-left
    ]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < board_size and 0 <= nc < board_size:
            neighbors.append((nr, nc))
    return neighbors

def check_win(board, player_id):
    """
    Checks if the given player has won the game by connecting their designated sides.
    """
    board_size = len(board)
    visited = set()

    def dfs(r, c):
        if not (0 <= r < board_size and 0 <= c < board_size) or (r, c) in visited or board[r][c] != player_id:
            return False

        visited.add((r, c))

        if player_id == 1: # Player 1 connects top (row 0) to bottom (row board_size-1)
            if r == board_size - 1:
                return True
        elif player_id == 2: # Player 2 connects left (col 0) to right (col board_size-1)
            if c == board_size - 1:
                return True

        for nr, nc in get_neighbors(board, r, c):
            if dfs(nr, nc):
                return True
        return False

    if player_id == 1:
        for c in range(board_size):
            if board[0][c] == player_id:
                if dfs(0, c):
                    return True
    elif player_id == 2:
        for r in range(board_size):
            if board[r][0] == player_id:
                if dfs(r, 0):
                    return True
    return False

def make_move(board, row, col, player_id, verbose=False): # verbose=False by default for GUI
    """Allows a player to make a move on the Hex board, with optional verbose output."""
    board_size = len(board)
    if not (0 <= row < board_size and 0 <= col < board_size):
        if verbose: print(f"Invalid move: coordinates ({row}, {col}) out of bounds.")
        return False
    if board[row][col] != 0:
        if verbose: print(f"Invalid move: cell ({row}, {col}) is already occupied by player {board[row][col]}.")
        return False
    board[row][col] = player_id
    if verbose: print(f"Player {player_id} placed a piece at ({row}, {col}).")
    return True

def ai_make_move(board, player_id):
    """
    A simple AI player that makes a random valid move.

    Args:
        board (list[list[int]]): The current Hex board.
        player_id (int): The ID of the AI player (1 or 2).

    Returns:
        tuple[int, int] or None: A (row, col) tuple for the chosen move,
                                 or None if no valid moves are available.
    """
    board_size = len(board)
    available_moves = []

    for r in range(board_size):
        for c in range(board_size):
            if board[r][c] == 0: # Check if the cell is empty
                available_moves.append((r, c))

    if available_moves:
        chosen_move = random.choice(available_moves)
        return chosen_move
    else:
        return None

# --- GUI Specific Geometry Functions (defined globally but rely on dynamic offsets) ---
def _get_relative_hex_center(row, col, hex_radius):
    """
    Calculates the center pixel coordinates (x, y) for a Hex board coordinate (row, col)
    relative to a (0,0) origin, for a pointy-top orientation (staggered grid).
    """
    hex_width_flat = hex_radius * math.sqrt(3) # distance between vertical centers
    hex_height_pointy = hex_radius * 1.5 # distance between horizontal centers (3/4 of hex_height for vertical stacking)

    x = col * hex_width_flat + (row * hex_width_flat / 2)
    y = row * hex_height_pointy

    return x, y

def get_hex_vertices(center_x, center_y, hex_radius):
    """
    Returns a list of 6 (x, y) tuples representing the vertices of a hexagon.
    Assumes a pointy-top hexagon orientation.
    """
    vertices = []
    for i in range(6):
        angle_deg = 30 + 60 * i # Offset by 30 for pointy-top hex
        angle_rad = math.pi / 180 * angle_deg
        x = center_x + hex_radius * math.cos(angle_rad)
        y = center_y + hex_radius * math.sin(angle_rad)
        vertices.append((int(x), int(y)))
    return vertices


def play_gui_game(board_size):
    """
    Runs the Hex game with a Pygame GUI.
    """
    global FONT_SMALL, FONT_MEDIUM, FONT_LARGE # Access global font variables

    # Initialize Pygame in case it was quit previously
    if not pygame.get_init():
        pygame.init()

    # Initialize fonts
    FONT_SMALL = pygame.font.Font(None, 30)
    FONT_MEDIUM = pygame.font.Font(None, 40)
    FONT_LARGE = pygame.font.Font(None, 74)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(CAPTION)

    # --- Game State --- #
    def reset_game_state():
        nonlocal game_board, current_player, turn_count, game_over, winner, message
        game_board = initialize_board(board_size)
        current_player = 1 # Player 1 (Red) starts
        turn_count = 0
        game_over = False
        winner = None
        message = f"Player {current_player}'s turn."

    game_board = None # Will be initialized by reset_game_state
    current_player = None
    turn_count = None
    game_over = None
    winner = None
    message = None
    reset_game_state() # Initialize game state

    # --- Calculate global offsets for centering the board ---
    min_board_x = float('inf')
    max_board_x = float('-inf')
    min_board_y = float('inf')
    max_board_y = float('-inf')

    for r_temp in range(board_size):
        for c_temp in range(board_size):
            center_x_temp, center_y_temp = _get_relative_hex_center(r_temp, c_temp, HEX_RADIUS)
            vertices_temp = get_hex_vertices(center_x_temp, center_y_temp, HEX_RADIUS)
            for vx, vy in vertices_temp:
                min_board_x = min(min_board_x, vx)
                max_board_x = max(max_board_x, vx)
                min_board_y = min(min_board_y, vy)
                max_board_y = max(max_board_y, vy)

    total_board_pixel_width = max_board_x - min_board_x
    total_board_pixel_height = max_board_y - min_board_y

    global_offset_x = (SCREEN_WIDTH - total_board_pixel_width) / 2 - min_board_x
    global_offset_y = (SCREEN_HEIGHT - total_board_pixel_height) / 2 - min_board_y

    def get_hex_pixel_pos_final(row, col, hex_radius_local):
        relative_x, relative_y = _get_relative_hex_center(row, col, hex_radius_local)
        return int(relative_x + global_offset_x), int(relative_y + global_offset_y)

    def get_hex_at_mouse_pos(mouse_pos, hex_radius_local):
        for r in range(board_size):
            for c in range(board_size):
                center_x, center_y = get_hex_pixel_pos_final(r, c, hex_radius_local)
                distance = math.sqrt((mouse_pos[0] - center_x)**2 + (mouse_pos[1] - center_y)**2)
                if distance < hex_radius_local * 0.9: # Check within 90% of radius
                    return r, c
        return None

    # --- Game Mode Selection Buttons ---
    button_font = pygame.font.Font(None, 28)
    button_width = 180 # Increased width
    button_height = 45 # Increased height
    button_x = SCREEN_WIDTH - button_width - 20
    button_y_start = 100
    button_spacing = 50

    modes = {
        'hvh': {'text': 'Human vs Human', 'rect': pygame.Rect(button_x, button_y_start, button_width, button_height)},
        'hva': {'text': 'Human vs AI', 'rect': pygame.Rect(button_x, button_y_start + button_spacing, button_width, button_height)},
        'ava': {'text': 'AI vs AI', 'rect': pygame.Rect(button_x, button_y_start + 2 * button_spacing, button_width, button_height)}
    }
    game_mode = None

    # Replay Button
    replay_button_rect = pygame.Rect(button_x, button_y_start + 4 * button_spacing, button_width, button_height)

    # --- Main Game Loop ---
    running = True
    while running:
        # Determine if current player is AI or Human
        is_player_1_human = (game_mode == 'hvh' or game_mode == 'hva')
        is_player_2_human = (game_mode == 'hvh')

        current_player_is_human = (current_player == 1 and is_player_1_human) or \
                                  (current_player == 2 and is_player_2_human)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if game_mode is None: # Mode selection phase
                    for mode_key, mode_info in modes.items():
                        if mode_info['rect'].collidepoint(mouse_x, mouse_y):
                            game_mode = mode_key
                            message = f"Game mode: {mode_info['text']}"
                            reset_game_state() # Reset game after mode selection
                            break
                elif replay_button_rect.collidepoint(mouse_x, mouse_y): # Replay button clicked
                    game_mode = None # Go back to mode selection
                    reset_game_state()
                    message = "Select game mode"
                elif not game_over and current_player_is_human: # Game is active, human player's turn
                    clicked_hex = get_hex_at_mouse_pos((mouse_x, mouse_y), HEX_RADIUS)

                    if clicked_hex:
                        r, c = clicked_hex
                        if make_move(game_board, r, c, current_player): # verbose=False is default
                            if check_win(game_board, current_player):
                                game_over = True
                                winner = current_player
                                message = f"Player {winner} wins!"
                            else:
                                current_player = 3 - current_player # Switch player
                                message = f"Player {current_player}'s turn."
                        else:
                            message = "Invalid move: cell occupied or out of bounds."
                    else:
                        message = "Invalid click: Outside of any hexagon."

        # AI move logic
        if game_mode is not None and not game_over and not current_player_is_human:
            pygame.time.wait(500) # Small delay for AI moves
            ai_move = ai_make_move(game_board, current_player)
            if ai_move:
                r, c = ai_move
                if make_move(game_board, r, c, current_player): # verbose=False is default
                    if check_win(game_board, current_player):
                        game_over = True
                        winner = current_player
                        message = f"Player {winner} (AI) wins!"
                    else:
                        current_player = 3 - current_player
                        message = f"Player {current_player}'s turn."
            else:
                message = "AI found no valid moves. Game might be stuck."
                game_over = True # Should not happen unless board is full

        screen.fill(DARK_GRAY) # Background color

        # Display game mode selection buttons
        if game_mode is None:
            text_surface = FONT_MEDIUM.render(message, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
            screen.blit(text_surface, text_rect)

            for mode_key, mode_info in modes.items():
                pygame.draw.rect(screen, BLUE, mode_info['rect'], border_radius=5)
                mode_text_surface = button_font.render(mode_info['text'], True, WHITE)
                mode_text_rect = mode_text_surface.get_rect(center=mode_info['rect'].center)
                screen.blit(mode_text_surface, mode_text_rect)
        else:
            # Display current player's turn or game messages
            turn_text_color = RED if current_player == 1 else BLUE
            if game_over:
                final_message_surface = FONT_LARGE.render(message, True, turn_text_color)
                final_message_rect = final_message_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
                screen.blit(final_message_surface, final_message_rect)
            else:
                turn_text_surface = FONT_MEDIUM.render(message, True, turn_text_color)
                turn_text_rect = turn_text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
                screen.blit(turn_text_surface, turn_text_rect)

            # Draw Replay Button
            pygame.draw.rect(screen, (0, 150, 0), replay_button_rect, border_radius=5)
            replay_text_surface = button_font.render("Replay / Change Mode", True, WHITE)
            replay_text_rect = replay_text_surface.get_rect(center=replay_button_rect.center)
            screen.blit(replay_text_surface, replay_text_rect)

            # Draw the Hex board
            for r in range(board_size):
                for c in range(board_size):
                    center_x, center_y = get_hex_pixel_pos_final(r, c, HEX_RADIUS)
                    vertices = get_hex_vertices(center_x, center_y, HEX_RADIUS)

                    cell_value = game_board[r][c]
                    cell_color = EMPTY_HEX_COLOR
                    if cell_value == 1:
                        cell_color = RED
                    elif cell_value == 2:
                        cell_color = BLUE

                    pygame.draw.polygon(screen, cell_color, vertices) # Fill hexagon
                    pygame.draw.polygon(screen, HEX_OUTLINE_COLOR, vertices, 1) # Draw outline

            # --- Draw Board Boundaries ---
            # The `global_offset_x`, `global_offset_y`, `total_board_pixel_width`, `total_board_pixel_height`
            # define the bounding box of the entire hex grid (from min_board_x/y to max_board_x/y)
            # adjusted by the global offset to be centered on screen.

            # Adjusted boundary drawing to encompass the entire grid, not just corner hexes
            board_left_bound = global_offset_x + min_board_x
            board_right_bound = global_offset_x + max_board_x
            board_top_bound = global_offset_y + min_board_y
            board_bottom_bound = global_offset_y + max_board_y

            line_thickness = 5

            # Red Player (Top to Bottom connection) boundary lines
            # Top line
            pygame.draw.line(screen, RED, (board_left_bound, board_top_bound), (board_right_bound, board_top_bound), line_thickness)
            # Bottom line
            pygame.draw.line(screen, RED, (board_left_bound, board_bottom_bound), (board_right_bound, board_bottom_bound), line_thickness)

            # Blue Player (Left to Right connection) boundary lines
            # Left line
            pygame.draw.line(screen, BLUE, (board_left_bound, board_top_bound), (board_left_bound, board_bottom_bound), line_thickness)
            # Right line
            pygame.draw.line(screen, BLUE, (board_right_bound, board_top_bound), (board_right_bound, board_bottom_bound), line_thickness)

        pygame.display.flip() # Update the full display Surface to the screen

    pygame.quit()
    print("Pygame quit.")
    sys.exit()

def play_terminal_game(board_size):
    """
    Runs the main game loop for Hex in the terminal.
    """
    board = initialize_board(board_size)
    current_player = 1
    turn_count = 0
    game_over = False

    print(f"\n--- Starting Hex Game (Board Size: {board_size}x{board_size}) ---")
    print("Player 1 (Red) connects top to bottom. Player 2 (Blue) connects left to right.")

    # Game Mode Selection for terminal
    game_mode = None
    while game_mode not in ['hvh', 'hva', 'ava']:
        mode_input = input("Select game mode (HvH: Human vs Human, HvA: Human vs AI, AvA: AI vs AI): ").lower()
        if mode_input == 'hvh':
            game_mode = 'hvh'
            print("Game mode: Human vs Human")
        elif mode_input == 'hva':
            game_mode = 'hva'
            print("Game mode: Human vs AI")
        elif mode_input == 'ava':
            game_mode = 'ava'
            print("Game mode: AI vs AI")
        else:
            print("Invalid game mode. Please choose 'hvh', 'hva', or 'ava'.")

    # Display board (simple text display for terminal mode)
    def display_board_terminal(board):
        board_size_t = len(board)
        print("\n--- Current Hex Board ---")
        col_headers = "  " + " ".join(str(i) for i in range(board_size_t))
        print(col_headers)

        for r_idx, row in enumerate(board):
            indent = " " * r_idx
            row_str = " ".join(str(cell) for cell in row)
            print(f"{indent}{r_idx} {row_str}")
        print("-------------------------")

    while not game_over:
        display_board_terminal(board)
        print(f"It's Player {current_player}'s turn.")

        # Determine if current player is AI or Human
        is_player_1_human = (game_mode == 'hvh' or game_mode == 'hva')
        is_player_2_human = (game_mode == 'hvh')

        current_player_is_human = (current_player == 1 and is_player_1_human) or \
                                  (current_player == 2 and is_player_2_human)

        # Implement the 'Swap Rule' for Player 2 on the first move
        if turn_count == 1 and current_player == 2 and is_player_2_human: # After Player 1's first move, it's P2's turn
            while True:
                swap_choice = input("Player 2, would you like to swap (yes/no)? ").lower()
                if swap_choice in ['yes', 'no']:
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")

            if swap_choice == 'yes':
                print("Player 2 chose to swap! Player 1's piece is now Player 2's, and the turn order is reversed.")
                for r in range(board_size):
                    for c in range(board_size):
                        if board[r][c] == 1:
                            board[r][c] = 2
                        elif board[r][c] == 2:
                            board[r][c] = 1
                current_player = 1 # The original P1 (now playing with '2' pieces) starts again
                display_board_terminal(board)
                print(f"It's Player {current_player}'s turn (after swap).")
            else:
                print("Player 2 chose not to swap.")

        move_made = False
        while not move_made:
            if current_player_is_human:
                try:
                    move_input = input(f"Player {current_player}, enter your move (row, col): ")
                    r, c = map(int, move_input.split(','))
                    move_made = make_move(board, r, c, current_player, verbose=True)
                except ValueError:
                    print("Invalid input. Please enter row and column as two numbers separated by a comma (e.g., '1,2').")
                except Exception as e:
                    print(f"An error occurred: {e}")
            else: # AI's turn
                ai_move = ai_make_move(board, current_player)
                if ai_move:
                    r, c = ai_move
                    move_made = make_move(board, r, c, current_player, verbose=True)
                    print(f"AI Player {current_player} moved to ({r}, {c}).")
                else:
                    print("AI found no valid moves. This should not happen in a non-full board.")
                    game_over = True # End game if AI has no moves (e.g., board full)
                    break

        if game_over: # Break out of game loop if AI couldn't make a move
            break

        turn_count += 1

        if check_win(board, current_player):
            display_board_terminal(board)
            print(f"\n!!! Player {current_player} wins the game! Congratulations! !!!")
            game_over = True
            break

        current_player = 3 - current_player # Switches between 1 and 2
    print("--- HEX GAME END ---")

def main():
    """
    Main entry point for the Hex game, allowing choice between terminal and GUI.
    """
    game_type = None
    while game_type not in ['t', 'g']:
        game_type = input("Choose game interface (T for Terminal, G for GUI): ").lower()
        if game_type not in ['t', 'g']:
            print("Invalid choice. Please enter 'T' or 'G'.")

    if game_type == 't':
        play_terminal_game(BOARD_SIZE)
    elif game_type == 'g':
        # Initialize Pygame only if GUI is chosen
        if not pygame.get_init():
            pygame.init()
        play_gui_game(BOARD_SIZE)

if __name__ == "__main__":
    main()