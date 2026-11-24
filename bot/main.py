import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from core.config import BOT_TOKEN
from bot.handlers import router
from bot.texts import DESCRIPTION, SHORT_DESCRIPTION


async def setup_bot_profile(bot: Bot):
    """Описание бота и меню команд (кнопка «Меню» слева от поля ввода)."""
    await bot.set_my_description(DESCRIPTION)
    await bot.set_my_short_description(SHORT_DESCRIPTION)
    await bot.set_my_commands([
        BotCommand(command="start", description="Приветствие"),
        BotCommand(command="help", description="Список команд"),
        BotCommand(command="price", description="Цена акции, например /price AAPL"),
    ])


async def main():
    logging.basicConfig(level=logging.INFO)
    # parse_mode=HTML — во всех ответах можно использовать <b>, <i>, <code>
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await setup_bot_profile(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
