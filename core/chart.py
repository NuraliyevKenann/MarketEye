"""График цены акции — картинка PNG для бота."""
import io

import matplotlib
matplotlib.use("Agg")  # рисуем без окна на экране — только в память (нужно для бота)
import matplotlib.pyplot as plt
import yfinance as yf

# Подписи периодов для заголовка
labels = {
    '1d': '1 день',
    '5d': '5 дней',
    '1mo': '1 месяц',
    '6mo': '6 месяцев',
    '1y': '1 год',
}

# Шаг между точками: для коротких периодов берём цены внутри дня,
# иначе за 1 день была бы всего одна точка
intervals = {
    '1d': '5m',    # каждые 5 минут
    '5d': '30m',   # каждые 30 минут
}

GREEN = '#22c55e'
RED = '#ef4444'
BACKGROUND = '#17212b'   # цвет тёмной темы Telegram
TEXT = '#c8d3df'


def make_chart(symbol, period):
    """Рисует график цены и возвращает PNG-картинку в байтах."""
    ticker = yf.Ticker(symbol)
    history = ticker.history(period=period, interval=intervals.get(period, '1d'))
    if history.empty:
        raise ValueError(f"Нет данных для {symbol}")

    close = history['Close']
    # Цена выросла за период — зелёный, упала — красный
    color = GREEN if close.iloc[-1] >= close.iloc[0] else RED

    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_facecolor(BACKGROUND)
    ax.set_facecolor(BACKGROUND)

    # По оси X берём номера точек, а не даты: так нет пустых «дыр» на ночи и выходные
    x = range(len(close))
    ax.plot(x, close.values, color=color, linewidth=2)
    ax.fill_between(x, close.values, close.min(), color=color, alpha=0.15)  # заливка под линией

    # Подписи дат снизу — 5 штук равномерно
    step = max(len(close) // 5, 1)
    ticks = list(range(0, len(close), step))
    date_format = '%H:%M' if period == '1d' else '%d.%m'
    ax.set_xticks(ticks)
    ax.set_xticklabels([close.index[i].strftime(date_format) for i in ticks])

    ax.set_title(f"{symbol} — {labels.get(period, period)}", color=TEXT, fontsize=14, pad=12)
    ax.tick_params(colors=TEXT)
    ax.grid(color=TEXT, alpha=0.1)
    for side in ax.spines.values():
        side.set_visible(False)

    buf = io.BytesIO()              # «файл» в памяти
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    plt.close(fig)                  # очищаем, иначе следующий график нарисуется поверх
    return buf.getvalue()
