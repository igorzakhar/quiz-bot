import re
import json


def remove_comments(answer):
    return re.sub(r"[\(\[].*?[\)\]]", "", answer).strip()


def get_answer_question(user_id, redis_conn, source='tg'):
    user_redis_value = json.loads(
        redis_conn.hget('users', f'user_{source}_{user_id}')
    )

    qa = json.loads(
        redis_conn.hget(
            'questions',
            user_redis_value.get('last_asked_question')
        )
    )

    answer = qa.get('answer')

    return answer
