from html import escape

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.texts import START_TEXT, HELP_TEXT

# Router — группа обработчиков сообщений
router = Router()


@router.message(CommandStart())
async def start(message: Message):
    # escape — защита: имя пользователя может содержать символы < >, которые сломают HTML
    name = escape(message.from_user.first_name or "друг")
    await message.answer(START_TEXT.format(name=name))


@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(HELP_TEXT)


# Эхо должно быть последним: оно ловит все остальные сообщения
@router.message()
async def echo(message: Message):
    if message.text:
        await message.answer(message.text, parse_mode=None)
