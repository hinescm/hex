import pygame
import math
import random
import sys

# --- Global Game Constants ---
BOARD_SIZE = 5 
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CAPTION = "Hex Game - Topology & Perimeter Final"
HEX_RADIUS = 30 

# --- Global Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GOLD = (255, 215, 0) 
DARK_GRAY = (40, 40, 40)
EMPTY_HEX_COLOR = (180, 180, 180)

# --- Core Game Logic ---
def initialize_board(board_size):
    return [[0] * board_size for _ in range(board_size)]

def get_neighbors(board, r, c):
    board_size = len(board)
    neighbors = []
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, 1), (1, -1)]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < board_size and 0 <= nc < board_size:
            neighbors.append((nr, nc))
    return neighbors

def find_winning_path(board, player_id):
    board_size = len(board)
    visited = set()
    
    def dfs(r, c, path):
        if (r, c) in visited or board[r][c] != player_id:
            return None
        visited.add((r, c))
        new_path = path + [(r, c)]
        if player_id == 1 and r == board_size - 1: return new_path
        if player_id == 2 and c == board_size - 1: return new_path
        for nr, nc in get_neighbors(board, r, c):
            res = dfs(nr, nc, new_path)
            if res: return res
        return None

    if player_id == 1:
        for c in range(board_size):
            if board[0][c] == player_id:
                res = dfs(0, c, [])
                if res: return res
    elif player_id == 2:
        for r in range(board_size):
            if board[r][0] == player_id:
                res = dfs(r, 0, [])
                if res: return res
    return None

def make_move(board, row, col, player_id):
    if board[row][col] == 0:
        board[row][col] = player_id
        return True
    return False

def ai_make_move(board):
    board_size = len(board)
    available = [(r, c) for r in range(board_size) for c in range(board_size) if board[r][c] == 0]
    return random.choice(available) if available else None

# --- UI & Rendering Helpers ---
def _get_relative_hex_center(row, col, hex_radius):
    hex_width = hex_radius * math.sqrt(3)
    x = col * hex_width + (row * hex_width / 2)
    y = row * hex_radius * 1.5
    return x, y

def get_hex_vertices(center_x, center_y, hex_radius):
    return [(int(center_x + hex_radius * math.cos(math.pi / 180 * (30 + 60 * i))),
             int(center_y + hex_radius * math.sin(math.pi / 180 * (30 + 60 * i)))) for i in range(6)]

