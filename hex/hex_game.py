import pygame
import math
import random
import sys

# --- Global Game Constants ---
BOARD_SIZE = 5 
SCREEN_WIDTH = 1200  
SCREEN_HEIGHT = 700
HEX_RADIUS = 42  # Larger size for better visibility
CAPTION = "Hex & Brouwer: Dual Representation"

# --- Global Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
GOLD = (255, 215, 0) 
DARK_GRAY = (25, 25, 25)
EMPTY_HEX_COLOR = (140, 140, 140)
GRAPH_EDGE_COLOR = (90, 90, 90)

# --- Logic ---
def initialize_board(board_size):
    return [[0] * board_size for _ in range(board_size)]

def get_neighbors(r, c, board_size):
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
        if (r, c) in visited or board[r][c] != player_id: return None
        visited.add((r, c))
        new_path = path + [(r, c)]
        if player_id == 1 and r == board_size - 1: return new_path
        if player_id == 2 and c == board_size - 1: return new_path
        for nr, nc in get_neighbors(r, c, board_size):
            res = dfs(nr, nc, new_path)
            if res: return res
        return None
    if player_id == 1:
        for c in range(board_size):
            if board[0][c] == player_id:
                res = dfs(0, c, [])
                if res: return res
    else:
        for r in range(board_size):
            if board[r][0] == player_id:
                res = dfs(r, 0, [])
                if res: return res
    return None

