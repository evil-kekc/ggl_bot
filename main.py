import logging
import os

import uvicorn
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import BotCommand
from fastapi import FastAPI

from bot_app.bot_main import API_TOKEN, storage
from bot_app.bug_report import bug_report_register_handlers
from bot_app.common import register_handlers_common
from bot_app.registration import register_handlers_registration
from logs.logger import get_logger

logger = get_logger(
    logger_name='aiogram',
    log_file_name='logs/ggl_bot.log'
)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

HOST_URL = os.getenv('HOST_URL')
WEBHOOK_PATH = f"/webhook"
WEBHOOK_URL = HOST_URL + WEBHOOK_PATH

app = FastAPI()


async def set_commands(bot_: Bot):
    """Set commands for bot

    :param bot_: Bot class instance
    :return:
    """
    commands = [
        BotCommand(command='/start', description='Начало работы'),
    ]

    await bot_.set_my_commands(commands)


async def bot_main():
    """Applies all bot settings

    :return:
    """
    logger.info('Starting bot')

    register_handlers_common(dp)
    register_handlers_registration(dp)
    bug_report_register_handlers(dp)

    await set_commands(bot)


@app.on_event("startup")
async def on_startup():
    """Setting up a webhook

    :return:
    """
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    """Getting Telegram updates

    :param update: Telegram update
    :return:
    """
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await bot_main()
    await dp.process_update(telegram_update)


@app.on_event("shutdown")
async def on_shutdown():
    """Closing session and delete webhook

    :return:
    """
    await bot.session.close()
    await bot.delete_webhook()


@app.get('/info')
async def home_page():
    """GET request to getting info about bot running

    :return: info about bot running
    """
    return 'Bot running successfully!'


if __name__ == "__main__":
    APP_HOST = os.getenv('APP_HOST')
    APP_PORT = int(os.getenv('APP_PORT'))
    uvicorn.run(
        app,
        host=APP_HOST,
        port=APP_PORT
    )
