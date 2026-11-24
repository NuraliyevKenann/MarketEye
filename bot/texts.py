# Все тексты бота в одном месте — так их проще править.

# Описание бота: его видно в пустом чате до нажатия «Старт» (до 512 символов)
DESCRIPTION = (
    "MarketEye — your eye on the stock market.\n"
    "\n"
    "📈 Real-time stock prices\n"
    "📊 Charts and key company metrics\n"
    "📰 Latest news by ticker\n"
    "🤖 AI-powered sentiment and insights\n"
    "\n"
    "Just send a ticker like AAPL or TSLA and get a quick market snapshot. "
    "Press Start to begin!"
)

# Короткое описание: видно в профиле бота и при пересылке ссылки (до 120 символов)
SHORT_DESCRIPTION = "Stock prices, charts, news and AI sentiment by ticker 📈"

# Приветствие на /start (формат HTML: <b> — жирный, <code> — моноширинный)
START_TEXT = (
    "Привет, {name}! Я <b>MarketEye</b> 👁 — твой глаз на фондовом рынке.\n"
    "\n"
    "<b>Что я умею:</b>\n"
    "📈 Показывать цену акции\n"
    "📊 Графики и ключевые метрики компании\n"
    "📰 Свежие новости по тикеру\n"
    "🤖 Анализ настроения рынка с помощью ИИ\n"
    "\n"
    "<b>Как пользоваться:</b>\n"
    "Отправь команду и тикер компании — короткое название акции на бирже.\n"
    "\n"
    "<b>Пример:</b>\n"
    "<code>/price AAPL</code> — цена акций Apple\n"
    "<code>/price TSLA</code> — цена акций Tesla\n"
    "\n"
    "Все команды — /help"
)

HELP_TEXT = (
    "<b>Команды MarketEye</b>\n"
    "\n"
    "/start — приветствие\n"
    "/help — эта справка\n"
    "/price &lt;тикер&gt; — цена акции <i>(скоро)</i>\n"
    "\n"
    "<b>Популярные тикеры:</b> AAPL, TSLA, MSFT, NVDA, AMZN, GOOGL"
)