# --- UI Helpers ---
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
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(CAPTION)
    
    font_s = pygame.font.Font(None, 24)
    font_m = pygame.font.Font(None, 32)
    
    game_board = initialize_board(board_size)
    current_player, game_over, game_mode = 1, False, 'hvh' 
    dual_view, win_path, is_fullscreen = True, [], False
    
    # --- Layout Tuning (Tighter Horizontal Spacing) ---
    # Moved the origins closer together (480px apart instead of 540px)
    left_origin = (120, 220)
    right_origin = (540, 220) 

    sidebar_x = 1010
    btn_w, btn_h = 175, 45
    modes = {
        'hvh': {'text': 'Human vs Human', 'rect': pygame.Rect(sidebar_x, 50, btn_w, btn_h)},
        'hva': {'text': 'Human vs AI', 'rect': pygame.Rect(sidebar_x, 105, btn_w, btn_h)},
        'ava': {'text': 'AI vs AI', 'rect': pygame.Rect(sidebar_x, 160, btn_w, btn_h)},
        'dual': {'text': 'Toggle Dual Graph', 'rect': pygame.Rect(sidebar_x, 250, btn_w, btn_h)},
        'full': {'text': 'Toggle Fullscreen', 'rect': pygame.Rect(sidebar_x, 305, btn_w, btn_h)},
        'reset': {'text': 'Reset Board', 'rect': pygame.Rect(sidebar_x, 450, btn_w, btn_h)}
    }

    running = True
    while running:
        current_is_ai = not game_over and ((game_mode == 'ava') or (game_mode == 'hva' and current_player == 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if modes['hvh']['rect'].collidepoint(mx, my):
                    game_mode, game_board, game_over, win_path = 'hvh', initialize_board(board_size), False, []
                elif modes['hva']['rect'].collidepoint(mx, my):
                    game_mode, game_board, game_over, win_path = 'hva', initialize_board(board_size), False, []
                elif modes['ava']['rect'].collidepoint(mx, my):
                    game_mode, game_board, game_over, win_path = 'ava', initialize_board(board_size), False, []
                elif modes['dual']['rect'].collidepoint(mx, my):
                    dual_view = not dual_view
                elif modes['full']['rect'].collidepoint(mx, my):
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen: screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else: screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                elif modes['reset']['rect'].collidepoint(mx, my):
                    game_board, game_over, win_path = initialize_board(board_size), False, []

                elif not game_over and not current_is_ai:
                    for r in range(board_size):
                        for c in range(board_size):
                            cx, cy = _get_relative_hex_center(r, c, HEX_RADIUS)
                            px, py = cx + left_origin[0], cy + left_origin[1]
                            if math.sqrt((mx - px)**2 + (my - py)**2) < HEX_RADIUS:
                                if game_board[r][c] == 0:
                                    game_board[r][c] = current_player
                                    win_path = find_winning_path(game_board, current_player) or []
                                    if win_path: game_over = True
                                    else: current_player = 3 - current_player

        if current_is_ai:
            pygame.time.delay(400)
            avail = [(r, c) for r in range(board_size) for c in range(board_size) if game_board[r][c] == 0]
            if avail:
                r, c = random.choice(avail)
                game_board[r][c] = current_player
                win_path = find_winning_path(game_board, current_player) or []
                if win_path: game_over = True
                else: current_player = 3 - current_player

        screen.fill(DARK_GRAY)

        # --- Render Board ---
        for r in range(board_size):
            for c in range(board_size):
                cx, cy = _get_relative_hex_center(r, c, HEX_RADIUS)
                px, py = cx + left_origin[0], cy + left_origin[1]
                verts = get_hex_vertices(px, py, HEX_RADIUS)
                
                # Perimeter Highlights
                t = 7
                if r == 0: 
                    pygame.draw.line(screen, RED, verts[4], verts[5], t); pygame.draw.line(screen, RED, verts[3], verts[4], t)
                if r == board_size-1:
                    pygame.draw.line(screen, RED, verts[0], verts[1], t); pygame.draw.line(screen, RED, verts[1], verts[2], t)
                if c == 0:
                    pygame.draw.line(screen, BLUE, verts[1], verts[2], t); pygame.draw.line(screen, BLUE, verts[2], verts[3], t)
                if c == board_size-1:
                    pygame.draw.line(screen, BLUE, verts[4], verts[5], t); pygame.draw.line(screen, BLUE, verts[5], verts[0], t)

                color = RED if game_board[r][c] == 1 else BLUE if game_board[r][c] == 2 else EMPTY_HEX_COLOR
                pygame.draw.polygon(screen, color, verts)
                pygame.draw.polygon(screen, GOLD if (r,c) in win_path else BLACK, verts, 5 if (r,c) in win_path else 1)

        # --- Render Dual Graph ---
        if dual_view:
            for r in range(board_size):
                for c in range(board_size):
                    cx, cy = _get_relative_hex_center(r, c, HEX_RADIUS)
                    px, py = cx + right_origin[0], cy + right_origin[1]
                    for nr, nc in get_neighbors(r, c, board_size):
                        ncx, ncy = _get_relative_hex_center(nr, nc, HEX_RADIUS)
                        pygame.draw.line(screen, GRAPH_EDGE_COLOR, (px, py), (ncx + right_origin[0], ncy + right_origin[1]), 2)
                    
                    node_color = RED if game_board[r][c] == 1 else BLUE if game_board[r][c] == 2 else WHITE
                    pygame.draw.circle(screen, node_color, (int(px), int(py)), 14)
                    if (r,c) in win_path: pygame.draw.circle(screen, GOLD, (int(px), int(py)), 17, 4)

        # UI Text and Buttons
        title = f"WINNER: Player {3-current_player}" if game_over else f"Player {current_player}'s Turn ({game_mode.upper()})"
        screen.blit(font_m.render(title, True, GOLD if game_over else WHITE), (50, 40))
        if dual_view: screen.blit(font_s.render("COMBINATORIAL DUAL GRAPH", True, WHITE), (right_origin[0], 100))

        for k, v in modes.items():
            b_color = (60, 60, 60) if k != 'reset' else (150, 30, 30)
            pygame.draw.rect(screen, b_color, v['rect'], border_radius=4)
            screen.blit(font_s.render(v['text'], True, WHITE), font_s.render(v['text'], True, WHITE).get_rect(center=v['rect'].center))

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__": play_gui_game(BOARD_SIZE)