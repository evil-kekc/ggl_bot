from typing import Union

from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

ANSWER_CALLBACK_DATA = CallbackData('answers', 'user_id', 'factor', 'points')
BUG_REPORT_CALLBACK_DATA = CallbackData('bug_report', 'user_id')


def create_answer_keyboard(user_id: int | str, factor: str, answers: list) -> types.InlineKeyboardMarkup:
    """Create answer InlineKeyboard

    :param user_id: Telegram user id
    :param factor: psychological factor
    :param answers: answers variants list
    :return: types.InlineKeyboardMarkup
    """

    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)

    for answer in answers:
        keyboard.add(
            types.InlineKeyboardButton(
                text=answer.get('text'),
                callback_data=ANSWER_CALLBACK_DATA.new(
                    user_id=user_id,
                    factor=factor,
                    points=answer.get('points')
                )
            )
        )

    return keyboard


def create_bug_report_keyboard(user_id: int | str) -> types.InlineKeyboardMarkup:
    """Create bug report InlineKeyboard

    :param user_id: Telegram user id
    :return: types.InlineKeyboardMarkup
    """

    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)

    keyboard.add(
        types.InlineKeyboardButton(
            text='Ответить',
            callback_data=BUG_REPORT_CALLBACK_DATA.new(user_id=user_id)
        )
    )

    return keyboard


def create_reply_keyboard(*buttons: str) -> ReplyKeyboardMarkup:
    """Creates a ReplyKeyboardMarkup with the specified buttons.

    :param buttons: List of buttons that need to be added to the keyboard.
    :type buttons: Union[list, tuple]
    :return: List of buttons that need to be added to the keyboard.
    :rtype: types.ReplyKeyboardMarkup
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for button_text in buttons:
        keyboard.add(button_text)

    return keyboard
