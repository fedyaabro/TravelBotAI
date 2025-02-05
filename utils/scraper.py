import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Базовые URL поисковых систем
BASE_URLS = {
    "aviasales": "https://www.aviasales.ru/search/",
    "onetwotrip": "https://www.onetwotrip.com/ru/f/search/"
}

# Список городов и их IATA-кодов
IATA_CODES = {
    "москва": "MOW",
    "санкт-петербург": "LED",
    "калининград": "KGD",
    "новосибирск": "OVB",
    "екатеринбург": "SVX",
    "казань": "KZN",
    "сочи": "AER",
    "париж": "CDG",
    "лондон": "LON",
    "нью-йорк": "JFK",
    "дубай": "DXB",
    "стамбул": "IST",
    "рим": "FCO",
    "пхукет": "HKT",
}

def get_iata_code(city: str) -> str:
    """Преобразует название города в IATA-код (если есть в базе)"""
    city = city.lower().strip()
    return IATA_CODES.get(city, "MOW")  # Если город не найден, ставим MOW (Москва)

def format_date(date_str: str) -> str:
    """Преобразует дату из ДД-ММ-ГГГГ в формат ДДММ (без года)"""
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")  # Теперь ждём формат ДД-ММ-ГГГГ
        return date_obj.strftime("%d%m")  # ДДММ
    except ValueError:
        return "0000"

def search_flights(origin: str, destination: str, departure_date: str, return_date: str = None):
    """
    Генерирует ссылки для поиска билетов на Aviasales и OneTwoTrip.
    """
    origin_code = get_iata_code(origin)
    destination_code = get_iata_code(destination)
    departure_date_formatted = format_date(departure_date)

    # Aviasales
    search_code = f"{origin_code}{departure_date_formatted}{destination_code}"
    if return_date:
        return_date_formatted = format_date(return_date)
        search_code += f"{return_date_formatted}"
    aviasales_url = f"{BASE_URLS['aviasales']}{search_code}1"

    # OneTwoTrip (2202LEDKGD2602)
    if return_date:
        return_date_formatted = format_date(return_date)
        onetwotrip_code = f"{departure_date_formatted}{origin_code}{destination_code}{return_date_formatted}"
    else:
        onetwotrip_code = f"{departure_date_formatted}{origin_code}{destination_code}"

    onetwotrip_url = f"{BASE_URLS['onetwotrip']}{onetwotrip_code}"

    return {
        "Aviasales": aviasales_url,
        "OneTwoTrip": onetwotrip_url
    }
