import yfinance as yf
import matplotlib.pyplot as plt

# Шаг 1. Тикер и период — в переменных. Меняешь здесь, меняется везде.
symbol = 'AAPL'
period = '6mo'

# Шаг 3. Словарь: код периода -> красивая подпись
labels = {
    '1d': '1 день',
    '5d': '5 дней',
    '1mo': '1 месяц',
    '6mo': '6 месяцев',
    '1y': '1 год',
}

ticker = yf.Ticker(symbol)
history = ticker.history(period=period)

last_price = history['Close'].iloc[-1]   # одно число — для текста
print('Цена', symbol, last_price)

# Рисуем ВСЮ колонку Close: по оси X — даты (индекс таблицы), по оси Y — цены
plt.plot(history['Close'])               # квадратные скобки — взять колонку

# Шаг 2. Заголовок собираем из переменных через f-строку
plt.title(f"{symbol} — {labels[period]}")

plt.savefig('chart.png')
print('График сохранён в chart.png')
