import json
from typing import NamedTuple

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot_app.keyboard.keyboard_generator import create_answer_keyboard, ANSWER_CALLBACK_DATA
from bot_main import RegistrationStates, bot
from db.db_engine import Session, Results, User

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
    with session:
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
            (1, 13): 'family_factor',
            (14, 30): 'psychological_factor',
            (31, 46): 'env_factor',
            (47, 53): 'school_factor',
        },
        AGE_CATEGORY_HIGH: {
            (1, 16): 'family_factor',
            (17, 30): 'psychological_factor',
            (31, 47): 'env_factor',
            (48, 54): 'school_factor',
        }
    }
    factors_dict = age_category_mapping.get(age_category)
    for number_range, factor in factors_dict.items():
        low = number_range[0]
        high = number_range[1]
        if low <= question_number <= high:
            await state.update_data(factor=factor)
            break


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
        await bot.send_message(
            user_id,
            'Спасибо, опрос завершен! Хорошего дня :)\n\nНашли ошибку или баг? Нажми /bug_report'
        )
        await state.finish()


async def cmd_start(message: types.Message, state: FSMContext):
    """Handler processing start command

    :param message: message object
    :param state: state object
    :return:
    """
    user_id = message.from_user.id
    username = message.from_user.username

    session = Session()
    with (session):
        user = session.query(Results).filter_by(user_id=user_id).first()
        if user is None:
            user = User(user_id=user_id)
            user.add_user(username=username)
        else:
            await message.answer('Извините, Вы уже прошли тестирование', reply_markup=ReplyKeyboardRemove())
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
    with session:
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

        keyboard = create_answer_keyboard(user_id, factor, answers)
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
    from db.db_engine import User

    question_data = await get_question(callback_query.from_user.id, state)

    age_category = check_age_category(callback_query.from_user.id)

    if question_data:
        await update_factor_based_on_age_and_question(
            age_category=age_category,
            question_number=question_data.number,
            state=state
        )

        answers = question_data.answers

        data = await state.get_data()
        factor = data['factor']

        user_id = callback_data['user_id']
        points = callback_data['points']

        user = User(
            user_id=user_id
        )
        user.edit_factor(
            factor=factor,
            value=points
        )

        await callback_query.answer()

        keyboard = create_answer_keyboard(callback_query.from_user.id, factor, answers)
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

        user = User(
            user_id=user_id
        )
        user.edit_factor(
            factor=factor,
            value=points
        )

        await callback_query.answer()
        user.set_results()


def register_handlers_common(dp: Dispatcher):
    """User Registration Handlers

    :param dp: Dispatcher object
    :return:
    """
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(start_survey, state=RegistrationStates.start_survey)
    dp.register_callback_query_handler(survey_question, ANSWER_CALLBACK_DATA.filter(),
                                       state=RegistrationStates.survey_question)
