import openai
from aiogram import Router, types
from magic_filter import F
from utils.config import OPENAI_API_KEY

# Создаём роутер для обработки сообщений
router = Router()

# Подключаем API-ключ OpenAI
openai.api_key = OPENAI_API_KEY


# 📌 Обработчик нажатия кнопки "🗺 Узнать о стране"
@router.message(F("🗺 Узнать о стране"))
async def ask_country(message: types.Message):
    await message.answer("Введите название страны, о которой хотите узнать:")


# 📌 Обработчик ввода страны
@router.message()
async def get_country_info(message: types.Message):
    country = message.text.strip()  # Получаем название страны от пользователя

    # Генерируем ответ через OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты - туристический гид. Расскажи про страну кратко, но интересно."},
            {"role": "user", "content": f"Расскажи мне о {country}: достопримечательности, культура, кухня."}
        ]
    )

    answer = response["choices"][0]["message"]["content"]

    await message.answer(f"🌍 {country}:\n\n{answer}")

