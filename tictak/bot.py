import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    Filters,
)
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize game state
games = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Welcome to Tic Tac Toe Bot!\n\n'
        'Use /newgame to start a new game.\n'
        'Commands:\n'
        '/newgame - Start a new game\n'
        '/help - Show help message'
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Tic Tac Toe Bot Commands:\n\n'
        '/newgame - Start a new game\n'
        '/help - Show this help message'
    )

def new_game(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id in games:
        update.message.reply_text('A game is already in progress! Finish it before starting a new one.')
        return
    games[chat_id] = {
        'board': [' ' for _ in range(9)],
        'current_player': 'X',
        'players': {}
    }
    send_board(update, context, chat_id)

def send_board(update: Update, context: CallbackContext, chat_id):
    board = games[chat_id]['board']
    buttons = []
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            idx = i + j
            text = board[idx] if board[idx] != ' ' else f'{idx+1}'
            row.append(InlineKeyboardButton(text, callback_data=str(idx)))
        buttons.append(row)
    reply_markup = InlineKeyboardMarkup(buttons)
    if update.callback_query:
        query = update.callback_query
        query.edit_message_text(
            f"Tic Tac Toe\nCurrent Player: {games[chat_id]['current_player']}",
            reply_markup=reply_markup
        )
        query.answer()
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Tic Tac Toe\nCurrent Player: {games[chat_id]['current_player']}",
            reply_markup=reply_markup
        )

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat.id
    data = int(query.data)
    game = games.get(chat_id)

    if not game:
        query.answer("No game in progress. Start a new game with /newgame.")
        return

    board = game['board']
    current_player = game['current_player']

    if board[data] != ' ':
        query.answer("This cell is already taken!")
        return

    board[data] = current_player

    if check_winner(board, current_player):
        send_board(update, context, chat_id)
        context.bot.send_message(chat_id, f"Player {current_player} wins!")
        del games[chat_id]
        return

    if ' ' not in board:
        send_board(update, context, chat_id)
        context.bot.send_message(chat_id, "It's a tie!")
        del games[chat_id]
        return

    # Switch player
    game['current_player'] = 'O' if current_player == 'X' else 'X'
    send_board(update, context, chat_id)

def check_winner(board, player):
    win_conditions = [
        [0, 1, 2],  # Rows
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],  # Columns
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],  # Diagonals
        [2, 4, 6]
    ]
    for condition in win_conditions:
        if all(board[i] == player for i in condition):
            return True
    return False

def main():
    # Get the bot token from environment variable
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables.")
        return

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("newgame", new_game))
    dispatcher.add_handler(CallbackQueryHandler(button, pattern='^\d+$'))

    # Start the Bot
    updater.start_polling()
    logger.info("Bot started successfully.")
    updater.idle()

if __name__ == '__main__':
    main()
