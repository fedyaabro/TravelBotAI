import urllib.parse

YANDEX_URL = "https://yandex.ru/images/search"

def get_image_from_yandex(place_name, city):
    """Генерирует ссылку на поиск изображений в Яндекс.Картинках"""
    query = f"{place_name} {city} достопримечательность Россия"
    encoded_query = urllib.parse.quote(query)
    return f"{YANDEX_URL}?text={encoded_query}"


