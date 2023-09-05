from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_keyboard(*buttons):
    """Create ReplyKeyboardMarkup"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if buttons:
        for button_text in buttons:
            keyboard.add(KeyboardButton(button_text))
        return keyboard
    else:
        return keyboard
