from typing import NamedTuple

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from db.db_engine import Session, Results
from bot_app.keyboard.keyboard_generator import create_answer_keyboard, create_reply_keyboard
from main import RegistrationStates


class Student(NamedTuple):
    """Student representation"""
    student_name: str
    student_last_name: str
    student_class: str


async def get_student_info(state: FSMContext):
    """Getting information about a student

    :param state: state object
    :return: student object
    """
    data = await state.get_data()
    student = Student(
        student_name=data.get('student_name'),
        student_last_name=data.get('student_last_name'),
        student_class=data.get('student_class'),
    )
    return student


async def get_student_name(message: types.Message, state: FSMContext):
    """Getting a student's name

    :param message: message object
    :param state: state object
    :return:
    """
    student_name = message.text
    await state.update_data(student_name=student_name)
    await message.answer('Введите Вашу фамилию')
    await state.set_state(RegistrationStates.get_last_name)


async def get_student_last_name(message: types.Message, state: FSMContext):
    """Getting a student's last name

    :param message: message object
    :param state: state object
    :return:
    """
    student_last_name = message.text
    await state.update_data(student_last_name=student_last_name)
    await message.answer('Введите Ваш класс')
    await state.set_state(RegistrationStates.get_class)


async def get_student_class(message: types.Message, state: FSMContext):
    """Getting a student's class

    :param message: message object
    :param state: state object
    :return:
    """
    student_class = message.text
    await state.update_data(student_class=student_class)

    student = await get_student_info(state)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Да').add('Нет')

    await message.answer(text=f'Подтвердите введенные данные:\n'
                              f'Имя: {student.student_name}\n'
                              f'Фамилия: {student.student_last_name}\n'
                              f'Класс: {student.student_class}',
                         reply_markup=keyboard)

    await state.set_state(RegistrationStates.confirmation)


async def confirmation(message: types.Message, state: FSMContext):
    """User data saving confirmation

    :param message: message object
    :param state: state object
    :return:
    """
    if message.text == 'Да':
        student = await get_student_info(state)
        user_id = message.from_user.id

        session = Session()
        user = session.query(Results).filter_by(user_id=user_id).first()

        user.first_name = student.student_name
        user.last_name = student.student_last_name
        user.student_class = student.student_class

        session.commit()

        keyboard = create_reply_keyboard('14-15 лет', '16-18 лет')
        await message.answer(
            'Выберите Вашу возрастную категорию',
            reply_markup=keyboard)
        await state.set_state(RegistrationStates.start_survey)
    else:
        await message.answer('Повторите регистрацию. Введите Ваше имя', reply_markup=ReplyKeyboardRemove())
        await state.set_state(RegistrationStates.get_name)


def register_handlers_registration(dp: Dispatcher):
    """User Registration Handlers

    :param dp: Dispatcher object
    :return:
    """
    dp.register_message_handler(get_student_name, state=RegistrationStates.get_name)
    dp.register_message_handler(get_student_last_name, state=RegistrationStates.get_last_name)
    dp.register_message_handler(get_student_class, state=RegistrationStates.get_class)
    dp.register_message_handler(confirmation, state=RegistrationStates.confirmation)
