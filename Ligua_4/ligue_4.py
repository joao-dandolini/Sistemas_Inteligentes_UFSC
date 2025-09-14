from typing import List, Tuple, Optional
import math
import random

ROWS, COLS = 6, 7
EMPTY = 0
BOT = 1
OPP = 2

# ---------- Utilidades de tabuleiro ----------
def new_board() -> List[List[int]]:
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def copy_board(board: List[List[int]]) -> List[List[int]]:
    return [row[:] for row in board]

def valid_moves(board: List[List[int]]) -> List[int]:
    return [c for c in range(COLS) if board[0][c] == EMPTY]

def drop_piece(board: List[List[int]], col: int, player: int) -> Optional[List[List[int]]]:
    if board[0][col] != EMPTY:
        return None
    b = copy_board(board)
    for r in range(ROWS - 1, -1, -1):
        if b[r][col] == EMPTY:
            b[r][col] = player
            return b
    return None

def is_winning(board: List[List[int]], player: int) -> bool:
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c+i] == player for i in range(4)):
                return True
    # Vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r+i][c] == player for i in range(4)):
                return True
    # Diag /
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r-i][c+i] == player for i in range(4)):
                return True
    # Diag \
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r+i][c+i] == player for i in range(4)):
                return True
    return False

def is_playable_cell(board: List[List[int]], r: int, c: int) -> bool:
    """Uma célula vazia é 'jogável' se estiver vazia e (linha inferior ou tem peça abaixo)."""
    if board[r][c] != EMPTY:
        return False
    return (r == ROWS - 1) or (board[r + 1][c] != EMPTY)

# ---------- Heurística ----------
class Weights:
    CENTER = 2.0
    TWO_OPEN = 5.0          # 2 em 4 com 2 vazios (aberto)
    THREE_OPEN = 50.0       # 3 em 4 com 1 vazio (ameaça forte)
    BROKEN_THREE = 60.0     # 1-1-0-1 (ou permutações) com 0 jogável
    TWO_SPACE_TWO = 80.0    # [1,1,0,1,1] horizontal (0 jogável)
    WIN = 1e6
    LOSE = -1e6

    #CENTER = 1e-6
    #TWO_OPEN = 0.019
    #THREE_OPEN = 0.16
    #BROKEN_THREE = 0.16
    #TWO_SPACE_TWO = 0.16
    #WIN = 1
    #LOSE = -1

def count_center_bonus(board: List[List[int]], player: int) -> float:
    center_col = COLS // 2
    count = sum(1 for r in range(ROWS) if board[r][center_col] == player)
    return count * Weights.CENTER

def eval_window_4(window: List[int], player: int) -> float:
    """Pontua uma janela de comprimento 4 (horizontal/vertical/diagonal)."""
    opp = OPP if player == BOT else BOT
    score = 0.0
    p_cnt = window.count(player)
    o_cnt = window.count(opp)
    e_cnt = window.count(EMPTY)

    # Reforço (terminais serão cortados no minimax)
    if p_cnt == 4:
        score += Weights.WIN
    elif o_cnt == 4:
        score += Weights.LOSE

    # Trincas e duplas abertas
    if p_cnt == 3 and e_cnt == 1 and o_cnt == 0:
        score += Weights.THREE_OPEN
    if p_cnt == 2 and e_cnt == 2 and o_cnt == 0:
        score += Weights.TWO_OPEN

    # Penalização simétrica
    if o_cnt == 3 and e_cnt == 1 and p_cnt == 0:
        score -= Weights.THREE_OPEN
    if o_cnt == 2 and e_cnt == 2 and p_cnt == 0:
        score -= Weights.TWO_OPEN

    return score

def broken_three_in_window(board: List[List[int]], coords: List[Tuple[int,int]], player: int) -> float:
    """coords: lista de 4 (r,c). Verifica 1-1-0-1 (e variações) com vazio jogável."""
    opp = OPP if player == BOT else BOT
    vals = [board[r][c] for (r,c) in coords]
    score = 0.0

    if opp in vals:
        return 0.0
    if vals.count(player) == 3 and vals.count(EMPTY) == 1:
        idx = vals.index(EMPTY)
        r, c = coords[idx]
        if is_playable_cell(board, r, c):
            score += Weights.BROKEN_THREE

    # Simétrico para o oponente
    if vals.count(opp) == 3 and vals.count(EMPTY) == 1:
        idx = vals.index(EMPTY)
        r, c = coords[idx]
        if is_playable_cell(board, r, c):
            score -= Weights.BROKEN_THREE
    return score

def two_space_two_horizontal(board: List[List[int]], r: int, c_start: int, player: int) -> float:
    """Detecta [p,p,_,p,p] horizontal em (r, c_start..c_start+4), com '_' jogável."""
    opp = OPP if player == BOT else BOT
    if c_start + 4 >= COLS:
        return 0.0
    window = [board[r][c_start+i] for i in range(5)]
    if opp in window:
        return 0.0
    if window.count(player) == 4 and window.count(EMPTY) == 1:
        idx = window.index(EMPTY)
        c = c_start + idx
        if is_playable_cell(board, r, c):
            return Weights.TWO_SPACE_TWO
    if window.count(opp) == 4 and window.count(EMPTY) == 1:
        idx = window.index(EMPTY)
        c = c_start + idx
        if is_playable_cell(board, r, c):
            return -Weights.TWO_SPACE_TWO
    return 0.0

