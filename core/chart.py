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


def make_chart(symbol, period, logo=None):
    ticker=yf.Ticker(symbol)
    if period == '1d':
        history = ticker.history(period=period, interval='5m')
    else:
        history = ticker.history(period=period)
    close = history['Close']

    # Цвет линии: выросла за период — зелёная, упала — красная
    if close.iloc[-1] >= close.iloc[0]:
        color = '#16a34a'
    else:
        color = '#dc2626'

    fig,ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(close, color=color, linewidth=2)
    ax.set_title(f'{symbol} - {labels[period]}', loc='left', fontsize=14)

    # Убираем лишние линии рамки сверху и справа, сетка еле заметная
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(alpha=0.2)
    fig.autofmt_xdate()  # наклоняем даты, чтобы не налезали

    # Маленький логотип компании в правом верхнем углу
    if logo:
        logo_ax = fig.add_axes([0.86, 0.86, 0.1, 0.1])  # [x, y, ширина, высота] в долях картинки
        logo_ax.imshow(plt.imread(io.BytesIO(logo)))
        logo_ax.axis('off')

    # Сохраняем В САМОМ КОНЦЕ — после всего оформления
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return buf.getvalue()
