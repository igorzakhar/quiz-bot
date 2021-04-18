import os
import json

import redis
from dotenv import load_dotenv


def read_quiz_files(directory='quiz-questions', file_encoding='KOI8-R'):
    for file in os.listdir(os.path.abspath(directory)):
        with open(f'{directory}/{file}', 'r', encoding=file_encoding) as file:
            text = file.read()
            yield text


def upload_questions_into_redis(redis_conn, hash_name='questions'):
    for text in read_quiz_files():
        counter = redis_conn.hlen(hash_name)

        sections_text = text.split('\n\n')

        for section in sections_text:
            if section.strip().startswith('Вопрос'):
                question = ' '.join(section.strip().splitlines()[1:])
                continue

            if section.strip().startswith('Ответ'):
                answer = ' '.join(section.strip().splitlines()[1:])
                counter += 1
                redis_conn.hset(
                    hash_name,
                    f'question_{counter}',
                    json.dumps({'question': question, 'answer': answer})
                )


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

    upload_questions_into_redis(redis_conn)


if __name__ == '__main__':
    main()
