import re


def remove_comments(answer):
    return re.sub(r"[\(\[].*?[\)\]]", "", answer).strip()
