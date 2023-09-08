import json
from typing import NamedTuple

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot_app.keyboard.keyboard_generator import create_keyboard, ANSWER_CALLBACK_DATA
from db.db_engine import Session, Results, set_results
from main import RegistrationStates, bot

AGE_CATEGORY_LOW = '14-15 лет'
AGE_CATEGORY_HIGH = '16-18 лет'


class Question(NamedTuple):
    """Question representation"""
    number: int
    text: str
    answers: list


def check_age_category(user_id: int):
    """User age check

    :param user_id: Telegram user id
    :return: age category
    """
    session = Session()
    user = session.query(Results).filter_by(user_id=user_id).first()

    return user.age_category


async def update_factor_based_on_age_and_question(age_category: str, question_number: int, state: FSMContext):
    """Updates the factor in the user's state based on the age category and question number.

    :param age_category: Age category ('14-15 years old' or '16-18 years old')
    :param question_number: Current issue number
    :param state: User state
    """

    age_category_mapping = {
        AGE_CATEGORY_LOW: {
            (1, 11): 'family_factor',
            (12, 22): 'psychological_factor',
            (23, 28): 'env_factor',
            (29, 35): 'school_factor',
        },
        AGE_CATEGORY_HIGH: {
            (1, 11): 'family_factor',
            (12, 22): 'psychological_factor',
            (23, 28): 'env_factor',
            (29, 35): 'school_factor',
        }
    }
    factors_dict = age_category_mapping.get(age_category)
    for number_range, factor in factors_dict.items():
        for number in number_range:
            if number == question_number:
                await state.update_data(factor=factor)


async def get_question(user_id, state: FSMContext):
    """Getting a question for a user

    :param user_id: Telegram user id
    :param state: state object
    :return: Question object
    """
    state_data = await state.get_data()
    age_category = state_data.get('age_category')
    if age_category == 'low':
        with open('bot_app/questions/14_15_questions.json', 'r') as file:
            json_data = json.load(file)
    else:
        with open('bot_app/questions/16_18_questions.json', 'r') as file:
            json_data = json.load(file)

    questions = json_data.get('questions')

    current_question_number = state_data.get('current_question')

    for question in questions:
        if question.get('number') == current_question_number:
            question_data = Question(
                number=question.get('number'),
                text=question.get('text'),
                answers=question.get('answers')
            )
            return question_data
    else:
        await bot.send_message(user_id, 'Спасибо, опрос завершен! Хорошего дня :)')
        await state.finish()
        return


async def add_points(user_id: int, factor: str, points: str):
    """Adding Factor Points

    :param user_id: Telegram user id
    :param factor: risk factor
    :param points: points of factor
    :return: Question object
    """
    session = Session()
    user = session.query(Results).filter_by(user_id=user_id).first()

    if factor == 'family_factor':
        new_value = user.family_factor + int(points)
        user.family_factor = new_value
        session.commit()

    elif factor == 'psychological_factor':
        new_value = user.psychological_factor + int(points)
        user.psychological_factor = new_value
        session.commit()

    elif factor == 'env_factor':
        new_value = user.env_factor + int(points)
        user.env_factor = new_value
        session.commit()

    elif factor == 'school_factor':
        new_value = user.school_factor + int(points)
        user.school_factor = new_value
        session.commit()


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
        new_user = Results(
            user_id=user_id, username=username
        )
        session.add(new_user)
        session.commit()
    else:
        await message.answer('Извините, Вы уже прошли тестирование')
        return

    await message.answer("Добро пожаловать! Введите Ваше имя", reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.get_name)


async def start_survey(message: types.Message, state: FSMContext):
    """Test start

    :param message: message object
    :param state: state object
    :return:
    """
    await message.answer(
        text='Уважаемые обучающиеся! Данное анкетирование проводится с целью изучения '
             'Вашего отношения к проблеме употребления психоактивных веществ. '
             'Внимательно прочитайте каждый вопрос и все предложенные варианты ответов к нем. '
             'Выберите один ответ, соответствующий Вашему мнению.\n',
        reply_markup=ReplyKeyboardRemove()
    )

    user_id = message.from_user.id
    session = Session()
    user = session.query(Results).filter_by(user_id=user_id).first()

    if message.text == AGE_CATEGORY_LOW:
        user.age_category = AGE_CATEGORY_LOW
        session.commit()

        await state.update_data(current_question=1, age_category='low')
    elif message.text == AGE_CATEGORY_HIGH:
        user.age_category = AGE_CATEGORY_HIGH
        session.commit()

        await state.update_data(current_question=1, age_category='high')
    else:
        await message.answer('Выберите один из предложенных вариантов')
        return

    question_data = await get_question(message.from_user.id, state)

    await state.update_data(factor='family_factor')

    data = await state.get_data()
    factor = data.get('factor')
    answers = question_data.answers

    keyboard = create_keyboard(user_id, factor, answers)
    await message.answer(question_data.text, reply_markup=keyboard)

    await state.update_data(
        answer=question_data.answers,
        current_question=question_data.number + 1,
        message_id=message.message_id
    )

    await state.set_state(RegistrationStates.survey_question)


async def survey_question(callback_query: types.CallbackQuery, state: FSMContext, callback_data: dict):
    """Response processing

    :param callback_query: callback_query object
    :param state: state object
    :param callback_data: user_id, factor, points
    :return:
    """
    await callback_query.answer()

    question_data = await get_question(callback_query.from_user.id, state)

    age_category = check_age_category(callback_query.from_user.id)

    if question_data:
        await update_factor_based_on_age_and_question(
            age_category=age_category,
            question_number=question_data.number,
            state=state
        )

        answers = question_data.answers

        user_id = callback_data['user_id']
        factor = callback_data['factor']
        points = callback_data['points']

        await add_points(
            user_id=user_id,
            factor=factor,
            points=points
        )

        keyboard = create_keyboard(callback_query.from_user.id, factor, answers)
        await bot.send_message(callback_query.from_user.id, question_data.text, reply_markup=keyboard)

        await state.update_data(
            answer=question_data.answers,
            current_question=question_data.number + 1,
            message_id=callback_query.message.message_id
        )

        await bot.delete_message(
            chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id
        )

        await state.set_state(RegistrationStates.survey_question)
    else:
        user_id = callback_data['user_id']
        factor = callback_data['factor']
        points = callback_data['points']

        await bot.delete_message(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id
        )

        await add_points(
            user_id=user_id,
            factor=factor,
            points=points
        )

        set_results(user_id=user_id)


def register_handlers_common(dp: Dispatcher):
    """User Registration Handlers

    :param dp: Dispatcher object
    :return:
    """
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(start_survey, state=RegistrationStates.start_survey)
    dp.register_callback_query_handler(survey_question, ANSWER_CALLBACK_DATA.filter(),
                                       state=RegistrationStates.survey_question)
