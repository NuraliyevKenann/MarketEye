import asyncio
import logging
from html import escape

import aiohttp
from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

from bot.texts import COMING_SOON, HELP_TEXT, START_TEXT
from core.chart import make_chart
from core.market import PERIODS, TickerNotFound, get_company, get_price_change

router = Router()
log = logging.getLogger(__name__)

# Запоминаем название и логотип компании, чтобы не скачивать заново при нажатии кнопок
company_cache = {}


class PriceForm(StatesGroup):
    """Состояние «бот ждёт тикер от пользователя» (FSM — машина состояний)."""
    waiting_ticker = State()


@router.message(CommandStart())
async def start(message: Message):
    # escape — защита: имя пользователя может содержать символы < >, которые сломают HTML
    name = escape(message.from_user.first_name or "друг")
    await message.answer(START_TEXT.format(name=name))


@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(HELP_TEXT)


# ---------- /price ----------

async def download_logo(domain):
    """Скачивает иконку сайта компании. Если не вышло — возвращает None."""
    url = f"https://www.google.com/s2/favicons?domain={domain}&sz=256"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception:
        log.warning("Не удалось скачать логотип %s", domain)
    return None


async def get_company_cached(ticker):
    """Название + логотип компании (из кэша или из интернета)."""
    if ticker not in company_cache:
        # yfinance работает медленно и «замораживает» бота — запускаем в отдельном потоке
        name, domain = await asyncio.to_thread(get_company, ticker)
        logo = await download_logo(domain) if domain else None
        company_cache[ticker] = (name, logo)
    return company_cache[ticker]


def price_text(name, ticker, period, price, change, change_pct):
    arrow = "🟢" if change >= 0 else "🔴"
    sign = "+" if change >= 0 else ""
    period_name = PERIODS[period][0]
    return (
        f"📈 <b>{escape(name)}</b> ({ticker})\n"
        f"\n"
        f"Цена: <b>${price:.2f}</b>\n"
        f"За {period_name}: {sign}{change:.2f} ({sign}{change_pct:.2f}%) {arrow}"
    )


def period_keyboard(ticker, selected):
    """Панель кнопок с периодами. Выбранный период отмечен точкой."""
    buttons = []
    for code, (label, _days) in PERIODS.items():
        text = f"• {label} •" if code == selected else label
        # callback_data — скрытые данные кнопки: что нажали и для какой акции
        buttons.append(InlineKeyboardButton(text=text, callback_data=f"price:{ticker}:{code}"))
    # Раскладываем по 3 кнопки в ряд
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("price"))
async def price_cmd(message: Message, command: CommandObject, state: FSMContext):
    # /price TSLA — тикер уже есть, сразу показываем цену
    if command.args:
        await send_price_card(message, command.args.split()[0].upper())
        return

    # /price без тикера — спрашиваем и ждём ответа
    await state.set_state(PriceForm.waiting_ticker)
    prompt = await message.answer(
        "<b>TICKER:</b>",
        reply_markup=ForceReply(input_field_placeholder="например AAPL"),
    )
    # Запоминаем id сообщения «TICKER:», чтобы потом его стереть
    await state.update_data(prompt_id=prompt.message_id)


@router.message(PriceForm.waiting_ticker, F.text, ~F.text.startswith("/"))
async def price_ticker_entered(message: Message, state: FSMContext):
    """Пользователь прислал тикер после «TICKER:»."""
    data = await state.get_data()
    await state.clear()  # больше не ждём тикер

    # Стираем сообщение «TICKER:»
    try:
        await message.bot.delete_message(message.chat.id, data["prompt_id"])
    except Exception:
        pass  # уже удалено или слишком старое — не страшно

    await send_price_card(message, message.text.split()[0].upper())


async def send_price_card(message: Message, ticker: str):
    """Собирает данные и отправляет карточку с ценой, логотипом и кнопками."""
    period = "1d"

    loading = await message.answer("⏳ Собираю данные…")
    try:
        if len(ticker) > 12:  # таких длинных тикеров не бывает
            raise TickerNotFound(ticker)
        # Сначала цена: если тикера нет, дальше не идём
        price, change, change_pct = await asyncio.to_thread(get_price_change, ticker, period)
        name, logo = await get_company_cached(ticker)
    except TickerNotFound:
        await loading.edit_text(f"❌ Не нашёл тикер <b>{escape(ticker)}</b>. Пример: /price AAPL")
        return
    except Exception:
        log.exception("Ошибка /price %s", ticker)
        await loading.edit_text("⚠️ Не удалось получить данные. Попробуй позже.")
        return

    text = price_text(name, ticker, period, price, change, change_pct)
    keyboard = period_keyboard(ticker, period)

    # Картинка карточки: график, а если он не построился — логотип
    picture = await get_chart(ticker, period) or logo
    if picture:
        await message.answer_photo(
            BufferedInputFile(picture, filename=f"{ticker}.png"),
            caption=text,
            reply_markup=keyboard,
        )
        await loading.delete()
    else:
        await loading.edit_text(text, reply_markup=keyboard)


async def get_chart(ticker, period):
    """График из core/chart.py. Если не получилось — None (карточка всё равно придёт)."""
    try:
        return await asyncio.to_thread(make_chart, ticker, period)
    except Exception:
        log.exception("Не удалось построить график %s %s", ticker, period)
        return None


@router.callback_query(F.data.startswith("price:"))
async def price_period(callback: CallbackQuery):
    """Нажатие на кнопку периода: меняем и цифры, и график."""
    _, ticker, period = callback.data.split(":")
    await callback.answer("⏳ Собираю данные…")  # всплывающая подсказка сверху

    try:
        name, _logo = await get_company_cached(ticker)
        price, change, change_pct = await asyncio.to_thread(get_price_change, ticker, period)
    except Exception:
        log.exception("Ошибка кнопки периода %s %s", ticker, period)
        return

    text = price_text(name, ticker, period, price, change, change_pct)
    keyboard = period_keyboard(ticker, period)

    if not callback.message.photo:
        # Карточка без картинки — меняем только текст
        await callback.message.edit_text(text, reply_markup=keyboard)
        return

    chart = await get_chart(ticker, period)
    if chart:
        # Заменяем картинку на новый график вместе с подписью
        await callback.message.edit_media(
            InputMediaPhoto(
                media=BufferedInputFile(chart, filename=f"{ticker}_{period}.png"),
                caption=text,
            ),
            reply_markup=keyboard,
        )
    else:
        await callback.message.edit_caption(caption=text, reply_markup=keyboard)


# ---------- Заглушки ----------

# Команды пока отвечают «в разработке».
@router.message(Command("overview", "sentiment", "thesis", "watchlist"))
async def coming_soon(message: Message, command: CommandObject):
    await message.answer(COMING_SOON.format(cmd=command.command))


# Должен быть последним: ловит все остальные сообщения
@router.message()
async def fallback(message: Message):
    await message.answer("Не понял 🤔 Открой /help, чтобы увидеть команды")
