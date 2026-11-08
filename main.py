"""Точка входа для хостинга (bothost): запускает бота «Твоя жизнь».
Файлы life_bot.py и life_engine.py должны лежать рядом.
Токен берётся из переменной окружения BOT_TOKEN (или впиши его в life_bot.py)."""
import asyncio
from life_bot import main

if __name__ == "__main__":
    asyncio.run(main())
