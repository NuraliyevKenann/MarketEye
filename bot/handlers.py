from html import escape

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from bot.texts import COMING_SOON, HELP_TEXT, START_TEXT

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    # escape — защита: имя пользователя может содержать символы < >, которые сломают HTML
    name = escape(message.from_user.first_name or "друг")
    await message.answer(START_TEXT.format(name=name))


@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(HELP_TEXT)


# Заглушки: команды пока отвечают «в разработке».
# TODO: заменить на свои обработчики, например @router.message(Command("price"))
@router.message(Command("price", "overview", "sentiment", "thesis", "watchlist"))
async def coming_soon(message: Message, command: CommandObject):
    await message.answer(COMING_SOON.format(cmd=command.command))


# Должен быть последним: ловит все остальные сообщения
@router.message()
async def fallback(message: Message):
    await message.answer("Не понял 🤔 Открой /help, чтобы увидеть команды")
