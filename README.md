# MarketEye 👁

Telegram-бот для анализа акций (учебный проект).

## Запуск

1. Создай виртуальное окружение и активируй его:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac / Linux
   ```
2. Установи зависимости:
   ```
   pip install -r requirements.txt
   ```
3. Скопируй файл `.env.example`, назови копию `.env` и вставь в неё токен от @BotFather.
4. Запусти из корня проекта:
   ```
   python -m bot.main
   ```

## Команды

- `/start` — начать
- `/help` — помощь
