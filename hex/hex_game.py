import pygame
import math
import random
import sys

# --- Constants & Colors ---
BOARD_SIZE = 5 
WINDOW_WIDTH = 1200  
WINDOW_HEIGHT = 750 
HEX_RADIUS = 42
RED, BLUE, WHITE, GOLD = (220, 20, 60), (30, 144, 255), (255, 255, 255), (255, 215, 0)
DARK_GRAY, BLACK, EMPTY_COLOR = (25, 25, 25), (0, 0, 0), (140, 140, 140)

# --- Logic Functions ---
def initialize_board(size): 
    return [[0]*size for _ in range(size)]

def get_neighbors(r, c, size):
    res = []
    for dr, dc in [(0,-1), (0,1), (-1,0), (1,0), (-1,1), (1,-1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < size and 0 <= nc < size: res.append((nr, nc))
    return res

def find_winning_path(board, player_id):
    size = len(board)
    visited = set()
    def dfs(r, c, path):
        if (r, c) in visited or board[r][c] != player_id: return None
        visited.add((r, c))
        new_path = path + [(r, c)]
        if player_id == 1 and r == size - 1: return new_path
        if player_id == 2 and c == size - 1: return new_path
        for nr, nc in get_neighbors(r, c, size):
            res = dfs(nr, nc, new_path)
            if res: return res
        return None
    if player_id == 1:
        for c in range(size):
            if board[0][c] == 1:
                res = dfs(0, c, [])
                if res: return res
    else:
        for r in range(size):
            if board[r][0] == 2:
                res = dfs(r, 0, [])
                if res: return res
    return None

def find_sperner_triangles(board):
    size = len(board)
    sperner_tris = []
    for r in range(size - 1):
        for c in range(size - 1):
            t1 = [(r, c), (r, c+1), (r+1, c)]
            if {board[p[0]][p[1]] for p in t1} == {0, 1, 2}: sperner_tris.append(t1)
            t2 = [(r+1, c), (r+1, c+1), (r, c+1)]
            if {board[p[0]][p[1]] for p in t2} == {0, 1, 2}: sperner_tris.append(t2)
    return sperner_tris

def _get_relative_hex_center(row, col, rad):
    x = col * (rad * math.sqrt(3)) + (row * (rad * math.sqrt(3)) / 2)
    y = row * rad * 1.5
    return x, y

def get_hex_vertices(cx, cy, rad):
    return [(int(cx + rad * math.cos(math.pi/180*(30+60*i))),
             int(cy + rad * math.sin(math.pi/180*(30+60*i)))) for i in range(6)]

def play_gui_game(size):
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Hex & Brouwer: Topology Lab (MAT 436)")
    
    font_s = pygame.font.Font(None, 24)
    font_m = pygame.font.Font(None, 32)
    
    game_board = initialize_board(size)
    history = [initialize_board(size)]
    history_index = 0
    
    current_player, game_over, game_mode = 1, False, 'hvh'
    sandbox_brush = 1 
    show_sperner, show_vectors, is_fullscreen = False, False, False
    
    left_origin, right_origin = (120, 200), (540, 200)
    sidebar_x = 1010
    btn_w, btn_h = 175, 45

    btns = {
        'hvh': {'text': 'Human vs Human', 'rect': pygame.Rect(sidebar_x, 30, btn_w, btn_h)},
        'hva': {'text': 'Human vs AI', 'rect': pygame.Rect(sidebar_x, 80, btn_w, btn_h)},
        'ava': {'text': 'AI vs AI', 'rect': pygame.Rect(sidebar_x, 130, btn_w, btn_h)},
        'random': {'text': 'Sandbox Mode', 'rect': pygame.Rect(sidebar_x, 180, btn_w, btn_h)},
        'brush_red': {'text': 'Red', 'rect': pygame.Rect(sidebar_x, 230, 55, btn_h)},
        'brush_blue': {'text': 'Blue', 'rect': pygame.Rect(sidebar_x + 60, 230, 55, btn_h)},
        'brush_clear': {'text': 'Clear', 'rect': pygame.Rect(sidebar_x + 120, 230, 55, btn_h)},
        'sperner': {'text': 'Toggle Sperner', 'rect': pygame.Rect(sidebar_x, 330, btn_w, btn_h)},
        'vector': {'text': 'Toggle Vectors', 'rect': pygame.Rect(sidebar_x, 380, btn_w, btn_h)},
        'fullscreen': {'text': 'Toggle Fullscreen', 'rect': pygame.Rect(sidebar_x, 430, btn_w, btn_h)},
        'reset': {'text': 'Reset Board', 'rect': pygame.Rect(sidebar_x, 530, btn_w, btn_h)},
        'prev': {'text': '< Prev Step', 'rect': pygame.Rect(350, 680, 150, 40)},
        'next': {'text': 'Next Step >', 'rect': pygame.Rect(520, 680, 150, 40)}
    }

    running = True
    while running:
        # Determine if it's the AI's turn
        is_ai_turn = not game_over and history_index == len(history) - 1 and \
                     ((game_mode == 'ava') or (game_mode == 'hva' and current_player == 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    is_fullscreen = not is_fullscreen
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN if is_fullscreen else 0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if btns['fullscreen']['rect'].collidepoint(mx, my):
                    is_fullscreen = not is_fullscreen
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN if is_fullscreen else 0)
                elif btns['hvh']['rect'].collidepoint(mx, my): 
                    game_mode, game_board, history, history_index, game_over = 'hvh', initialize_board(size), [initialize_board(size)], 0, False
                elif btns['hva']['rect'].collidepoint(mx, my): 
                    game_mode, game_board, history, history_index, game_over = 'hva', initialize_board(size), [initialize_board(size)], 0, False
                elif btns['ava']['rect'].collidepoint(mx, my): 
                    game_mode, game_board, history, history_index, game_over = 'ava', initialize_board(size), [initialize_board(size)], 0, False
                elif btns['random']['rect'].collidepoint(mx, my):
                    game_mode = 'random'
                    game_board = [[random.choice([0, 1, 2]) for _ in range(size)] for _ in range(size)]
                    history.append([row[:] for row in game_board]); history_index = len(history)-1
                    game_over = False
                elif btns['brush_red']['rect'].collidepoint(mx, my): sandbox_brush = 1
                elif btns['brush_blue']['rect'].collidepoint(mx, my): sandbox_brush = 2
                elif btns['brush_clear']['rect'].collidepoint(mx, my): sandbox_brush = 0
                elif btns['sperner']['rect'].collidepoint(mx, my): show_sperner = not show_sperner
                elif btns['vector']['rect'].collidepoint(mx, my): show_vectors = not show_vectors
                elif btns['reset']['rect'].collidepoint(mx, my):
                    game_board, history, history_index, game_over, current_player = initialize_board(size), [initialize_board(size)], 0, False, 1
                elif btns['prev']['rect'].collidepoint(mx, my) and history_index > 0: history_index -= 1
                elif btns['next']['rect'].collidepoint(mx, my) and history_index < len(history) - 1: history_index += 1
                
                # Manual Clicks
                elif not game_over and history_index == len(history) - 1 and not is_ai_turn:
                    for r in range(size):
                        for c in range(size):
                            cx, cy = _get_relative_hex_center(r, c, HEX_RADIUS)
                            px, py = cx + left_origin[0], cy + left_origin[1]
                            if math.sqrt((mx-px)**2 + (my-py)**2) < HEX_RADIUS:
                                if game_mode == 'random':
                                    game_board[r][c] = sandbox_brush
                                elif game_board[r][c] == 0:
                                    game_board[r][c] = current_player
                                    current_player = 3 - current_player
                                history.append([row[:] for row in game_board])
                                history_index += 1
                                if find_winning_path(game_board, 1) or find_winning_path(game_board, 2): game_over = True

        # AI Move Logic
        if is_ai_turn:
            pygame.time.delay(500)
            avail = [(r, c) for r in range(size) for c in range(size) if game_board[r][c] == 0]
            if avail:
                r, c = random.choice(avail)
                game_board[r][c] = current_player
                history.append([row[:] for row in game_board])
                history_index += 1
                if find_winning_path(game_board, current_player): game_over = True
                else: current_player = 3 - current_player

        screen.fill(DARK_GRAY)
        display_board = history[history_index]
        s_triangles = find_sperner_triangles(display_board)
        win_path = find_winning_path(display_board, 1) or find_winning_path(display_board, 2) or []

        # --- Draw Boards ---
        for r in range(size):
            for c in range(size):
                cx, cy = _get_relative_hex_center(r, c, HEX_RADIUS)
                lx, ly, rx, ry = cx + left_origin[0], cy + left_origin[1], cx + right_origin[0], cy + right_origin[1]
                v_l = get_hex_vertices(lx, ly, HEX_RADIUS)
                
                # Borders
                t = 7
                if r == 0: pygame.draw.line(screen, RED, v_l[4], v_l[5], t); pygame.draw.line(screen, RED, v_l[3], v_l[4], t)
                if r == size-1: pygame.draw.line(screen, RED, v_l[0], v_l[1], t); pygame.draw.line(screen, RED, v_l[1], v_l[2], t)
                if c == 0: pygame.draw.line(screen, BLUE, v_l[1], v_l[2], t); pygame.draw.line(screen, BLUE, v_l[2], v_l[3], t)
                if c == size-1: pygame.draw.line(screen, BLUE, v_l[4], v_l[5], t); pygame.draw.line(screen, BLUE, v_l[5], v_l[0], t)

                # Hexes
                color = RED if display_board[r][c]==1 else BLUE if display_board[r][c]==2 else EMPTY_COLOR
                pygame.draw.polygon(screen, color, v_l)
                pygame.draw.polygon(screen, GOLD if (r,c) in win_path else BLACK, v_l, 4 if (r,c) in win_path else 1)

                # Dual Graph / Vectors
                for nr, nc in get_neighbors(r, c, size):
                    ncx, ncy = _get_relative_hex_center(nr, nc, HEX_RADIUS)
                    pygame.draw.line(screen, (70, 70, 70), (rx, ry), (ncx+right_origin[0], ncy+right_origin[1]), 1)
                
                if show_vectors:
                    dirs = {1: (0, -1), 2: (1, 0.5), 0: (-1, 0.5)}
                    vx, vy = dirs[display_board[r][c]]
                    pygame.draw.line(screen, GOLD, (rx, ry), (rx + vx*22, ry + vy*22), 2)
                
                node_c = RED if display_board[r][c]==1 else BLUE if display_board[r][c]==2 else WHITE
                pygame.draw.circle(screen, node_c, (int(rx), int(ry)), 12)

        if show_sperner:
            for tri in s_triangles:
                avg_x = sum(_get_relative_hex_center(tr, tc, HEX_RADIUS)[0] for tr, tc in tri) / 3
                avg_y = sum(_get_relative_hex_center(tr, tc, HEX_RADIUS)[1] for tr, tc in tri) / 3
                pygame.draw.circle(screen, GOLD, (int(avg_x + right_origin[0]), int(avg_y + right_origin[1])), 10)
                pygame.draw.circle(screen, WHITE, (int(avg_x + right_origin[0]), int(avg_y + right_origin[1])), 14, 2)

        # UI & Buttons
        status = f"MODE: {game_mode.upper()} | STEP: {history_index}"
        screen.blit(font_m.render(status, True, WHITE), (50, 40))
        for k, v in btns.items():
            active = (k == game_mode) or (k == 'sperner' and show_sperner) or (k == 'vector' and show_vectors) or \
                     (k == 'brush_red' and sandbox_brush == 1 and game_mode == 'random') or \
                     (k == 'brush_blue' and sandbox_brush == 2 and game_mode == 'random') or \
                     (k == 'brush_clear' and sandbox_brush == 0 and game_mode == 'random') or (k == 'fullscreen' and is_fullscreen)
            
            b_color = (120, 120, 120) if active else (60, 60, 60)
            if k == 'reset': b_color = (180, 0, 0)
            pygame.draw.rect(screen, b_color, v['rect'], border_radius=5)
            if active: pygame.draw.rect(screen, GOLD, v['rect'], width=3, border_radius=5)
            screen.blit(font_s.render(v['text'], True, WHITE), font_s.render(v['text'], True, WHITE).get_rect(center=v['rect'].center))

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    play_gui_game(BOARD_SIZE)