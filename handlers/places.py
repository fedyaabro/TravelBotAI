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
class PlacesState(StatesGroup):
    waiting_for_city = State()

def generate_google_maps_link(place_name, city):
    """Генерирует ссылку на Google Maps для конкретного места"""
    query = f"{place_name}, {city}"
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

def is_image_accessible(url):
    """Проверяет, доступно ли изображение"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# 📌 Обработчик кнопки "📍 Что посмотреть"
@router.message(F.text == "📍 Что посмотреть")
async def ask_city(message: types.Message, state: FSMContext):
    await message.answer("🏙 Введите название города, в котором хотите найти достопримечательности:")
    await state.set_state(PlacesState.waiting_for_city)

# 📌 Обрабатываем ввод города и даём рекомендации с точным поиском фото
@router.message(PlacesState.waiting_for_city)
async def get_places(message: types.Message, state: FSMContext):
    city = message.text.strip()

    await message.answer(f"🔍 Ищу достопримечательности в **{city}**...")

    # Генерируем ответ через OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты - туристический гид. Составь список 5 лучших достопримечательностей в указанном городе. "
                                              "Для каждой достопримечательности напиши её название и краткое описание."},
                {"role": "user", "content": f"Расскажи о главных достопримечательностях в {city}."}
            ]
        )

        answer = response["choices"][0]["message"]["content"]

        # Обрабатываем список достопримечательностей
        places = answer.split("\n")
        for place in places:
            if place.strip():
                place_name = place.split("**")[1] if "**" in place else place  # Извлекаем название
                google_maps_link = generate_google_maps_link(place_name, city)
                image_url = get_yandex_image_api(place_name, city)  # Точный запрос в API Яндекса

                if image_url and is_image_accessible(image_url):
                    print(f"📸 Отправка изображения: {image_url}")  # Логируем в консоль
                    await message.answer_photo(
                        photo=image_url,
                        caption=f"{place}\n\n📍 [Google Maps]({google_maps_link})",
                        parse_mode="Markdown", disable_web_page_preview=True
                    )
                else:
                    print(f"⚠ Telegram не смог загрузить изображение, отправляем ссылку: {image_url}")
                    await message.answer(
                        f"{place}\n\n📍 [Google Maps]({google_maps_link})\n🌍 [Посмотреть изображение]({image_url})",
                        parse_mode="Markdown"
                    )

    except Exception as e:
        print(f"⚠ Ошибка OpenAI: {e}")
        await message.answer("⚠ Не удалось получить информацию. Попробуйте позже.")

    # Завершаем состояние
    await state.clear()
