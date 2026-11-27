# Ваш график цены.
#
# ЦЕЛЬ: функция make_chart(symbol, period)
#   получает:  тикер ("AAPL") и период ("6mo")
#   отдаёт:    картинку графика (PNG в байтах)
#
# Бот вызывает её, когда пользователь нажимает кнопку периода.
# Пока здесь заглушка — бот показывает логотип вместо графика.

# 👇 Шаг 1: импорты пишите здесь
import io
import yfinance as yf 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 

labels = {
    '1d': '1 день',
    '5d': '5 дней',
    '1mo': '1 месяц',
    '6mo': '6 месяцев',
    '1y': '1 год',
}


def make_chart(symbol, period):
    ticker=yf.Ticker(symbol)
    history=ticker.history(period=period)
    plt.plot(history['Close'])
    plt.title(f'{symbol} - {labels[period]}' )
    buf = io.BytesIO()
    plt.savefig(buf, format ='png')
    plt.close()
    return buf.getvalue()
