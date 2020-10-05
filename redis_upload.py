import os
import json

import redis
from dotenv import load_dotenv


def upload_questions_into_redis(text, redis_conn, hash_name='questions'):
    counter = redis_conn.hlen(hash_name)

    for contents in text:
        if contents.strip().startswith('Вопрос'):
            question = ' '.join(contents.strip().splitlines()[1:])
            continue

        if contents.strip().startswith('Ответ'):
            answer = ' '.join(contents.strip().splitlines()[1:])
            counter += 1
            redis_conn.hset(
                hash_name,
                f'question_{counter}',
                json.dumps({'question': question, 'answer': answer})
            )


def read_files(directory='quiz-questions'):
    for file in os.listdir(os.path.abspath(directory)):
        with open(f'{directory}/{file}', 'r', encoding='KOI8-R') as file:
            text = file.read().split('\n\n')
            yield text


def upload_questions(redis_conn):
    for text in read_files():
        upload_questions_into_redis(text, redis_conn)


def main():
    load_dotenv()

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

    upload_questions(redis_conn)


if __name__ == '__main__':
    main()