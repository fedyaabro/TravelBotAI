import requests
import urllib.parse
import xml.etree.ElementTree as ET
import urllib3
from utils.config import YANDEX_API_KEY, YANDEX_FOLDER_ID

# Отключаем SSL Warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

YANDEX_IMAGE_API_URL = "https://yandex.com/images-xml"

def get_yandex_image_api(place_name, city):
    """Запрашивает фото достопримечательности через API Яндекса (только название и город)"""
    query = f"{place_name}, {city} + 'фото' "  # Без дополнительных слов

    params = {
        "folderid": YANDEX_FOLDER_ID,
        "apikey": YANDEX_API_KEY,
        "text": query,
        "itype": "jpg,png",
        "isize": "large",
        "iorient": "horizontal"
    }

    # Логируем запрос
    full_url = f"{YANDEX_IMAGE_API_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    print(f"🔍 Запрос к API Яндекса: {full_url}")

    response = requests.get(YANDEX_IMAGE_API_URL, params=params, verify=False)

    if response.status_code != 200:
        print(f"⚠ Ошибка API Яндекса: {response.status_code} - {response.text}")
        return None

    try:
        # Разбираем XML-ответ
        root = ET.fromstring(response.text)

        best_image = None
        best_size = 0

        for doc in root.findall(".//doc"):
            img_url_element = doc.find(".//url")
            image_link_element = doc.find(".//image-properties/image-link")

            # Используем `<url>`, если оно ведёт на изображение
            img_url = img_url_element.text if img_url_element is not None and (".jpg" in img_url_element.text or ".png" in img_url_element.text) else None
            img_link = image_link_element.text if image_link_element is not None else None

            final_img = img_url if img_url else img_link

            width = doc.find(".//image-properties/original-width")
            height = doc.find(".//image-properties/original-height")

            if final_img and width is not None and height is not None:
                img_width = int(width.text)
                img_height = int(height.text)
                img_size = img_width * img_height

                # Выбираем самое большое изображение
                if img_size > best_size:
                    best_image = final_img
                    best_size = img_size

        if best_image:
            print(f"✅ Выбрано изображение: {best_image}")
            return best_image

        print("⚠ API не вернул подходящих изображений.")
        return None

    except ET.ParseError:
        print(f"⚠ Ошибка обработки XML-ответа Яндекса. Ответ API:\n{response.text}")
        return None

