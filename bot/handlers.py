import asyncio
import logging
import re
from html import escape

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from bot.formatting import format_overview, format_price
from bot.texts import COMING_SOON, HELP_TEXT, NO_TICKER, START_TEXT, TICKER_NOT_FOUND
from core.market import TickerNotFound, get_overview, get_price

router = Router()
log = logging.getLogger(__name__)

# Тикер: латиница, цифры, точка, дефис, ^ и = (например AAPL, BRK-B, ^GSPC, BTC-USD)
TICKER_RE = re.compile(r"^[A-Za-z0-9.\-^=]{1,12}$")


def parse_ticker(text: str | None) -> str | None:
    """Достаёт тикер из аргумента команды: '/price aapl' -> 'AAPL'."""
    if not text:
        return None
    first = text.split()[0]
    return first.upper() if TICKER_RE.match(first) else None


async def reply_with_data(message: Message, ticker: str, fetch, formatter):
    """Общая логика: показать «печатает…», получить данные, ответить или сообщить об ошибке."""
    await message.bot.send_chat_action(message.chat.id, "typing")
    try:
        # yfinance синхронный — запускаем в отдельном потоке, чтобы бот не «зависал»
        data = await asyncio.to_thread(fetch, ticker)
    except TickerNotFound:
        await message.answer(TICKER_NOT_FOUND.format(ticker=escape(ticker)))
        return
    except Exception:
        log.exception("Ошибка при получении данных для %s", ticker)
        await message.answer("⚠️ Не удалось получить данные. Попробуй ещё раз чуть позже.")
        return
    await message.answer(formatter(data), disable_web_page_preview=True)


@router.message(CommandStart())
async def start(message: Message):
    # escape — защита: имя пользователя может содержать символы < >, которые сломают HTML
    name = escape(message.from_user.first_name or "друг")
    await message.answer(START_TEXT.format(name=name))


@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(HELP_TEXT)


@router.message(Command("price"))
async def price_cmd(message: Message, command: CommandObject):
    ticker = parse_ticker(command.args)
    if not ticker:
        await message.answer(NO_TICKER.format(cmd="price"))
        return
    await reply_with_data(message, ticker, get_price, format_price)


@router.message(Command("overview"))
async def overview_cmd(message: Message, command: CommandObject):
    ticker = parse_ticker(command.args)
    if not ticker:
        await message.answer(NO_TICKER.format(cmd="overview"))
        return
    await reply_with_data(message, ticker, get_overview, format_overview)


# Команды в разработке — пока отвечают «скоро»
@router.message(Command("sentiment", "thesis", "watchlist"))
async def coming_soon(message: Message, command: CommandObject):
    await message.answer(COMING_SOON.format(cmd=command.command))


# Просто тикер без команды (например «AAPL») — показываем цену
@router.message(F.text.regexp(TICKER_RE))
async def plain_ticker(message: Message):
    await reply_with_data(message, message.text.upper(), get_price, format_price)


# Всё остальное должно быть последним: ловит любые другие сообщения
@router.message()
async def fallback(message: Message):
    await message.answer("Не понял 🤔 Отправь тикер, например <code>AAPL</code>, или открой /help")
