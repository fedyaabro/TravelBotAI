import openai
import urllib.parse
import requests
from aiogram import Router, types
from magic_filter import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.config import OPENAI_API_KEY
from utils.yandex_api import get_yandex_image_api  # Подключаем API Яндекса

router = Router()

# Подключаем OpenAI
openai.api_key = OPENAI_API_KEY

# Определяем состояние FSM
class CountryInfoState(StatesGroup):
    waiting_for_country = State()

def is_image_accessible(url):
    """Проверяет, доступно ли изображение"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# 📌 Обработчик кнопки "🌍 Узнать о стране"
@router.message(F.text == "🗺 Узнать о стране/городе")
async def ask_country(message: types.Message, state: FSMContext):
    await message.answer("Введите название страны или города, о которой/ом хотите узнать:")
    await state.set_state(CountryInfoState.waiting_for_country)

# 📌 Обрабатываем ввод страны и отправляем информацию + фото
@router.message(CountryInfoState.waiting_for_country)
async def get_country_info(message: types.Message, state: FSMContext):
    country = message.text.strip()

    await message.answer(f"🔍 Ищу информацию о **{country}**...")

    # Генерируем ответ через OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты - эксперт по странам. Расскажи кратко об этой стране: столица, население, язык, интересные факты, валюта."},
                {"role": "user", "content": f"Расскажи кратко о стране {country}."}
            ]
        )

        answer = response["choices"][0]["message"]["content"]

        # Запрашиваем 3 изображения через API Яндекса
        image_urls = []
        for _ in range(3):  # Запросим три разных картинки
            img_url = get_yandex_image_api(country, "")
            if img_url and img_url not in image_urls and is_image_accessible(img_url):
                image_urls.append(img_url)

        # Отправляем информацию и фото
        if image_urls:
            media_group = [types.InputMediaPhoto(media=url) for url in image_urls]
            media_group[0].caption = answer  # Первое фото с текстом
            await message.answer_media_group(media=media_group)
        else:
            print(f"⚠ Telegram не смог загрузить изображения, отправляем ссылки")
            await message.answer(f"{answer}\n\n🌍 [Посмотреть изображения](https://yandex.com/images/search?text={urllib.parse.quote(country)})", parse_mode="Markdown")

    except Exception as e:
        print(f"⚠ Ошибка OpenAI: {e}")
        await message.answer("⚠ Не удалось получить информацию. Попробуйте позже.")

    # Завершаем состояние
    await state.clear()
