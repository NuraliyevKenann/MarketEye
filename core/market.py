"""Получение рыночных данных через yfinance (Yahoo Finance).

Модуль ничего не знает о Telegram: только данные. Поэтому его же
можно использовать в анализе данных и ML.
"""
from dataclasses import dataclass

import yfinance as yf


class TickerNotFound(Exception):
    """Тикер не найден или по нему нет данных."""


@dataclass
class PriceInfo:
    ticker: str
    name: str
    currency: str
    price: float
    change: float          # изменение к закрытию предыдущего дня
    change_pct: float      # то же в процентах


@dataclass
class Overview:
    ticker: str
    name: str
    currency: str
    sector: str | None
    industry: str | None
    country: str | None
    market_cap: float | None
    trailing_pe: float | None
    forward_pe: float | None
    dividend_yield: float | None   # уже в процентах, например 0.31 = 0.31%
    high_52w: float | None
    low_52w: float | None
    website: str | None
    summary: str | None


def get_price(ticker: str) -> PriceInfo:
    """Последняя цена и изменение за день.

    Функция синхронная (yfinance ходит в интернет и ждёт ответа),
    поэтому из бота её вызываем через asyncio.to_thread.
    """
    ticker = ticker.upper()
    t = yf.Ticker(ticker)

    # Берём 5 дней, чтобы точно было 2 торговых дня даже после выходных
    history = t.history(period="5d")
    if history.empty or len(history) < 2:
        raise TickerNotFound(ticker)

    price = float(history["Close"].iloc[-1])
    prev_close = float(history["Close"].iloc[-2])
    change = price - prev_close

    info = t.info or {}
    return PriceInfo(
        ticker=ticker,
        name=info.get("shortName") or info.get("longName") or ticker,
        currency=info.get("currency") or "USD",
        price=price,
        change=change,
        change_pct=change / prev_close * 100,
    )


def get_overview(ticker: str) -> Overview:
    """Краткая информация о компании и ключевые метрики."""
    ticker = ticker.upper()
    info = yf.Ticker(ticker).info or {}

    # Для несуществующего тикера Yahoo возвращает почти пустой словарь
    name = info.get("longName") or info.get("shortName")
    if not name:
        raise TickerNotFound(ticker)

    return Overview(
        ticker=ticker,
        name=name,
        currency=info.get("currency") or "USD",
        sector=info.get("sector"),
        industry=info.get("industry"),
        country=info.get("country"),
        market_cap=info.get("marketCap"),
        trailing_pe=info.get("trailingPE"),
        forward_pe=info.get("forwardPE"),
        dividend_yield=info.get("dividendYield"),
        high_52w=info.get("fiftyTwoWeekHigh"),
        low_52w=info.get("fiftyTwoWeekLow"),
        website=info.get("website"),
        summary=info.get("longBusinessSummary"),
    )
