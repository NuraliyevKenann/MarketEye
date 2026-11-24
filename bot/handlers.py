from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

# Router — группа обработчиков сообщений
router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет, я MarketEye 👁")


@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer("/start — начать\n/help — помощь")


# Эхо должно быть последним: оно ловит все остальные сообщения
@router.message()
async def echo(message: Message):
    await message.answer(message.text)
