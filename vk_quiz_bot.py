import json
import logging
import os
import random
import sys

import redis
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from answer_tools import remove_comments, get_answer_question


logger = logging.getLogger(__name__)


def get_custom_keyboard():
    keyboard = VkKeyboard()

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    return keyboard.get_keyboard()


def handle_new_question(event, vk, redis_conn):
    question_num = random.choice(redis_conn.hkeys('questions'))
    redis_conn.hset(
        'users',
        f'user_vk_{event.user_id}',
        json.dumps({'last_asked_question': question_num})
    )

    qa = json.loads(redis_conn.hget('questions', question_num))
    question = qa.get('question')

    vk.messages.send(
        peer_id=event.user_id,
        random_id=get_random_id(),
        keyboard=get_custom_keyboard(),
        message=question
    )


def handle_solution_attempt(event, vk, redis_conn):
    answer = get_answer_question(event.user_id, redis_conn, source='vk')

    user_response = event.text
    correct_answer = remove_comments(answer).lower().strip('.')

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


def handle_give_up(event, vk, redis_conn):
    answer = get_answer_question(event.user_id, redis_conn, source='vk')

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


def run_chatbot(token):
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
                handle_new_question(event, api_vk, redis_conn)
            elif event.text == 'Сдаться':
                handle_give_up(event, api_vk, redis_conn)
            else:
                handle_solution_attempt(event, api_vk, redis_conn)


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    vk_token = os.getenv('VK_TOKEN')

    while True:
        try:
            run_chatbot(vk_token)

        except Exception as err:
            logger.error(f'Бот "{__file__}" упал с ошибкой.')
            logger.exception(err)

            continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
