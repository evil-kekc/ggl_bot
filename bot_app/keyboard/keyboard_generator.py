from aiogram import types
from aiogram.utils.callback_data import CallbackData

ANSWER_CALLBACK_DATA = CallbackData('answers', 'user_id', 'factor', 'points')


def create_keyboard(user_id: int | str, factor: str, answers: list) -> types.InlineKeyboardMarkup:
    """Create confirm expenses_kb

    :param user_id: Telegram user id
    :param factor: psychological factor
    :param answers: answers variants list
    :return: types.InlineKeyboardMarkup
    """

    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)

    for answer in answers:
        keyboard.add(
            types.InlineKeyboardButton(text=answer.get('text'),
                                       callback_data=ANSWER_CALLBACK_DATA.new(user_id=user_id,
                                                                              factor=factor,
                                                                              points=answer.get('points'))
                                       )
        )

    return keyboard
