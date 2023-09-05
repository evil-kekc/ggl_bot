import json
from typing import NamedTuple

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from bot_app.keyboard.keyboard_generator import create_keyboard
from db.db_engine import Session, Results
from main import RegistrationStates


class Question(NamedTuple):
    """Question representation"""
    number: int
    text: str
    answers: list


async def cmd_start(message: types.Message, state: FSMContext):
    """Handler processing start command

    :param message: message object
    :param state: state object
    :return:
    """
    user_id = message.from_user.id
    username = message.from_user.username

    session = Session()
    user = session.query(Results).filter_by(user_id=user_id).first()
    if user is None:
        new_user = Results(user_id=user_id, username=username)
        session.add(new_user)
        session.commit()
    else:
        await message.answer('Извините, Вы уже прошли тестирование')
        return

    await message.answer("Добро пожаловать! Введите Ваше имя")
    await state.set_state(RegistrationStates.get_name)


async def start_survey(message: types.Message, state: FSMContext):
    """Test start

    :param message: message object
    :return:
    """
    user_id = message.from_user.id
    session = Session()
    user = session.query(Results).filter_by(user_id=user_id).first()

    if message.text == '14-15 лет':
        user.age_category = '14-15 лет'
        session.commit()
        await state.update_data(current_question=1)
    elif message.text == '16-17 лет':
        user.age_category = '14-15 лет'
        session.commit()
        await state.update_data(current_question=1)
    else:
        await message.answer('Выберите один из предложенных вариантов')
        return

    with open('bot_app/questions/14_15_questions.json', 'r') as file:
        json_data = json.load(file)

    questions = json_data.get('questions')
    state_data = await state.get_data()
    current_question_number = state_data.get('current_question')

    question_data = None

    for question in questions:
        if question.get('number') == current_question_number:
            question_data = Question(
                number=question.get('number'),
                text=question.get('text'),
                answers=question.get('answers')
            )
            break

    keyboard = create_keyboard()
    for answer in question_data.answers:
        keyboard.add(answer['text'])

    await message.answer(question_data.text, reply_markup=keyboard)

    await state.update_data(answer=question_data.answers, number=question_data.number)
    await state.set_state(RegistrationStates.survey_question)


async def survey_question(message: types.Message, state: FSMContext):
    """Question Handling

    :param message: message object
    :param state: state object
    :return:
    """
    data = await state.get_data()
    answer = data.get('answer')
    number = data.get('number')
    print(answer, number)

    await state.set_state(RegistrationStates.start_survey)


def register_handlers_common(dp: Dispatcher):
    """User Registration Handlers

    :param dp: Dispatcher object
    :return:
    """
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(start_survey, state=RegistrationStates.start_survey)
    dp.register_message_handler(survey_question, state=RegistrationStates.survey_question)
