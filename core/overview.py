# Информация о компании для команды /overview.
#
# ЦЕЛЬ: функция get_overview(symbol)
#   получает:  тикер ("AAPL")
#   отдаёт:    словарь с данными о компании, например:
#              {'name': 'Apple Inc.', 'sector': 'Technology', 'market_cap': 5118960861184, ...}
#
# Бот возьмёт этот словарь и красиво покажет его в Telegram.

import yfinance as yf


def get_overview(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info

    # Свой словарь: 'наш ключ': значение из info по ключу yfinance
    overview = {
        'name': info.get('longName'),
        'sector': info.get('sector'),
        'industry': info.get('industry'),
        'country': info.get('country'),
        'employees': info.get('fullTimeEmployees'),
        'price': info.get('currentPrice'),
        'market_cap': info.get('marketCap'),
        'pe': info.get('trailingPE'),
        'forward_pe': info.get('forwardPE'),
        'dividend_yield': info.get('dividendYield'),
        'low_52w': info.get('fiftyTwoWeekLow'),
        'high_52w': info.get('fiftyTwoWeekHigh'),
        'target_price': info.get('targetMeanPrice'),
        'recommendation': info.get('recommendationKey'),
    }

    return overview
