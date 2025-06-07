import time
import copy
import math

DIRECTIONS = [
    (-1, -1), 
    (-1, 0),  
    (-1, 1),   
    (0, -1),   
    (0, 1),   
    (1, -1),   
    (1, 0),    
    (1, 1)     
]

def in_bounds(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def valid_movements(board, player):
    opponent = -player
    valid_moves = []
    
    for x in range(8):
        for y in range(8):
            if board[x][y] != 0:
                continue
            
            for dx, dy in DIRECTIONS:
                i, j = x + dx, y + dy
                found_opponent = False
                
                while in_bounds(i, j) and board[i][j] == opponent:
                    i += dx
                    j += dy
                    found_opponent = True
                
                if found_opponent and in_bounds(i, j) and board[i][j] == player:
                    valid_moves.append((x, y))
                    break
    
    return valid_moves

POSITION_VALUES = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,  -1,  -1,  -1,  -1,  -2,  10],
    [  5,  -2,  -1,  -1,  -1,  -1,  -2,   5],
    [  5,  -2,  -1,  -1,  -1,  -1,  -2,   5],
    [ 10,  -2,  -1,  -1,  -1,  -1,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100]
]

start_time = None
time_limit = 2.8  

def make_move(board, move, player):
    new_board = copy.deepcopy(board)
    x, y = move
    new_board[x][y] = player
    opponent = -player
    
    for dx, dy in DIRECTIONS:
        pieces_to_flip = []
        i, j = x + dx, y + dy
        
        while in_bounds(i, j) and new_board[i][j] == opponent:
            pieces_to_flip.append((i, j))
            i += dx
            j += dy
        
        if in_bounds(i, j) and new_board[i][j] == player and pieces_to_flip:
            for flip_x, flip_y in pieces_to_flip:
                new_board[flip_x][flip_y] = player
    
    return new_board

def count_pieces(board, player):
    count = 0
    for row in board:
        for cell in row:
            if cell == player:
                count += 1
    return count

def get_corner_control(board, player):
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    player_corners = 0
    opponent_corners = 0
    
    for x, y in corners:
        if board[x][y] == player:
            player_corners += 1
        elif board[x][y] == -player:
            opponent_corners += 1
    
    return player_corners - opponent_corners

def count_stable_pieces(board, player):
    stable_count = 0
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    
    for corner_x, corner_y in corners:
        if board[corner_x][corner_y] == player:
            stable_count += 1
            
            if corner_x == 0 and corner_y == 0:  
                for y in range(1, 8):
                    if board[0][y] == player:
                        stable_count += 1
                    else:
                        break
                for x in range(1, 8):
                    if board[x][0] == player:
                        stable_count += 1
                    else:
                        break
            elif corner_x == 0 and corner_y == 7: 
                for y in range(6, -1, -1):
                    if board[0][y] == player:
                        stable_count += 1
                    else:
                        break
                for x in range(1, 8):
                    if board[x][7] == player:
                        stable_count += 1
                    else:
                        break
    
    return stable_count

def evaluate_board(board, player):
    opponent = -player
    
    player_pieces = count_pieces(board, player)
    opponent_pieces = count_pieces(board, opponent)
    total_pieces = player_pieces + opponent_pieces
    
    position_value = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == player:
                position_value += POSITION_VALUES[x][y]
            elif board[x][y] == opponent:
                position_value -= POSITION_VALUES[x][y]
    
    player_moves = len(valid_movements(board, player))
    opponent_moves = len(valid_movements(board, opponent))
    mobility_diff = player_moves - opponent_moves
    
    corner_diff = get_corner_control(board, player) * 100
    
    player_stable = count_stable_pieces(board, player)
    opponent_stable = count_stable_pieces(board, opponent)
    stability_diff = (player_stable - opponent_stable) * 20
    
    if total_pieces < 20: 
        piece_weight = 0.1
        position_weight = 5.0
        mobility_weight = 2.0
        corner_weight = 10.0
        stability_weight = 3.0
    elif total_pieces < 40: 
        piece_weight = 0.5
        position_weight = 2.0
        mobility_weight = 3.0
        corner_weight = 8.0
        stability_weight = 5.0
    else: 
        piece_weight = 2.0
        position_weight = 1.0
        mobility_weight = 1.0
        corner_weight = 5.0
        stability_weight = 7.0
    
    total_eval = (
        piece_weight * (player_pieces - opponent_pieces) +
        position_weight * position_value +
        mobility_weight * mobility_diff * 10 +
        corner_weight * corner_diff +
        stability_weight * stability_diff
    )
    
    return total_eval

