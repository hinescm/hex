import tkinter as tk
import random
import time # For AI delay

# --- ToroidalTicTacToe Class ---
class ToroidalTicTacToe:
    def __init__(self, board_size=3):
        self.board_size = board_size
        self.board = self._initialize_board()

    def _initialize_board(self):
        """
        Initializes a Tic-Tac-Toe board of a given size, filled with empty spaces.
        (Private method, called by __init__)
        """
        board = []
        for _ in range(self.board_size):
            board.append([' '] * self.board_size)
        return board

    def _get_toroidal_coord(self, coord):
        """
        Returns the toroidal coordinate for a given coordinate and board size.
        (Private helper method)
        """
        return coord % self.board_size

    def get_empty_cells(self):
        """
        Returns a list of all empty cells (row, col) on the board.
        """
        empty_cells = []
        for r_idx, row in enumerate(self.board):
            for c_idx, cell in enumerate(row):
                if cell == ' ':
                    empty_cells.append((r_idx, c_idx))
        return empty_cells

    def make_move(self, row, col, player):
        """
        Allows a player to make a move on the Tic-Tac-Toe board.

        Args:
            row (int): The row coordinate for the move.
            col (int): The column coordinate for the move.
            player (str): The symbol of the current player ('X' or 'O').

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        # 1. Validate coordinates are within bounds
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return False

        # 2. Check if the cell is empty
        if self.board[row][col] != ' ':
            return False

        # If both conditions are met, make the move
        self.board[row][col] = player
        return True

    def check_win(self, player):
        """
        Checks for a win condition (dynamic length in a row, column, or diagonal) on a toroidal board.

        Args:
            player (str): The symbol of the current player ('X' or 'O').

        Returns:
            bool: True if the player has won, False otherwise.
        """
        # The win condition length should be equal to board_size for the game to be N-in-a-row
        win_length = self.board_size

        # Iterate through each cell on the board
        for r in range(self.board_size):
            for c in range(self.board_size):
                # Only check if the current cell contains the player's symbol
                if self.board[r][c] == player:
                    # Directions to check: horizontal, vertical, and two diagonals
                    primary_directions = [
                        (0, 1),   # Horizontal right
                        (1, 0),   # Vertical down
                        (1, 1),   # Diagonal down-right
                        (1, -1)   # Diagonal down-left
                    ]

                    for dr, dc in primary_directions:
                        count = 0
                        for i in range(win_length):
                            tr, tc = self._get_toroidal_coord(r + i * dr), self._get_toroidal_coord(c + i * dc)
                            if self.board[tr][tc] == player:
                                count += 1
                            else:
                                break
                        if count == win_length:
                            return True
        return False

    def check_draw(self):
        """
        Checks if the game has ended in a draw (all cells filled, no winner assumed).

        Returns:
            bool: True if the board is full, False otherwise.
        """
        for row in self.board:
            for cell in row:
                if cell == ' ':
                    return False  # Found an empty cell, so it's not a draw yet
        return True  # No empty cells found, board is full

    # --- Minimax implementation additions ---
    SCORE_WIN = 10
    SCORE_LOSE = -10
    SCORE_DRAW = 0

    def _evaluate_board(self, player_symbol, opponent_symbol):
        """
        Evaluates the current board state to determine if it's a win, loss, or draw.

        Args:
            player_symbol (str): The symbol of the current AI player.
            opponent_symbol (str): The symbol of the opponent player.

        Returns:
            int: SCORE_WIN if player_symbol wins, SCORE_LOSE if opponent_symbol wins,
                 SCORE_DRAW if it's a draw, or None if the game is still ongoing.
        """
        if self.check_win(player_symbol):
            return self.SCORE_WIN
        if self.check_win(opponent_symbol):
            return self.SCORE_LOSE
        if self.check_draw():
            return self.SCORE_DRAW
        return None  # Game is still ongoing

    def minimax(self, depth, is_maximizing_player, player_symbol, opponent_symbol, alpha, beta):
        """
        Recursive Minimax function with Alpha-Beta Pruning to find the optimal move.

        Args:
            depth (int): Current depth in the game tree.
            is_maximizing_player (bool): True if the current turn is for the maximizing player (AI).
            player_symbol (str): The symbol of the AI player (maximizing).
            opponent_symbol (str): The symbol of the opponent player (minimizing).
            alpha (int): The best value found so far for the maximizing player.
            beta (int): The best value found so far for the minimizing player.

        Returns:
            int: The optimal score for the current board state.
        """
        score = self._evaluate_board(player_symbol, opponent_symbol)

        # Terminal node: game is won, lost, or drawn
        if score is not None:
            # Adjust score based on depth: deeper wins are less preferred, deeper losses are more preferred (less bad)
            if score == self.SCORE_WIN:
                return score - depth
            elif score == self.SCORE_LOSE:
                return score + depth
            return score

        # Non-terminal node: game is ongoing
        if is_maximizing_player:
            max_eval = -float('inf')
            for r, c in self.get_empty_cells():
                self.board[r][c] = player_symbol  # Make a temporary move
                eval = self.minimax(depth + 1, False, player_symbol, opponent_symbol, alpha, beta)
                self.board[r][c] = ' '  # Undo the move
                max_eval = max(max_eval, eval)
                alpha = max(alpha, max_eval) # Update alpha
                if alpha >= beta: # Alpha-Beta Pruning
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for r, c in self.get_empty_cells():
                self.board[r][c] = opponent_symbol  # Make a temporary move
                eval = self.minimax(depth + 1, True, player_symbol, opponent_symbol, alpha, beta)
                self.board[r][c] = ' '  # Undo the move
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval) # Update beta
                if alpha >= beta: # Alpha-Beta Pruning
                    break
            return min_eval

    def get_ai_move(self, ai_player_symbol):
        """
        Determines the AI's move using the Minimax algorithm with Alpha-Beta Pruning.

        Args:
            ai_player_symbol (str): The symbol of the AI player ('X' or 'O').

        Returns:
            tuple: A tuple (row, col) representing the AI's chosen optimal move, or None if no empty cells.
        """
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return None

        best_score = -float('inf')
        best_move = None

        opponent_symbol = 'O' if ai_player_symbol == 'X' else 'X'

        # Initialize alpha and beta for the initial call
        alpha = -float('inf')
        beta = float('inf')

        # Iterate through all possible moves and evaluate them using minimax
        for r, c in empty_cells:
            # Temporarily make the move
            self.board[r][c] = ai_player_symbol

            # Call minimax for the opponent's turn (is_maximizing_player=False)
            # The score returned is from the perspective of the current AI player.
            score = self.minimax(0, False, ai_player_symbol, opponent_symbol, alpha, beta)

            # Undo the move
            self.board[r][c] = ' '

            if score > best_score:
                best_score = score
                best_move = (r, c)
            alpha = max(alpha, best_score) # Update alpha for the root node's children

        return best_move

    def display_board(self):
        """
        Displays the current state of the Tic-Tac-Toe board in a readable format.
        """
        board_size = self.board_size
        for r_idx, row in enumerate(self.board):
            print(" | ".join([cell if cell != ' ' else ' ' for cell in row]))
            if r_idx < board_size - 1:
                print("-" * (board_size * 4 - 3))


def play_terminal_game(board_size=3):
    """
    Handles the game flow for Toroidal Tic-Tac-Toe using terminal I/O.
    """
    game_instance = ToroidalTicTacToe(board_size=board_size)
    current_player = 'X'
    game_over = False
    game_mode_str = ""

    print("\n--- Welcome to Terminal Toroidal Tic-Tac-Toe! ---")
    print(f"Board Size: {board_size}x{board_size}")

    # Game Mode selection
    while game_mode_str not in ["1", "2", "3"]:
        try:
            game_mode_str = input("Select game mode: (1) Human vs Human, (2) Human vs AI, (3) AI vs AI: ").strip()
            if game_mode_str not in ["1", "2", "3"]:
                print("Invalid game mode. Please choose 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Quitting game. Goodbye!")
            return # Exit the function

    if game_mode_str == "1":
        player_x_type = "human"
        player_o_type = "human"
    elif game_mode_str == "2":
        player_x_type = "human"
        player_o_type = "ai"
    elif game_mode_str == "3":
        player_x_type = "ai"
        player_o_type = "ai"
    
    print(f"\nGame Mode: {player_x_type.capitalize()} (X) vs {player_o_type.capitalize()} (O)")

    try:
        while not game_over:
            print(f"\n{'='*15}\nPlayer '{current_player}'s turn.\n{'='*15}")
            game_instance.display_board()

            move_successful = False
            while not move_successful:
                row, col = -1, -1 # Initialize with invalid values

                is_ai_player = (current_player == 'X' and player_x_type == 'ai') or \
                               (current_player == 'O' and player_o_type == 'ai')

                if is_ai_player:
                    print(f"AI ({current_player}) is thinking...")
                    time.sleep(1) # Delay for AI move
                    ai_move = game_instance.get_ai_move(current_player)
                    if ai_move:
                        row, col = ai_move
                        print(f"AI ({current_player}) chooses: ({row}, {col})")
                    else:
                        # This case implies a draw before AI can find a move, unlikely with Minimax unless full.
                        print("AI could not find a valid move. This shouldn't happen before a draw.")
                        game_over = True # End game if AI gets stuck
                        break
                else: # Human player
                    row_input = input(f"Player '{current_player}', enter row (0-{board_size-1}) (or 'q' to quit): ")
                    if row_input.lower() == 'q':
                        print("Quitting game. Goodbye!")
                        return # Exit the function
                    row = int(row_input)
                    col_input = input(f"Player '{current_player}', enter column (0-{board_size-1}) (or 'q' to quit): ")
                    if col_input.lower() == 'q':
                        print("Quitting game. Goodbye!")
                        return # Exit the function
                    col = int(col_input)

                if game_instance.make_move(row, col, current_player):
                    move_successful = True
                else:
                    if not is_ai_player: # Only print error for human players trying invalid moves
                        print("Invalid move. Cell is either out of bounds or already occupied. Try again.")

            if game_over: # Break out of outer loop if AI got stuck
                break

            # Check for win
            if game_instance.check_win(current_player):
                print(f"\n!!! Player '{current_player}' wins! Congratulations !!!")
                game_over = True
            # Check for draw
            elif game_instance.check_draw():
                print("\n!!! It's a DRAW! Good game! !!!")
                game_over = True
            else:
                # Switch player for the next turn
                current_player = 'O' if current_player == 'X' else 'X'

                # If in AI vs AI mode, ensure the next AI turn is processed without waiting for human input
                if (player_x_type == 'ai' and player_o_type == 'ai') or \
                   (current_player == 'O' and player_o_type == 'ai') or \
                   (current_player == 'X' and player_x_type == 'ai'):
                    continue # The loop will re-run and next AI will move after a delay
    except ValueError:
        print("Invalid input. Please enter numbers for row and column.")
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Quitting game. Goodbye!")
        return # Exit the function

    print("\n--- Game Over ---")
    game_instance.display_board()


# --- ToroidalTicTacToeApp Class ---
class ToroidalTicTacToeApp:
    def __init__(self, master):
        self.master = master
        master.title('Toroidal Tic-Tac-Toe')

        self.game_instance = None # Initialize to None, set in reset_game
        self.buttons = [] # To store the Tkinter button objects

        self.current_player = 'X'
        self.game_over = False
        self.game_mode = tk.StringVar(value="HvH") # "HvH", "HvAI", "AIvAI"
        self.board_size_var = tk.IntVar(value=3) # Variable to hold selected board size

        # --- Basic layout setup ---
        self.label = tk.Label(master, text="Welcome to Toroidal Tic-Tac-Toe!", font=('Arial', 14))
        self.label.pack(pady=10)

        # Game Mode selection
        mode_frame = tk.Frame(master)
        mode_frame.pack(pady=5)
        tk.Radiobutton(mode_frame, text="Human vs Human", variable=self.game_mode, value="HvH", command=self.reset_game).pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="Human vs AI", variable=self.game_mode, value="HvAI", command=self.reset_game).pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="AI vs AI", variable=self.game_mode, value="AIvAI", command=self.reset_game).pack(side=tk.LEFT)

        # Board Size selection
        size_frame = tk.Frame(master)
        size_frame.pack(pady=5)
        tk.Label(size_frame, text="Board Size:").pack(side=tk.LEFT)
        tk.Radiobutton(size_frame, text="3x3", variable=self.board_size_var, value=3, command=self.reset_game).pack(side=tk.LEFT)
        tk.Radiobutton(size_frame, text="4x4", variable=self.board_size_var, value=4, command=self.reset_game).pack(side=tk.LEFT)

        self.board_frame = tk.Frame(master, borderwidth=2, relief="groove")
        self.board_frame.pack(pady=10)

        self.status_label = tk.Label(master, text=f"Player {self.current_player}'s turn", font=('Arial', 12))
        self.status_label.pack(pady=10)

        self.reset_button = tk.Button(master, text="Reset Game", command=self.reset_game, font=('Arial', 12))
        self.reset_button.pack(pady=5)

        self.reset_game() # Call reset to initialize the board and game state

    def handle_click(self, row, col):
        if self.game_over:
            return # Do nothing if game is over

        if self.game_mode.get() == "AIvAI":
            return # Human clicks don't register in AI vs AI mode

        # Attempt to make a move
        if self.game_instance.make_move(row, col, self.current_player):
            self.update_board_display()
            self._check_game_state()
            self._check_for_ai_turn() # Check if AI needs to move next
        else:
            # Invalid move (e.g., cell already occupied)
            self.status_label.config(text="Invalid move. Try again.", fg="red")
            self.master.after(1500, lambda: self.status_label.config(text=f"Player {self.current_player}'s turn", fg="black"))

    def ai_turn(self):
        if self.game_over:
            return

        self._disable_all_buttons()
        self.status_label.config(text=f"AI ({self.current_player}) is thinking...", fg="blue")
        self.master.update_idletasks() # Update GUI immediately

        ai_move = self.game_instance.get_ai_move(self.current_player)
        if ai_move:
            row, col = ai_move
            if self.game_instance.make_move(row, col, self.current_player):
                self.update_board_display()
                self._check_game_state()

        if not self.game_over:
            self._enable_all_buttons() # Re-enable for next human player or disable again for next AI
            # Schedule next AI turn if in AI vs AI mode or if it's AI's turn in HvAI
            if (self.game_mode.get() == "AIvAI") or \
               (self.game_mode.get() == "HvAI" and self.current_player == 'O'):
                self.master.after(1000, self.ai_turn) # AI moves after a delay


    def _check_game_state(self):
        # Check for win
        if self.game_instance.check_win(self.current_player):
            self.status_label.config(text=f"Player {self.current_player} wins! Congratulations!")
            self.game_over = True
            self._disable_all_buttons()
        # Check for draw
        elif self.game_instance.check_draw():
            self.status_label.config(text="It's a DRAW! Good game!")
            self.game_over = True
            self._disable_all_buttons()
        # Game continues, switch player
        else:
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            # Only update status_label if not in AI vs AI mode to avoid 'Player X's turn' message
            if self.game_mode.get() != "AIvAI":
                self.status_label.config(text=f"Player {self.current_player}'s turn")

    def _check_for_ai_turn(self):
        current_mode = self.game_mode.get()
        if not self.game_over:
            if current_mode == "AIvAI":
                self._disable_all_buttons() # Disable buttons as no human input is needed
                self.master.after(1000, self.ai_turn)
            elif current_mode == "HvAI" and self.current_player == 'O':
                self._disable_all_buttons() # Disable buttons during AI turn
                self.master.after(1000, self.ai_turn)
            else:
                self._enable_all_buttons() # Re-enable buttons for human player (HvH or HvAI for 'X')

    def update_board_display(self):
        """
        Updates the text of the GUI buttons to reflect the current state of the game board.
        """
        # Clear existing buttons from the board_frame if there are any changes in size, otherwise just update
        if not self.buttons or len(self.buttons) != self.game_instance.board_size:
            for widget in self.board_frame.winfo_children():
                widget.destroy()
            self.buttons = []
            for r in range(self.game_instance.board_size):
                row_buttons = []
                for c in range(self.game_instance.board_size):
                    button = tk.Button(self.board_frame,
                                       text='',
                                       font=('Arial', 24, 'bold'),
                                       width=4,
                                       height=2,
                                       command=lambda r=r, c=c: self.handle_click(r, c))
                    button.grid(row=r, column=c, padx=5, pady=5)
                    row_buttons.append(button)
                self.buttons.append(row_buttons)

        for r in range(self.game_instance.board_size):
            for c in range(self.game_instance.board_size):
                player_symbol = self.game_instance.board[r][c]
                self.buttons[r][c].config(text=player_symbol)

    def _disable_all_buttons(self):
        for r in range(self.game_instance.board_size):
            for c in range(self.game_instance.board_size):
                self.buttons[r][c].config(state=tk.DISABLED)

    def _enable_all_buttons(self):
        current_mode = self.game_mode.get()
        if current_mode == "AIvAI" or self.game_over:
            self._disable_all_buttons()
            return

        for r in range(self.game_instance.board_size):
            for c in range(self.game_instance.board_size):
                if self.game_instance.board[r][c] == ' ': 
                    # Buttons are enabled only for human players in relevant modes
                    if current_mode == "HvH" or (current_mode == "HvAI" and self.current_player == 'X'):
                        self.buttons[r][c].config(state=tk.NORMAL)
                    else:
                        self.buttons[r][c].config(state=tk.DISABLED)
                else:
                    self.buttons[r][c].config(state=tk.DISABLED)

    def reset_game(self):
        # Clear existing buttons from the board_frame
        for row_buttons in self.buttons:
            for button in row_buttons:
                button.destroy()
        self.buttons = []

        self.game_instance = ToroidalTicTacToe(board_size=self.board_size_var.get())
        self.current_player = 'X'
        self.game_over = False

        # Recreate the board buttons for the new size
        for r in range(self.game_instance.board_size):
            row_buttons = []
            for c in range(self.game_instance.board_size):
                button = tk.Button(self.board_frame,
                                   text='',
                                   font=('Arial', 24, 'bold'),
                                   width=4,
                                   height=2,
                                   command=lambda r=r, c=c: self.handle_click(r, c))
                button.grid(row=r, column=c, padx=5, pady=5)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

        self.update_board_display()
        self.status_label.config(text=f"Player {self.current_player}'s turn", fg="black")
        self._enable_all_buttons()
        self._check_for_ai_turn()

# --- Main execution block ---

def get_user_board_size():
    valid_size = False
    board_size_choice = 3 # Default
    while not valid_size:
        try:
            size_input = input("Enter board size (3 or 4): ").strip()
            board_size_choice = int(size_input)
            if board_size_choice in [3, 4]:
                valid_size = True
            else:
                print("Invalid board size. Please enter 3 or 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Exiting.")
            return None # Indicate user wants to quit
    return board_size_choice


if __name__ == "__main__":
    game_version_choice = None
    while game_version_choice not in ['gui', 'term']:
        try:
            game_version_choice = input("Do you want to play the GUI or Terminal version? (gui/term): ").strip().lower()
            if game_version_choice not in ['gui', 'term']:
                print("Invalid choice. Please enter 'gui' or 'term'.")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Exiting.")
            game_version_choice = None # Indicate user wants to quit
            break

    if game_version_choice == 'gui':
        try:
            # Create the main application window
            root = tk.Tk()

            # Instantiate the GUI application
            app = ToroidalTicTacToeApp(root)

            # Start the Tkinter event loop
            root.mainloop()
        except tk.TclError as e:
            print(f"\nTkinter Error: {e}")
            print("Tkinter GUI applications cannot be run directly in this environment (e.g., Google Colab) ")
            print("because it lacks a graphical display server.")

            # Offer terminal version as fallback
            play_terminal_fallback = input("Do you want to play the terminal version instead? (y/n): ").strip().lower()
            if play_terminal_fallback == 'y' or play_terminal_fallback == 'yes':
                board_size_choice = get_user_board_size()
                if board_size_choice is not None:
                    play_terminal_game(board_size=board_size_choice)
            else:
                print("Exiting game. Goodbye!")
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Exiting GUI launch. Goodbye!")

    elif game_version_choice == 'term':
        board_size_choice = get_user_board_size()
        if board_size_choice is not None:
            play_terminal_game(board_size=board_size_choice)
    else:
        # This handles the case where the user quit during the initial prompt
        print("Exiting game. Goodbye!")