import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage  # Добавляем поддержку FSM
from handlers import info  # Импорт обработчика информации о странах
from utils.config import TOKEN  # Файл с токеном бота
from handlers import tickets  # Добавляем поиск билетов
from handlers import places  # Импортируем обработчик достопримечательностей




# Включаем логирование для отладки
logging.basicConfig(level=logging.INFO)

# Создаём объект бота и диспетчер с хранилищем состояний
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ⚡ Главное меню бота
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗺 Узнать о стране/городе")],
        [KeyboardButton(text="✈ Купить билеты")],
        [KeyboardButton(text="📍 Что посмотреть")]
    ],
    resize_keyboard=True
)

# 🎯 Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я твой помощник в путешествиях. 🌍\n"
        "Выбери, что тебя интересует:",
        reply_markup=main_menu
    )

# ✅ Регистрируем обработчики
dp.include_router(info.router)
dp.include_router(tickets.router)  # Подключаем обработчики
dp.include_router(places.router)  # Подключаем обработчик
# 🚀 Запуск бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

