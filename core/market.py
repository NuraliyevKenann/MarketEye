"""Получение рыночных данных.

Этот файл ничего не знает про Telegram — только данные.
Поэтому потом его же используем для анализа данных и ML.
"""
from datetime import timedelta
from urllib.parse import urlparse

import yfinance as yf

# Периоды для кнопок: код -> (подпись, сколько дней назад)
PERIODS = {
    "1d": ("1 день", 1),
    "5d": ("5 дней", 7),      # 5 торговых дней = календарная неделя
    "1mo": ("1 месяц", 30),
    "6mo": ("6 месяцев", 182),
    "1y": ("1 год", 365),
}


class TickerNotFound(Exception):
    """Тикер не найден или по нему нет данных."""


def get_company(ticker):
    """Название компании и домен её сайта (для логотипа)."""
    info = yf.Ticker(ticker).info or {}
    name = info.get("shortName") or info.get("longName") or ticker
    website = info.get("website")
    domain = urlparse(website).netloc.removeprefix("www.") if website else None
    return name, domain


def get_price_change(ticker, period):
    """Текущая цена и её изменение за период.

    Возвращает (цена, изменение, изменение в %).
    """
    # Берём историю за год с запасом — из неё считаем любой период
    history = yf.Ticker(ticker).history(period="2y")
    if history.empty or len(history) < 2:
        raise TickerNotFound(ticker)

    closes = history["Close"]
    price = closes.iloc[-1]

    if period == "1d":
        # За день — сравниваем с закрытием предыдущего торгового дня
        start_price = closes.iloc[-2]
    else:
        days_back = PERIODS[period][1]
        start_date = closes.index[-1] - timedelta(days=days_back)
        # Последняя цена закрытия на дату начала периода или раньше
        start_price = closes[closes.index <= start_date].iloc[-1]

    change = price - start_price
    change_pct = change / start_price * 100
    return float(price), float(change), float(change_pct)
