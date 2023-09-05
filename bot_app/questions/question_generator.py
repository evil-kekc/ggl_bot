import json

with open('bot_app/questions/14_15_questions.json', 'r') as file:
    data = json.load(file)

questions = data['questions']

for question_data in questions:
    question_text = question_data['text']
    answers = question_data['answers']

    print(f"Вопрос: {question_text}")

    for answer in answers:
        answer_text = answer['text']
        points = answer['points']

        print(f"Ответ: {answer_text}, Баллы: {points}")