def play_gui_game(board_size):
    pygame.init()
    font_small = pygame.font.Font(None, 28)
    font_medium = pygame.font.Font(None, 40)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(CAPTION)

    game_board = initialize_board(board_size)
    current_player, game_over, game_mode = 1, False, None
    message = "Select Game Mode"
    win_path = []

    # Centering math
    min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
    for r in range(board_size):
        for c in range(board_size):
            cx, cy = _get_relative_hex_center(r, c, HEX_RADIUS)
            for vx, vy in get_hex_vertices(cx, cy, HEX_RADIUS):
                min_x, max_x, min_y, max_y = min(min_x, vx), max(max_x, vx), min(min_y, vy), max(max_y, vy)
    offset_x = (SCREEN_WIDTH - (max_x - min_x)) / 2 - min_x
    offset_y = (SCREEN_HEIGHT - (max_y - min_y)) / 2 - min_y

    modes = {
        'hvh': {'text': 'Human vs Human', 'rect': pygame.Rect(SCREEN_WIDTH - 200, 100, 180, 45)},
        'hva': {'text': 'Human vs AI', 'rect': pygame.Rect(SCREEN_WIDTH - 200, 150, 180, 45)},
        'ava': {'text': 'AI vs AI', 'rect': pygame.Rect(SCREEN_WIDTH - 200, 200, 180, 45)}
    }
    replay_rect = pygame.Rect(SCREEN_WIDTH - 200, 300, 180, 45)

    running = True
    while running:
        current_is_ai = (game_mode == 'ava') or (game_mode == 'hva' and current_player == 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if game_mode is None:
                    for key, val in modes.items():
                        if val['rect'].collidepoint(mx, my):
                            game_mode, game_board, current_player, game_over, win_path = key, initialize_board(board_size), 1, False, []
                            message = f"Player {current_player}'s Turn"
                elif replay_rect.collidepoint(mx, my):
                    game_mode, message = None, "Select Game Mode"
                elif not game_over and not current_is_ai:
                    for r in range(board_size):
                        for c in range(board_size):
                            cx, cy = _get_relative_hex_center(r, c, HEX_RADIUS)
                            px, py = cx + offset_x, cy + offset_y
                            if math.sqrt((mx - px)**2 + (my - py)**2) < HEX_RADIUS * 0.9:
                                if make_move(game_board, r, c, current_player):
                                    path = find_winning_path(game_board, current_player)
                                    if path:
                                        game_over, message, win_path = True, f"Player {current_player} Wins!", path
                                    else:
                                        current_player = 3 - current_player
                                        message = f"Player {current_player}'s Turn"

        if game_mode is not None and not game_over and current_is_ai:
            pygame.time.delay(600)
            move = ai_make_move(game_board)
            if move and make_move(game_board, move[0], move[1], current_player):
                path = find_winning_path(game_board, current_player)
                if path:
                    game_over, message, win_path = True, f"Player {current_player} Wins!", path
                else:
                    current_player = 3 - current_player
                    message = f"Player {current_player}'s Turn"

        screen.fill(DARK_GRAY)
        
        if game_mode is not None:
            for r in range(board_size):
                for c in range(board_size):
                    cx, cy = _get_relative_hex_center(r, c, HEX_RADIUS)
                    px, py = cx + offset_x, cy + offset_y
                    verts = get_hex_vertices(px, py, HEX_RADIUS)
                    
                    # --- Boundary Rendering ---
                    b_thick = 8
                    if r == 0: # Red Top
                        pygame.draw.line(screen, RED, verts[4], verts[5], b_thick)
                        pygame.draw.line(screen, RED, verts[3], verts[4], b_thick)
                    if r == board_size - 1: # Red Bottom
                        pygame.draw.line(screen, RED, verts[0], verts[1], b_thick)
                        pygame.draw.line(screen, RED, verts[1], verts[2], b_thick)
                    if c == 0: # Blue Left (Outer shifted)
                        pygame.draw.line(screen, BLUE, verts[1], verts[2], b_thick)
                        pygame.draw.line(screen, BLUE, verts[2], verts[3], b_thick)
                    if c == board_size - 1: # Blue Right (Outer shifted)
                        pygame.draw.line(screen, BLUE, verts[4], verts[5], b_thick)
                        pygame.draw.line(screen, BLUE, verts[5], verts[0], b_thick)

                    # Draw Hex
                    color = RED if game_board[r][c] == 1 else BLUE if game_board[r][c] == 2 else EMPTY_HEX_COLOR
                    pygame.draw.polygon(screen, color, verts)
                    
                    if (r, c) in win_path:
                        pygame.draw.polygon(screen, GOLD, verts, 5)
                    else:
                        pygame.draw.polygon(screen, BLACK, verts, 1)

        msg_surf = font_medium.render(message, True, RED if current_player == 1 else BLUE)
        screen.blit(msg_surf, msg_surf.get_rect(center=(SCREEN_WIDTH // 2, 50)))

        if game_mode is None:
            for val in modes.values():
                pygame.draw.rect(screen, BLUE, val['rect'], border_radius=8)
                screen.blit(font_small.render(val['text'], True, WHITE), font_small.render(val['text'], True, WHITE).get_rect(center=val['rect'].center))
        else:
            pygame.draw.rect(screen, (0, 120, 0), replay_rect, border_radius=8)
            screen.blit(font_small.render("Change Mode", True, WHITE), font_small.render("Change Mode", True, WHITE).get_rect(center=replay_rect.center))

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    play_gui_game(BOARD_SIZE)