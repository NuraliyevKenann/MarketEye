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
from core.overview import get_overview
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
    await ask_ticker(message, state, cmd="price")


@router.message(Command("overview"))
async def overview_cmd(message: Message, command: CommandObject, state: FSMContext):
    if command.args:
        await send_overview(message, command.args.split()[0].upper())
        return
    await ask_ticker(message, state, cmd="overview")


async def ask_ticker(message: Message, state: FSMContext, cmd: str):
    """Отправляет «TICKER:» и запоминает, для какой команды ждём тикер."""
    await state.set_state(PriceForm.waiting_ticker)
    prompt = await message.answer(
        "<b>TICKER:</b>",
        reply_markup=ForceReply(input_field_placeholder="например AAPL"),
    )
    # Запоминаем id сообщения «TICKER:» (чтобы стереть) и команду
    await state.update_data(prompt_id=prompt.message_id, cmd=cmd)


@router.message(PriceForm.waiting_ticker, F.text, ~F.text.startswith("/"))
async def ticker_entered(message: Message, state: FSMContext):
    """Пользователь прислал тикер после «TICKER:»."""
    data = await state.get_data()
    await state.clear()  # больше не ждём тикер

    # Стираем сообщение «TICKER:»
    try:
        await message.bot.delete_message(message.chat.id, data["prompt_id"])
    except Exception:
        pass  # уже удалено или слишком старое — не страшно

    ticker = message.text.split()[0].upper()
    if data.get("cmd") == "overview":
        await send_overview(message, ticker)
    else:
        await send_price_card(message, ticker)


# ---------- /overview ----------

RECOMMENDATIONS = {
    "strong_buy": "Активно покупать 🟢🟢",
    "buy": "Покупать 🟢",
    "hold": "Держать 🟡",
    "underperform": "Хуже рынка 🟠",
    "sell": "Продавать 🔴",
}


COUNTRY_CODES = {
    "United States": "US", "Canada": "CA", "United Kingdom": "GB", "Germany": "DE",
    "France": "FR", "Netherlands": "NL", "Switzerland": "CH", "Ireland": "IE",
    "Sweden": "SE", "Denmark": "DK", "Norway": "NO", "Finland": "FI", "Spain": "ES",
    "Italy": "IT", "Belgium": "BE", "Luxembourg": "LU", "Japan": "JP", "China": "CN",
    "Hong Kong": "HK", "Taiwan": "TW", "South Korea": "KR", "India": "IN",
    "Singapore": "SG", "Australia": "AU", "Israel": "IL", "Brazil": "BR",
    "Mexico": "MX", "Argentina": "AR", "Bermuda": "BM", "Cayman Islands": "KY",
    "Uruguay": "UY", "Chile": "CL", "South Africa": "ZA", "Russia": "RU",
    "Kazakhstan": "KZ", "Azerbaijan": "AZ", "Turkey": "TR", "Greece": "GR",
}


def flag(country):
    """'United States' -> 🇺🇸. Флаг собирается из двух «букв-флагов» Unicode."""
    code = COUNTRY_CODES.get(country)
    if not code:
        return "🌍"
    return "".join(chr(0x1F1E6 + ord(letter) - ord("A")) for letter in code)


def big_number(value):
    """5210368901120 -> 5.21T"""
    if value is None:
        return "—"
    for limit, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M")):
        if abs(value) >= limit:
            return f"{value / limit:.2f}{suffix}"
    return f"{value:,.0f}"


NO_DATA = "<i>нет данных</i>"


def num(value, fmt="{:.2f}"):
    """Число по шаблону или «нет данных»."""
    return NO_DATA if value is None else fmt.format(value)