def is_corner(x, y):
    return (x, y) in [(0, 0), (0, 7), (7, 0), (7, 7)]

def is_x_square(x, y, board):
    x_squares = {
        (1, 1): (0, 0),
        (1, 6): (0, 7),
        (6, 1): (7, 0),
        (6, 6): (7, 7)
    }
    
    if (x, y) in x_squares:
        corner_x, corner_y = x_squares[(x, y)]
        return board[corner_x][corner_y] == 0
    
    return False

def order_moves(moves, board):
    move_priorities = []
    
    for move in moves:
        x, y = move
        priority = 0
        
        if is_corner(x, y):
            priority = 1000
        elif is_x_square(x, y, board):
            priority = -100
        elif x == 0 or x == 7 or y == 0 or y == 7:
            priority = 50
        else:
            priority = POSITION_VALUES[x][y]
        
        move_priorities.append((move, priority))
    
    move_priorities.sort(key=lambda x: x[1], reverse=True)
    return [move for move, _ in move_priorities]

def minimax(board, depth, alpha, beta, maximizing_player, player, original_player):
    global start_time
    
    if time.time() - start_time > time_limit:
        return evaluate_board(board, original_player)
    
    if depth == 0:
        return evaluate_board(board, original_player)
    
    valid_moves = valid_movements(board, player)
    
    if not valid_moves:
        opponent_moves = valid_movements(board, -player)
        if not opponent_moves:
            player_pieces = count_pieces(board, original_player)
            opponent_pieces = count_pieces(board, -original_player)
            if player_pieces > opponent_pieces:
                return 10000
            elif player_pieces < opponent_pieces:
                return -10000
            else:
                return 0
        return minimax(board, depth - 1, alpha, beta, not maximizing_player, -player, original_player)
    
    if depth > 2: 
        valid_moves = order_moves(valid_moves, board)
    
    if maximizing_player:
        max_eval = -math.inf
        for move in valid_moves:
            new_board = make_move(board, move, player)
            eval_score = minimax(new_board, depth - 1, alpha, beta, False, -player, original_player)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  
        return max_eval
    else:
        min_eval = math.inf
        for move in valid_moves:
            new_board = make_move(board, move, player)
            eval_score = minimax(new_board, depth - 1, alpha, beta, True, -player, original_player)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  
        return min_eval

def ai_move(board, player):
    global start_time
    start_time = time.time()
    
    valid_moves = valid_movements(board, player)
    
    if not valid_moves:
        return None
    
    if len(valid_moves) == 1:
        return valid_moves[0]
    
    best_move = valid_moves[0]
    best_value = -math.inf
    
    for depth in range(1, 10): 
        if time.time() - start_time > time_limit * 0.7:
            break
        
        current_best_move = None
        current_best_value = -math.inf
        move_values = []
        
        for move in valid_moves:
            if time.time() - start_time > time_limit * 0.9:
                break
            
            new_board = make_move(board, move, player)
            value = minimax(new_board, depth - 1, -math.inf, math.inf, False, -player, player)
            move_values.append((move, value))
            
            if value > current_best_value:
                current_best_value = value
                current_best_move = move
        
        if current_best_move is not None:
            best_move = current_best_move
            best_value = current_best_value
            
            move_values.sort(key=lambda x: x[1], reverse=True)
            valid_moves = [move for move, _ in move_values]
    
    return best_move


def print_board(board):
    print("\n  0 1 2 3 4 5 6 7")
    print("  ----------------")
    for i in range(8):
        print(f"{i}|", end="")
        for j in range(8):
            if board[i][j] == 1:
                print(" ●", end="")
            elif board[i][j] == -1:
                print(" ○", end="")
            else:
                print(" ·", end="")
        print(f"|{i}")
    print("  ----------------")
    print("  0 1 2 3 4 5 6 7")
    
    # Contar fichas
    black = sum(row.count(1) for row in board)
    white = sum(row.count(-1) for row in board)
    print(f"\nNegras (●): {black}  Blancas (○): {white}")

def test_ai():

    board = [[0 for _ in range(8)] for _ in range(8)]
    board[3][3] = -1  
    board[3][4] = 1   
    board[4][3] = 1   
    board[4][4] = -1  
    
    print("Tablero inicial:")
    print_board(board)
    
    print("\nProbando IA con fichas negras (1)...")
    move = ai_move(board, 1)
    if move:
        print(f"IA juega en: {move}")
        board = make_move(board, move, 1)
        print_board(board)
    else:
        print("No hay movimientos válidos")

if __name__ == "__main__":
    test_ai()