import logging
from aiogram import Router, types
from magic_filter import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.scraper import search_flights  # Импорт парсера

router = Router()

class TicketSearchState(StatesGroup):
    waiting_for_origin = State()
    waiting_for_destination = State()
    waiting_for_departure_date = State()
    waiting_for_return_date = State()

# 📌 Обработчик кнопки "✈ Купить билеты"
@router.message(F.text == "✈ Купить билеты")
async def ask_origin(message: types.Message, state: FSMContext):
    await message.answer("🛫 Введите город вылета (например: Москва):")
    await state.set_state(TicketSearchState.waiting_for_origin)

# 📌 Получаем город вылета
@router.message(TicketSearchState.waiting_for_origin)
async def get_origin(message: types.Message, state: FSMContext):
    await state.update_data(origin=message.text)
    await message.answer("✈ Введите страну (или город) прилёта (например: Лондон):")
    await state.set_state(TicketSearchState.waiting_for_destination)

# 📌 Получаем страну прилёта
@router.message(TicketSearchState.waiting_for_destination)
async def get_destination(message: types.Message, state: FSMContext):
    await state.update_data(destination=message.text)
    await message.answer("📅 Введите дату вылета в формате **ДД-ММ-ГГГГ** (например: 23-06-2025):")
    await state.set_state(TicketSearchState.waiting_for_departure_date)

# 📌 Получаем дату вылета
@router.message(TicketSearchState.waiting_for_departure_date)
async def get_departure_date(message: types.Message, state: FSMContext):
    await state.update_data(departure_date=message.text)
    await message.answer("📅 Введите дату обратного рейса в формате **ДД-ММ-ГГГГ** (или 'нет', если в один конец):")
    await state.set_state(TicketSearchState.waiting_for_return_date)

# 📌 Получаем дату обратного рейса и даём ссылки
@router.message(TicketSearchState.waiting_for_return_date)
async def get_return_date(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    origin = user_data['origin']
    destination = user_data['destination']
    departure_date = user_data['departure_date']
    return_date = message.text if message.text.lower() != "нет" else None

    await message.answer(f"🔍 Ищу билеты из **{origin}** в **{destination}**\n"
                         f"📅 Дата вылета: {departure_date}\n"
                         f"📅 Дата возврата: {return_date if return_date else 'Без обратного билета'}")

    # Парсим ссылки на билеты
    flight_links = search_flights(origin, destination, departure_date, return_date)

    result = (
        f"✅ Найдено!\n"
        f"[🛫 Aviasales]({flight_links['Aviasales']})\n"
        f"[🛩 OneTwoTrip]({flight_links['OneTwoTrip']})"
    )

    await message.answer(result, parse_mode="Markdown", disable_web_page_preview=True)

    # Завершаем состояние
    await state.clear()
