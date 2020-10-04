import os


def extract_questions(text):
    questions = {}

    for contents in text:
        if 'Вопрос' in contents:
            question = ' '.join(contents.strip().splitlines()[1:])
            continue
        elif 'Ответ' in contents:
            answer = ' '.join(contents.strip().splitlines()[1:])
            questions[question] = answer

    return questions


def load_questions(directory='quiz-questions'):
    all_questions = {}

    for file in os.listdir(os.path.abspath(directory)):
        with open(f'{directory}/{file}', 'r', encoding='KOI8-R') as file:
            text = file.read().split('\n\n')

        questions = extract_questions(text)
        all_questions.update(questions)

    return all_questions
