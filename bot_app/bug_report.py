import os

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv

from bot_app.keyboard.keyboard_generator import create_bug_report_keyboard, create_reply_keyboard, \
    BUG_REPORT_CALLBACK_DATA
from db.db_engine import Session, BugReport, add_bug_report, edit_bug_report_status, add_user, Results
from main import ReportAnswer, bot, Report


async def cancel(message: types.Message, state: FSMContext):
    """Cancel input and finish the conversation state.

    :param message: The user's message that triggered the cancellation.
    :type message: types.Message
    :param state: The FSM (Finite State Machine) context.
    :type state: FSMContext
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Ввод отменен', reply_markup=types.ReplyKeyboardRemove())


async def start_report_mess(message: types.Message):
    """Start reporting a problem and set the conversation state to 'Report.send_report'.

    :param message: The user's message that starts the reporting process.
    :type message: types.Message
    """
    cancel_button = create_reply_keyboard()

    session = Session()
    user = session.query(Results).filter_by(user_id=message.from_user.id).first()
    if user is None:
        add_user(
            user_id=message.from_user.id,
            username=message.from_user.username
        )

    await bot.send_message(
        message.from_user.id, f'Опишите проблему, с которой вы столкнулись',
        reply_markup=cancel_button
    )
    await Report.send_report.set()


async def send_report(message: types.Message, state: FSMContext):
    """Handle user's choice and send a bug report to the admin.

    :param message: The user's message with their choice.
    :type message: types.Message
    :param state: The FSM (Finite State Machine) context.
    :type state: FSMContext
    """
    send_report_answer = create_bug_report_keyboard(message.from_user.id)
    load_dotenv()

    await bot.copy_message(
        os.getenv('ADMIN_ID'),
        message.from_user.id, message.message_id,
        reply_markup=send_report_answer
    )

    add_bug_report(
        user_id=message.from_user.id,
        description=message.text
    )

    await message.reply(
        'Спасибо за ваш отчет, мы рассмотрим ваше обращение в ближайшее время',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()


async def get_answer(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """Handle getting an answer from the admin.

    :param callback_query: The callback query from the admin.
    :type callback_query: types.CallbackQuery
    :param callback_data: Data associated with the callback query.
    :type callback_data: dict
    :param state: The FSM (Finite State Machine) context.
    :type state: FSMContext
    """
    user_id = callback_data['user_id']

    await state.update_data(id=user_id)
    await state.update_data(message_id=callback_query.message.message_id)

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        f'Введите ответ'
    )

    await state.set_state(ReportAnswer.send_answer.state)


async def send_answer(message: types.Message, state: FSMContext):
    """Send an answer to the user.

    :param message: The admin message with the answer.
    :type message: types.Message
    :param state: The FSM (Finite State Machine) context.
    :type state: FSMContext
    """
    data = await state.get_data()
    user_id = data['id']
    message_id = data['message_id']

    edit_bug_report_status(
        user_id=user_id,
        status='Closed'
    )

    await bot.delete_message(message.from_user.id, message_id)

    await bot.send_message(user_id, message.text)
    await state.finish()


def bug_report_register_handlers(dp: Dispatcher):
    dp.register_message_handler(cancel, commands=['отмена', 'cancel'])
    dp.register_message_handler(cancel, Text(equals='отмена', ignore_case=True))

    dp.register_message_handler(start_report_mess, commands='bug_report')

    dp.register_message_handler(send_report, state=Report.send_report)

    dp.register_message_handler(send_answer, state=ReportAnswer.send_answer)

    dp.register_callback_query_handler(get_answer, BUG_REPORT_CALLBACK_DATA.filter())
