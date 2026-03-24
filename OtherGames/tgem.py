import tkinter as tk
import random
import time

# --- ToroidalTicTacToe Class ---
class ToroidalTicTacToe:
    def __init__(self, board_size=3):
        self.board_size = board_size
        self.board = [[' ' for _ in range(board_size)] for _ in range(board_size)]
        
        # Scoring Constants
        self.SCORE_WIN = 1000
        self.SCORE_LOSE = -1000
        self.SCORE_DRAW = 0

    def _get_toroidal_coord(self, coord):
        return coord % self.board_size

    def get_empty_cells(self):
        return [(r, c) for r in range(self.board_size) for c in range(self.board_size) if self.board[r][c] == ' ']

    def make_move(self, row, col, player):
        if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == ' ':
            self.board[row][col] = player
            return True
        return False

    def check_win(self, player):
        win_length = self.board_size
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] == player:
                    for dr, dc in directions:
                        count = 0
                        for i in range(win_length):
                            tr = self._get_toroidal_coord(r + i * dr)
                            tc = self._get_toroidal_coord(c + i * dc)
                            if self.board[tr][tc] == player:
                                count += 1
                            else:
                                break
                        if count == win_length:
                            return True
        return False

    def check_draw(self):
        return all(cell != ' ' for row in self.board for cell in row)

    def _evaluate_heuristic(self, player_symbol):
        """
        Simple heuristic for non-terminal states.
        Counts how many 2-in-a-row or 3-in-a-row chains exist.
        """
        opponent = 'O' if player_symbol == 'X' else 'X'
        if self.check_win(player_symbol): return self.SCORE_WIN
        if self.check_win(opponent): return self.SCORE_LOSE
        return 0

    def minimax(self, depth, is_maximizing, p_sym, o_sym, alpha, beta, max_depth):
        # 1. Check for terminal states
        if self.check_win(p_sym): return self.SCORE_WIN - depth
        if self.check_win(o_sym): return self.SCORE_LOSE + depth
        if self.check_draw(): return self.SCORE_DRAW
        
        # 2. Depth limit to prevent hanging on 4x4
        if depth >= max_depth:
            return self._evaluate_heuristic(p_sym)

        if is_maximizing:
            max_eval = -float('inf')
            for r, c in self.get_empty_cells():
                self.board[r][c] = p_sym
                eval = self.minimax(depth + 1, False, p_sym, o_sym, alpha, beta, max_depth)
                self.board[r][c] = ' '
                max_eval = max(max_eval, eval)
                alpha = max(alpha, max_eval)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = float('inf')
            for r, c in self.get_empty_cells():
                self.board[r][c] = o_sym
                eval = self.minimax(depth + 1, True, p_sym, o_sym, alpha, beta, max_depth)
                self.board[r][c] = ' '
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval)
                if beta <= alpha: break
            return min_eval

    def get_ai_move(self, ai_symbol):
        cells = self.get_empty_cells()
        if not cells: return None
        
        # Search Depth Settings: 3x3 is solved, 4x4 is limited to 4-5 moves for speed
        limit = 4 if self.board_size == 4 else 9
        
        best_score = -float('inf')
        best_move = cells[0]
        opp = 'O' if ai_symbol == 'X' else 'X'
        
        # Shuffle moves to make AI play differently each game
        random.shuffle(cells)

        for r, c in cells:
            self.board[r][c] = ai_symbol
            score = self.minimax(0, False, ai_symbol, opp, -float('inf'), float('inf'), limit)
            self.board[r][c] = ' '
            if score > best_score:
                best_score = score
                best_move = (r, c)
        return best_move

    def display_board(self):
        for r_idx, row in enumerate(self.board):
            print(" | ".join(row))
            if r_idx < self.board_size - 1:
                print("-" * (self.board_size * 4 - 1))

