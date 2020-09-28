import functools
import logging
import os
import random
import re

import redis
import telegram
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from load_questions import load_questions


logger = logging.getLogger(__name__)


def remove_comments(answer):
    return re.sub("[\(\[].*?[\)\]]", "", answer).strip()


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


def ask_question(bot, update, questions, redis_conn):
    if update.message.text == 'Новый вопрос':
        question = random.choice(list(questions.keys()))
        user_id = update.message.from_user.id

        update.message.reply_text(question)
        redis_conn.set(user_id, question)

        logger.debug(
            f'user_id: {user_id}. '
            f'Question: {question} '
            f'Answer: {questions.get(question)}'
        )

    else:
        current_question = redis_conn.get(update.message.from_user.id)
        answer = questions.get(current_question.decode("utf-8"))

        user_response = update.message.text.lower()
        correct_answer = remove_comments(answer).lower().strip('.')

        logger.debug(
            f'User response: {user_response} '
            f'Correct answer: {correct_answer}'
        )

        if user_response == correct_answer:
            update.message.reply_text(
                'Правильно! Поздравляю! '
                'Для следующего вопроса нажми «Новый вопрос».'
            )
        else:
            update.message.reply_text('Неправильно. Попробуешь ещё раз?')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    load_dotenv()
    questions = load_questions()

    tg_token = os.getenv('TELEGRAM_TOKEN')
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    redis_password = os.getenv('REDIS_PASSWORD')

    redis_conn = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        db=0
    )

    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(tg_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    ask_question_handler = functools.partial(
        ask_question,
        questions=questions,
        redis_conn=redis_conn
    )
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
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    main()
