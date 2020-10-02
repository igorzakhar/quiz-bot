import logging
import os
import random
import re
import sys

import redis
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from load_questions import load_questions


logger = logging.getLogger(__name__)


def remove_comments(answer):
    return re.sub("[\(\[].*?[\)\]]", "", answer).strip()


def get_custom_keyboard():
    keyboard = VkKeyboard()

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    return keyboard.get_keyboard()


def handle_new_question(event, vk, questions, redis_conn):
    question = random.choice(list(questions.keys()))

    redis_conn.set(event.user_id, question)

    logger.debug(
        f'user_id: {event.user_id}. '
        f'Question: {question} '
        f'Answer: {questions.get(question)}'
    )

    vk.messages.send(
        peer_id=event.user_id,
        random_id=get_random_id(),
        keyboard=get_custom_keyboard(),
        message=question
    )


def handle_solution_attempt(event, vk, questions, redis_conn):
    current_question = redis_conn.get(event.user_id)
    answer = questions.get(current_question)
    user_response = event.text
    correct_answer = remove_comments(answer).lower().strip('.')

    logger.debug(
        f'User response: {user_response} '
        f'Correct answer: {correct_answer}'
    )

    if user_response.lower() == correct_answer:
        message = (
            'Правильно! Поздравляю! '
            'Для следующего вопроса нажми «Новый вопрос».'
        )
        vk.messages.send(
            peer_id=event.user_id,
            random_id=get_random_id(),
            keyboard=get_custom_keyboard(),
            message=message
        )

    else:
        vk.messages.send(
            peer_id=event.user_id,
            random_id=get_random_id(),
            keyboard=get_custom_keyboard(),
            message='Неправильно. Попробуешь ещё раз?'
        )


def handle_give_up(event, vk, questions, redis_conn):
    current_question = redis_conn.get(event.user_id)
    answer = questions.get(current_question)
    response = (
        f'Вот тебе правильный ответ: {answer} '
        'Чтобы продолжить нажми «Новый вопрос»'
    )

    vk.messages.send(
        peer_id=event.user_id,
        random_id=get_random_id(),
        keyboard=get_custom_keyboard(),
        message=response
    )


def run_chatbot(token, questions):
    vk_session = vk_api.VkApi(token=token)
    api_vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

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

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                handle_new_question(event, api_vk, questions, redis_conn)
            elif event.text == 'Сдаться':
                handle_give_up(event, api_vk, questions, redis_conn)
            else:
                handle_solution_attempt(event, api_vk, questions, redis_conn)


def main():
    questions = load_questions()
    vk_token = os.getenv('VK_TOKEN')

    while True:
        try:
            run_chatbot(vk_token, questions)

        except Exception as err:
            logger.error(f'Бот "{__file__}" упал с ошибкой.')
            logger.exception(err)

            continue


if __name__ == "__main__":
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
