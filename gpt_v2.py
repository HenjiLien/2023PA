import numpy as np
import random
black = '⚫️'
white = '⚪️'
# 建立棋盤
def create_board():
    board = [['0' for col in range(8)] for row in range(8)]
    board[3][3] = board[4][4] = black
    board[3][4] = board[4][3] = white
    return board

# 檢查是否為合法的移動
def is_valid_move(board, row, col, player):
    if board[row][col] != '0':
        return False
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if r < 0 or r >= 8 or c < 0 or c >= 8:
                continue
            if board[r][c] != player:
                while True:
                    r += dr
                    c += dc
                    if r < 0 or r >= 8 or c < 0 or c >= 8:
                        break
                    if board[r][c] == '0':
                        break
                    if board[r][c] == player:
                        return True
    return False

# 執行移動
def execute_move(board, row, col, player):
    board[row][col] = player
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if r < 0 or r >= 8 or c < 0 or c >= 8:
                continue
            if board[r][c] != player:
                positions_to_flip = [(r, c)]
                while True:
                    r += dr
                    c += dc
                    if r < 0 or r >= 8 or c < 0 or c >= 8:
                        break
                    if board[r][c] == '0':
                        break
                    if board[r][c] == player:
                        print(positions_to_flip)
                        for fr, fc in positions_to_flip:
                            board[fr][fc] = player
                        break
                    positions_to_flip.append((r, c))

# AI下棋
def ai_move(board, player):
    valid_moves = [(row, col) for row in range(8) for col in range(8) if board[row][col] == '0']
    random.shuffle(valid_moves)
    for move in valid_moves:
        row, col = move
        if is_valid_move(board, row, col, player) == True:
            return row, col

# 檢查遊戲是否結束
def is_game_over(board):
    return sum(board[row][col] == '0' for row in range(8) for col in range(8))

# 統計棋盤上黑子和白子的數量
def count_pieces(board):
    black_pieces = sum(board[row][col] == black for row in range(8) for col in range(8))
    white_pieces = sum(board[row][col] == white for row in range(8) for col in range(8))
    return black_pieces, white_pieces

# 顯示棋盤
def print_board(board):
    for r in range(8):
        for c in range(8):
            if board[r][c] == '0':
                print('  ', end="")
            else:
                print(board[r][c], end="")
        print()
# 主程式
def main():
    board = create_board()
    player = black  # 玩家使用黑子
    game_over = False

    while not game_over:
        print_board(board)

        if player == black:
            print("輪到玩家下棋")
            valid_move = False
            while not valid_move:
                move = input("請輸入下棋的位置（例如 A1）：")
                col = ord(move[0].upper()) - ord('A')
                row = int(move[1:]) - 1
                valid_move = is_valid_move(board, row, col, player)
                if not valid_move:
                    print("無效的移動，請重試")
            execute_move(board, row, col, player)
        else:
            print("輪到AI下棋")
            row, col = ai_move(board, player)
            execute_move(board, row, col, player)

        print(is_game_over(board))
        if is_game_over(board) == 0:
            game_over = True

        # 切換玩家
        if player == black:
            player = white
        else:
            player = black

    print_board(board)
    black_pieces, white_pieces = count_pieces(board)
    print("遊戲結束")
    if black_pieces > white_pieces:
        print("玩家獲勝")
    elif black_pieces < white_pieces:
        print("AI獲勝")
    else:
        print("平局")

if __name__ == "__main__":
    main()
