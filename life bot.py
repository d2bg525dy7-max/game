"""Telegram-бот «Твоя жизнь». Рядом должен лежать life_engine.py.
Запуск:  pip install aiogram   |   BOT_TOKEN=... python life_bot.py"""
import asyncio, json, os
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import life_engine as L

def load_env(path=".env"):
    """Читает .env рядом с ботом (без доп. библиотек)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()
TOKEN = os.getenv("BOT_TOKEN", "ВСТАВЬ_ТОКЕН")
SAVE = "life_save.json"
users = {}

def load():
    global users
    if os.path.exists(SAVE):
        users = json.load(open(SAVE, encoding="utf-8"))

def save():
    json.dump(users, open(SAVE, "w", encoding="utf-8"), ensure_ascii=False)

def markup(rows):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=d) for t, d in row] for row in rows])

dp = Dispatcher()

@dp.message(CommandStart())
@dp.message(Command("new"))
async def start(m: Message):
    users.pop(str(m.from_user.id), None); save()
    text, rows = L.city_menu()
    await m.answer(text, reply_markup=markup(rows))

@dp.message(Command("continue"))
async def cont(m: Message):
    u = users.get(str(m.from_user.id))
    if not u:
        text, rows = L.city_menu()
    else:
        text, rows = L.event_screen(u) if u["ev"] else L.hub(u)
    await m.answer(text, reply_markup=markup(rows))

@dp.callback_query()
async def on_click(cb: CallbackQuery):
    uid, data = str(cb.from_user.id), cb.data
    if data == "again":
        users.pop(uid, None); text, rows = L.city_menu()
    elif data.startswith("city:"):
        u = L.new_game(data[5:], cb.from_user.first_name or "Игрок")
        users[uid] = u; text, rows = L.intro(u)
    else:
        u = users.get(uid)
        if not u:
            text, rows = L.city_menu()
        else:
            text, rows = L.handle(u, data)
    save()
    try:
        await cb.message.edit_text(text, reply_markup=markup(rows))
    except Exception:
        pass  # «сообщение не изменилось» и т.п.
    await cb.answer()

async def main():
    load()
    await dp.start_polling(Bot(TOKEN))

if __name__ == "__main__":
    asyncio.run(main())
