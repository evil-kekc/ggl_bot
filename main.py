import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv('BOT_TOKEN')

storage = MemoryStorage()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())


class RegistrationStates(StatesGroup):
    get_name = State()
    get_last_name = State()
    get_class = State()
    confirmation = State()
    start_survey = State()
    survey_question = State()


if __name__ == '__main__':
    from aiogram import executor
    from bot_app.registration import register_handlers_registration
    from bot_app.common import register_handlers_common

    register_handlers_common(dp)
    register_handlers_registration(dp)

    executor.start_polling(dp, skip_updates=True)
