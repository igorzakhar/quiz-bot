import functools
import json
import logging
import os
import random
import textwrap

import redis
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    RegexHandler,
    Filters,
    ConversationHandler
)

from answer_tools import remove_comments, get_answer_question


logger = logging.getLogger(__name__)

CHOOSING, ATTEMPT = range(2)


def start(bot, update):
    """Send a message when the command /start is issued."""
    keyboard = [['Новый вопрос', 'Сдаться']]
    kb_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    start_message = textwrap.dedent(
        '''\
        Приветствую! Нажмите «Новый вопрос» для начала викторины.
        /cancel - для отмены.
        '''
    )
    update.message.reply_text(start_message, reply_markup=kb_markup)

    return CHOOSING


def handle_new_question_request(bot, update, redis_conn):
    question_num = random.choice(redis_conn.hkeys('questions'))
    redis_conn.hset(
        'users',
        f'user_tg_{update.message.from_user.id}',
        json.dumps({'last_asked_question': question_num})
    )

    qa = json.loads(redis_conn.hget('questions', question_num))
    question = qa.get('question')

    logger.debug(
        f'question: {question} '
        f'answer: {qa.get("answer")}'
    )

    update.message.reply_text(question)

    return ATTEMPT


def handle_solution_attempt(bot, update, redis_conn):
    user_id = update.message.from_user.id
    answer = get_answer_question(user_id, redis_conn)
    user_response = update.message.text
    correct_answer = remove_comments(answer).lower().strip('.')

    logger.debug(
        f'user_response: {user_response.lower()} '
        f'correct_answer: {correct_answer} '
    )

    if user_response.lower() == correct_answer:
        update.message.reply_text(
            'Правильно! Поздравляю! '
            'Для следующего вопроса нажми «Новый вопрос».'
        )
        return CHOOSING
    else:
        update.message.reply_text('Неправильно. Попробуешь ещё раз?')

        return ATTEMPT


def handle_give_up(bot, update, redis_conn):
    user_id = update.message.from_user.id
    answer = get_answer_question(user_id, redis_conn)
    update.message.reply_text(
        f'Вот тебе правильный ответ: {answer} '
        'Чтобы продолжить нажми «Новый вопрос»'
    )

    return CHOOSING


def cancel(bot, update):
    update.message.reply_text(
        f'До свидания, {update.message.from_user.first_name}!',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def run_chatbot(token):
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')
    redis_password = os.getenv('REDIS_PASSWORD')

    redis_conn = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        charset='utf-8',
        decode_responses=True
    )

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    handlers_dispatcher = updater.dispatcher

    handle_new_question = functools.partial(
        handle_new_question_request,
        redis_conn=redis_conn
    )

    handle_solution = functools.partial(
        handle_solution_attempt,
        redis_conn=redis_conn
    )

    handle_giveup = functools.partial(
        handle_give_up,
        redis_conn=redis_conn
    )

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler('^Новый вопрос$', handle_new_question)],

            ATTEMPT: [
                RegexHandler('^Сдаться$', handle_giveup),
                MessageHandler(Filters.text, handle_solution)
            ]
        },

        fallbacks=[CommandHandler('cancel', cancel)]

    )

    handlers_dispatcher.add_handler(conversation_handler)

    # log all errors
    handlers_dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


def main():
    logging.getLogger(__name__).setLevel(logging.INFO)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    tg_token = os.getenv('TELEGRAM_TOKEN')

    run_chatbot(tg_token)


if __name__ == '__main__':
    main()
