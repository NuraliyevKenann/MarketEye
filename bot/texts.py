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

# Меню команд (кнопка «Меню» в Telegram): команда -> описание
COMMANDS = {
    "start": "Приветствие",
    "help": "Список команд",
    "price": "Цена акции",
    "overview": "О компании и ключевые метрики (скоро)",
    "sentiment": "Настроение рынка по новостям (скоро)",
    "thesis": "Инвест-идея от ИИ: за и против (скоро)",
    "watchlist": "Мой список акций (скоро)",
}

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
    "<b>Примеры:</b>\n"
    "<code>/price AAPL</code> — цена акций Apple\n"
    "<code>/price TSLA</code> — цена акций Tesla\n"
    "<code>/overview NVDA</code> — всё о компании Nvidia\n"
    "\n"
    "Все команды — /help"
)

HELP_TEXT = (
    "<b>Команды MarketEye</b>\n"
    "\n"
    "/price &lt;тикер&gt; — цена и изменение за период\n"
    "/overview &lt;тикер&gt; — о компании и ключевые метрики <i>(скоро)</i>\n"
    "/sentiment &lt;тикер&gt; — настроение по новостям <i>(скоро)</i>\n"
    "/thesis &lt;тикер&gt; — инвест-идея от ИИ <i>(скоро)</i>\n"
    "/watchlist — мой список акций <i>(скоро)</i>\n"
    "\n"
    "<b>Популярные тикеры:</b> AAPL, TSLA, MSFT, NVDA, AMZN, GOOGL"
)

COMING_SOON = "🛠 Команда /{cmd} уже в разработке — скоро заработает!"