def overview_text(ticker, o):
    def esc(value):
        return escape(value) if value else NO_DATA

    target = num(o["target_price"], "${:.2f}")
    # Насколько целевая цена выше/ниже текущей
    if o["price"] and o["target_price"]:
        target += f" ({(o['target_price'] / o['price'] - 1) * 100:+.1f}%)"

    sections = [
        # 1. Кто это
        f"🏢 <b>{escape(o['name'])}</b> ({ticker})\n"
        f"{flag(o['country'])} {esc(o['country'])}",

        # 2. Профиль
        "<b>📋 Профиль</b>\n"
        f"Сектор: {esc(o['sector'])}\n"
        f"Отрасль: {esc(o['industry'])}\n"
        f"Сотрудники: {num(o['employees'], '{:,}')}",

        # 3. Цена
        "<b>💵 Цена</b>\n"
        f"Сейчас: <b>{num(o['price'], '${:.2f}')}</b>\n"
        f"Мин. за год: {num(o['low_52w'], '${:.2f}')}\n"
        f"Макс. за год: {num(o['high_52w'], '${:.2f}')}",

        # 4. Оценка
        "<b>📊 Оценка</b>\n"
        f"Капитализация: {NO_DATA if o['market_cap'] is None else '$' + big_number(o['market_cap'])}\n"
        f"P/E: {num(o['pe'])}\n"
        f"Прогнозный P/E: {num(o['forward_pe'])}\n"
        f"Дивиденды: {num(o['dividend_yield'], '{:.2f}%')}",

        # 5. Аналитики
        "<b>🎯 Аналитики</b>\n"
        f"Целевая цена: {target}\n"
        f"Рекомендация: {RECOMMENDATIONS.get(o['recommendation'], NO_DATA)}",
    ]
    # Разделы отделяем пустой строкой
    return "\n\n".join(sections)


async def send_overview(message: Message, ticker: str):
    """Собирает данные о компании (core/overview.py) и отправляет карточку."""
    loading = await message.answer("⏳ Собираю данные…")
    try:
        if len(ticker) > 12:
            raise TickerNotFound(ticker)
        o = await asyncio.to_thread(get_overview, ticker)
        if not o.get("name"):  # для несуществующего тикера Yahoo не даёт название
            raise TickerNotFound(ticker)
        _name, logo = await get_company_cached(ticker)
    except TickerNotFound:
        await loading.edit_text(f"❌ Не нашёл тикер <b>{escape(ticker)}</b>. Пример: /overview AAPL")
        return
    except Exception:
        log.exception("Ошибка /overview %s", ticker)
        await loading.edit_text("⚠️ Не удалось получить данные. Попробуй позже.")
        return

    text = overview_text(ticker, o)
    if logo:
        await message.answer_photo(BufferedInputFile(logo, filename=f"{ticker}.png"), caption=text)
        await loading.delete()
    else:
        await loading.edit_text(text)


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
    picture = await get_chart(ticker, period, logo) or logo
    if picture:
        await message.answer_photo(
            BufferedInputFile(picture, filename=f"{ticker}.png"),
            caption=text,
            reply_markup=keyboard,
        )
        await loading.delete()
    else:
        await loading.edit_text(text, reply_markup=keyboard)


async def get_chart(ticker, period, logo=None):
    """График из core/chart.py. Если не получилось — None (карточка всё равно придёт)."""
    try:
        return await asyncio.to_thread(make_chart, ticker, period, logo)
    except Exception:
        log.exception("Не удалось построить график %s %s", ticker, period)
        return None


@router.callback_query(F.data.startswith("price:"))
async def price_period(callback: CallbackQuery):
    """Нажатие на кнопку периода: меняем и цифры, и график."""
    _, ticker, period = callback.data.split(":")
    await callback.answer("⏳ Собираю данные…")  # всплывающая подсказка сверху

    try:
        name, logo = await get_company_cached(ticker)
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

    chart = await get_chart(ticker, period, logo)
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
@router.message(Command("sentiment", "thesis", "watchlist"))
async def coming_soon(message: Message, command: CommandObject):
    await message.answer(COMING_SOON.format(cmd=command.command))


# Должен быть последним: ловит все остальные сообщения
@router.message()
async def fallback(message: Message):
    await message.answer("Не понял 🤔 Открой /help, чтобы увидеть команды")