def evaluate(board: List[List[int]], player: int) -> float:
    """Heurística estática do ponto de vista de `player`."""
    opp = OPP if player == BOT else BOT

    # Terminais
    if is_winning(board, player):
        return Weights.WIN
    if is_winning(board, opp):
        return Weights.LOSE

    score = 0.0
    score += count_center_bonus(board, player)

    # Horizontal (janelas 4) + broken-three + 2-esp-2
    for r in range(ROWS):
        for c in range(COLS - 3):
            coords = [(r, c+i) for i in range(4)]
            window = [board[r][c+i] for i in range(4)]
            score += eval_window_4(window, player)
            score += broken_three_in_window(board, coords, player)
        for c in range(COLS - 4):
            score += two_space_two_horizontal(board, r, c, player)

    # Vertical (janelas 4) + broken-three
    for c in range(COLS):
        for r in range(ROWS - 3):
            coords = [(r+i, c) for i in range(4)]
            window = [board[r+i][c] for i in range(4)]
            score += eval_window_4(window, player)
            score += broken_three_in_window(board, coords, player)

    # Diagonais / e \
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            coords = [(r-i, c+i) for i in range(4)]
            window = [board[r-i][c+i] for i in range(4)]
            score += eval_window_4(window, player)
            score += broken_three_in_window(board, coords, player)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            coords = [(r+i, c+i) for i in range(4)]
            window = [board[r+i][c+i] for i in range(4)]
            score += eval_window_4(window, player)
            score += broken_three_in_window(board, coords, player)

    return score

# ---------- Minimax com poda e ordenação ----------
def order_moves(board: List[List[int]], moves: List[int], player: int) -> List[int]:
    center = COLS // 2
    return sorted(moves, key=lambda c: abs(c - center))

def minimax(board: List[List[int]], depth: int, alpha: float, beta: float, maximizing: bool, pov_player: int) -> Tuple[float, Optional[int]]:
    opp = OPP if pov_player == BOT else BOT

    # Parada
    if depth == 0 or is_winning(board, pov_player) or is_winning(board, opp) or not valid_moves(board):
        return evaluate(board, pov_player), None

    moves = order_moves(board, valid_moves(board), pov_player if maximizing else opp)

    best_move = None
    if maximizing:
        value = -math.inf
        for c in moves:
            child = drop_piece(board, c, pov_player)
            if child is None:
                continue
            child_val, _ = minimax(child, depth - 1, alpha, beta, False, pov_player)
            if child_val > value:
                value, best_move = child_val, c
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value, best_move
    else:
        value = math.inf
        for c in moves:
            child = drop_piece(board, c, opp)
            if child is None:
                continue
            child_val, _ = minimax(child, depth - 1, alpha, beta, True, pov_player)
            if child_val < value:
                value, best_move = child_val, c
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value, best_move

def choose_move(board: List[List[int]], player: int = BOT, depth: int = 5) -> Tuple[int, float]:
    value, move = minimax(board, depth, -math.inf, math.inf, True, player)
    if move is None:
        vm = valid_moves(board)
        return (random.choice(vm) if vm else -1), value
    return move, value

# ---------- Visualização e loop de jogo ----------
def print_board(board: List[List[int]]) -> None:
    symbols = {EMPTY: ".", BOT: "X", OPP: "O"}
    print("\n 0 1 2 3 4 5 6")
    for r in range(ROWS):
        print(" " + " ".join(symbols[board[r][c]] for c in range(COLS)))
    print()

def play(depth: int = 5, human_plays_as: int = OPP) -> None:
    """
    human_plays_as: OPP (padrão, 'O') ou BOT ('X') caso queira começar.
    depth: profundidade do minimax do bot.
    """
    board = new_board()
    print_board(board)

    human = human_plays_as
    bot = BOT if human == OPP else OPP
    turn = BOT  # Começa pelo BOT por padrão; ajuste aqui se quiser o humano começar
    if human == BOT:
        turn = BOT  # humano começa
    else:
        turn = OPP  # humano começa se ele for OPP

    while True:
        if turn == human:
            vm = valid_moves(board)
            if not vm:
                print("Empate!")
                break
            move = None
            while move not in vm:
                try:
                    move = int(input(f"Sua vez ({'X' if human==BOT else 'O'})! Colunas válidas {vm}: "))
                except ValueError:
                    move = None
            next_board = drop_piece(board, move, human)
            if next_board is None:
                print("Coluna inválida. Tente novamente.")
                continue
            board = next_board
            if is_winning(board, human):
                print_board(board)
                print("Você venceu!")
                break
        else:
            vm = valid_moves(board)
            if not vm:
                print("Empate!")
                break
            col, val = choose_move(board, player=bot, depth=depth)
            board = drop_piece(board, col, bot)
            print(f"Bot ({'X' if bot==BOT else 'O'}) jogou na coluna {col} (valor={val:.1f})")
            if is_winning(board, bot):
                print_board(board)
                print("Bot venceu!")
                break

        print_board(board)
        if not valid_moves(board):
            print("Empate!")
            break
        turn = BOT if turn == OPP else OPP

# ---------- Execução direta ----------
if __name__ == "__main__":
    # Opções rápidas:
    # 1) Humano começa como OPP (O) e bot com profundidade 5
    play(depth=2, human_plays_as=OPP)

    # 2) Se quiser começar como BOT (X), use:
    # play(depth=5, human_plays_as=BOT)
