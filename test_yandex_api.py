import requests
import urllib.parse
import xml.etree.ElementTree as ET
import urllib3
from utils.config import YANDEX_FOLDER_ID, YANDEX_API_KEY

# Отключаем SSL Warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Замените на свои данные
YANDEX_IMAGE_API_URL = "https://yandex.com/images-xml"
YANDEX_API_KEY = YANDEX_API_KEY
YANDEX_FOLDER_ID = YANDEX_FOLDER_ID

def test_yandex_image_api():
    """Тестируем API Яндекса – теперь берём изображение из <url> в <doc>"""
    query = "Кремль, Москва"  # Улучшенный запрос
    encoded_query = urllib.parse.quote(query)

    params = {
        "folderid": YANDEX_FOLDER_ID,
        "apikey": YANDEX_API_KEY,
        "text": query,
        "itype": "jpg,png",  # Запрашиваем только фото
        "isize": "large",  # Берём только большие картинки
        "iorient": "horizontal"  # Предпочитаем горизонтальные
    }

    # Логируем URL запроса
    full_url = f"{YANDEX_IMAGE_API_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    print(f"🔍 Тестовый запрос в API Яндекса: {full_url}")

    response = requests.get(YANDEX_IMAGE_API_URL, params=params, verify=False)

    if response.status_code != 200:
        print(f"⚠ Ошибка API Яндекса: {response.status_code} - {response.text}")
        return None

    print(f"📥 Полный ответ API Яндекса:\n{response.text}")

    try:
        # Разбираем XML-ответ
        root = ET.fromstring(response.text)

        for doc in root.findall(".//doc"):
            img_url_element = doc.find(".//url")  # Берём `<url>` внутри `<doc>`
            if img_url_element is not None:
                img_url = img_url_element.text

                # Проверяем, что это изображение (jpg, png)
                if img_url.endswith(".jpg") or img_url.endswith(".png"):
                    print(f"✅ Найдено изображение: {img_url}")
                    return img_url

        print("⚠ API не вернул подходящих изображений.")
        return None

    except ET.ParseError:
        print(f"⚠ Ошибка обработки XML-ответа Яндекса. Ответ API:\n{response.text}")
        return None

# Запускаем тест
if __name__ == "__main__":
    test_yandex_image_api()
