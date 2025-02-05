import openai
from aiogram import Router, types
from magic_filter import F  # Импортируем F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.config import OPENAI_API_KEY

# Создаём роутер
router = Router()

# Подключаем API-ключ OpenAI
openai.api_key = OPENAI_API_KEY

# Определяем состояния (FSM)
class CountryInfoState(StatesGroup):
    waiting_for_country = State()

# 📌 Обработчик кнопки "🗺 Узнать о стране"
# Список стран, где туризм может быть опасен
DANGEROUS_COUNTRIES = [
    "Афганистан", "Сомали", "Сирия", "Йемен", "Судан", "ЦАР",
    "Ливия", "Ирак", "Пакистан", "Северная Корея", "Мали",
    "Конго", "Нигер", "Южный Судан", "Венесуэла"
]

@router.message(F.text == "🗺 Узнать о стране")
async def ask_country(message: types.Message, state: FSMContext):
    await message.answer("Введите название страны, о которой хотите узнать:")
    await state.set_state(CountryInfoState.waiting_for_country)

# 📌 Обработчик ответа пользователя (ожидание ввода страны)
@router.message(CountryInfoState.waiting_for_country)
async def get_country_info(message: types.Message, state: FSMContext):
    country = message.text.strip()  # Получаем название страны

    # Проверяем, есть ли страна в списке опасных
    warning = ""
    if country in DANGEROUS_COUNTRIES:
        warning = ("⚠ *Внимание!* Эта страна может быть опасна для туризма. "
                   "Перед поездкой проверьте рекомендации МИД и будьте осторожны.\n\n")

    await message.answer(f"🔍 Ищу информацию о {country}...")

    # Генерируем ответ через OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты - туристический гид. Расскажи про страну кратко, но интересно."},
                {"role": "user", "content": f"Расскажи мне о {country}: достопримечательности, культура, кухня."}
            ]
        )

        answer = response["choices"][0]["message"]["content"]
        await message.answer(f"{warning}🌍 {country}:\n\n{answer}", parse_mode="Markdown")

    except Exception as e:
        await message.answer("⚠ Произошла ошибка при получении информации. Попробуйте позже.")
        print(f"Ошибка OpenAI: {e}")

    # Завершаем состояние (бот больше не ожидает ввод)
    await state.clear()

