import functools
import logging
import os
import random

import telegram
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from load_questions import load_questions


logger = logging.getLogger(__name__)


def start(bot, update):
    """Send a message when the command /start is issued."""
    keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Привет! Я бот для проведения викторины.',
        reply_markup=reply_markup
    )


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def ask_question(bot, update, questions):
    if update.message.text == 'Новый вопрос':
        question = random.choice(list(questions.keys()))
        update.message.reply_text(question)

    else:
        update.message.reply_text(update.message.text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    load_dotenv()

    questions = load_questions()

    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    tg_token = os.getenv('TELEGRAM_TOKEN')
    updater = Updater(tg_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    ask_question_handler = functools.partial(ask_question, questions=questions)
    dp.add_handler(MessageHandler(Filters.text, ask_question_handler))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    main()
