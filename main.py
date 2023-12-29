import numpy as np
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from henji import TOKEN
import random

black = '⚫️'
white = '⚪️'


def create_board():
    board = [['0' for col in range(8)] for row in range(8)]
    board[3][3] = board[4][4] = black
    board[3][4] = board[4][3] = white
    return board


board = create_board()
player = black
game_over = False


def enc(board):
    # board is a dictionary mapping (row, col) to grid
    # grid = [[board.get((row, col), '') for col in range(8)] for row in range(8)]
    number = 0
    base = 3
    for row in range(8):
        for col in range(8):
            number *= base
            # if grid[row][col] == black:
            if board.get((row, col)) == black:
                number += 2
            # elif grid[row][col] == white:
            elif board.get((row, col)) == white:
                number += 1
    return str(number)


def dec(number):
    board = {}
    base = 3
    for row in [7, 6, 5, 4, 3, 2, 1, 0]:
        for col in [7, 6, 5, 4, 3, 2, 1, 0]:
            if number % 3 == 2:
                board[(row, col)] = black
            elif number % 3 == 1:
                board[(row, col)] = white
            number //= base
    return board


def board_markup(board):
    '''
    # Convert board values to strings
    str_board = np.where(board == 1, black, np.where(board == 2, white, '  '))
    # Create markup with string values
    '''
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(board[row][col], callback_data=f'{row}{col}') for col in range(8)]
        for row in range(8)])


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
            if board[r][c] != player and board[r][c] != '0':
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
            if board[r][c] != player and board[r][c] != '0':
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
        if is_valid_move(board, row, col, player):
            return row, col
    return None


# 檢查遊戲是否結束
def is_game_over(board):
    return sum(board[row][col] == '0' for row in range(8) for col in range(8))


# 統計棋盤上黑子和白子的數量
def count_pieces(board):
    black_pieces = sum(board[row][col] == black for row in range(8) for col in range(8))
    white_pieces = sum(board[row][col] == white for row in range(8) for col in range(8))
    return black_pieces, white_pieces


# Define a few command handlers. These usually take the two arguments update and
# context.
async def func(update, context):
    global board, player, game_over
    if game_over or player == white:
        return

    if not any(is_valid_move(board, r, c, player) for r in range(8) for c in range(8)):
        player = white
        await context.bot.edit_message_text('您無法落子',
                                            reply_markup=board_markup(board),
                                            chat_id=update.callback_query.message.chat_id,
                                            message_id=update.callback_query.message.message_id)
    else:
        data = update.callback_query.data
        # user clicked the button on row int(data[0]) and col int(data[1])
        row = int(data[0])
        col = int(data[1])
        # TODO: check if the button is clickable. if not, report it is not clickable and return

        if not is_valid_move(board, row, col, player):
            await context.bot.answer_callback_query(update.callback_query.id, '這邊不能下')
            return

        await context.bot.answer_callback_query(update.callback_query.id, f'你按的 row {row} col {col}')

        # the board is encoded and stored as data[2:]
        # board = dec(int(data[2:]))
        execute_move(board, row, col, player)
        # 切換玩家
        player = white
    # reply_markup = board_markup(board)
    await context.bot.edit_message_text('等待 AI 下棋',
                                        reply_markup=board_markup(board),
                                        chat_id=update.callback_query.message.chat_id,
                                        message_id=update.callback_query.message.message_id)
    ai_move_result = ai_move(board, player)
    if ai_move_result is None:
        await context.bot.edit_message_text('AI 無法落子',
                                            reply_markup=board_markup(board),
                                            chat_id=update.callback_query.message.chat_id,
                                            message_id=update.callback_query.message.message_id)
    else:
        ai_row, ai_col = ai_move_result
        execute_move(board, ai_row, ai_col, player)

    await context.bot.edit_message_text('換你',
                                        reply_markup=board_markup(board),
                                        chat_id=update.callback_query.message.chat_id,
                                        message_id=update.callback_query.message.message_id)
    player = black

    if is_game_over(board) == 0:
        game_over = True

    if game_over:
        black_pieces, white_pieces = count_pieces(board)
        print("遊戲結束")
        if black_pieces > white_pieces:
            await context.bot.edit_message_text('遊戲結束，你贏了',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
            print("玩家獲勝")
        elif black_pieces < white_pieces:
            print("AI獲勝")
            await context.bot.edit_message_text('遊戲結束，你輸了',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)
        else:
            print("平局")
            await context.bot.edit_message_text('遊戲結束，和局',
                                                reply_markup=board_markup(board),
                                                chat_id=update.callback_query.message.chat_id,
                                                message_id=update.callback_query.message.message_id)


async def start(update, context):
    global board, player, game_over
    board = create_board()
    player = black
    game_over = False
    # board = {(3, 3): '⚫️', (3, 4): '⚪️', (4, 3): '⚪️', (4, 4): '⚫️'}
    # reply_markup = board_markup(board)
    await update.message.reply_text('目前盤面', reply_markup=board_markup(board))


def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("game_start", start))

    application.add_handler(CallbackQueryHandler(func))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