# --- ToroidalTicTacToeApp (GUI) ---
class ToroidalTicTacToeApp:
    def __init__(self, master):
        self.master = master
        master.title('Toroidal Tic-Tac-Toe')
        self.game_mode = tk.StringVar(value="HvAI")
        self.board_size_var = tk.IntVar(value=3)
        self.buttons = []
        self.game_instance = None
        self.current_player = 'X'
        self.game_over = False

        # UI Elements
        tk.Label(master, text="Toroidal Tic-Tac-Toe", font=('Arial', 16, 'bold')).pack(pady=5)
        
        ctl_frame = tk.Frame(master)
        ctl_frame.pack()
        tk.Radiobutton(ctl_frame, text="H vs H", variable=self.game_mode, value="HvH").grid(row=0, column=0)
        tk.Radiobutton(ctl_frame, text="H vs AI", variable=self.game_mode, value="HvAI").grid(row=0, column=1)
        tk.Radiobutton(ctl_frame, text="AI vs AI", variable=self.game_mode, value="AIvAI").grid(row=0, column=2)

        size_frame = tk.Frame(master)
        size_frame.pack()
        tk.Radiobutton(size_frame, text="3x3", variable=self.board_size_var, value=3, command=self.reset_game).pack(side=tk.LEFT)
        tk.Radiobutton(size_frame, text="4x4", variable=self.board_size_var, value=4, command=self.reset_game).pack(side=tk.LEFT)

        self.board_frame = tk.Frame(master)
        self.board_frame.pack(pady=10)
        
        self.status_label = tk.Label(master, text="", font=('Arial', 12))
        self.status_label.pack()

        tk.Button(master, text="Reset / Start", command=self.reset_game).pack(pady=5)
        self.reset_game()

    def reset_game(self):
        for widget in self.board_frame.winfo_children(): widget.destroy()
        self.size = self.board_size_var.get()
        self.game_instance = ToroidalTicTacToe(self.size)
        self.buttons = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = 'X'
        self.game_over = False
        
        for r in range(self.size):
            for c in range(self.size):
                btn = tk.Button(self.board_frame, text='', font=('Arial', 20), width=4, height=2,
                               command=lambda r=r, c=c: self.handle_click(r, c))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[r][c] = btn
        
        self.status_label.config(text=f"Turn: {self.current_player}")
        if self.game_mode.get() == "AIvAI" or (self.game_mode.get() == "HvAI" and self.current_player == 'O'):
            self.master.after(500, self.ai_move)

    def handle_click(self, r, c):
        if self.game_over or self.game_instance.board[r][c] != ' ': return
        if self.game_mode.get() == "AIvAI": return

        self.execute_move(r, c)
        if not self.game_over and self.game_mode.get() == "HvAI":
            self.master.after(500, self.ai_move)

    def execute_move(self, r, c):
        if self.game_instance.make_move(r, c, self.current_player):
            self.buttons[r][c].config(text=self.current_player)
            if self.game_instance.check_win(self.current_player):
                self.status_label.config(text=f"Player {self.current_player} Wins!")
                self.game_over = True
            elif self.game_instance.check_draw():
                self.status_label.config(text="Draw!")
                self.game_over = True
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                self.status_label.config(text=f"Turn: {self.current_player}")

    def ai_move(self):
        if self.game_over: return
        move = self.game_instance.get_ai_move(self.current_player)
        if move:
            self.execute_move(move[0], move[1])
        if not self.game_over and self.game_mode.get() == "AIvAI":
            self.master.after(500, self.ai_move)

# --- Terminal Version (Fallback) ---
def play_terminal(size):
    game = ToroidalTicTacToe(size)
    player = 'X'
    while True:
        game.display_board()
        print(f"Player {player}'s turn.")
        r, c = map(int, input("Enter row col (e.g. 0 1): ").split())
        if game.make_move(r, c, player):
            if game.check_win(player):
                game.display_board()
                print(f"Player {player} wins!")
                break
            player = 'O' if player == 'X' else 'X'

if __name__ == "__main__":
    choice = input("gui or term? ").lower()
    if choice == 'gui':
        root = tk.Tk()
        app = ToroidalTicTacToeApp(root)
        root.mainloop()
    else:
        play_terminal(3)