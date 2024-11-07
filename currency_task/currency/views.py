# currency/views.py
import requests
from django.core.cache import cache
from django.http import JsonResponse
from .models import CurrencyRequest
import logging


API_KEY = "cur_live_VP1AGn2Zxm0jde6pM5p7njW34mQjHlBN5NHxbupF"
API_URL = f"https://api.currencyapi.com/v3/latest?apikey={API_KEY}&currencies=RUB&base_currency=USD"
CACHE_TIMEOUT = 10  # Время кэша


def get_usd_to_rub():
    """
    Получение курса доллара из API
    """

    try:
        response = requests.get(API_URL)
        data = response.json()

        return data["data"]["RUB"]["value"]

    except Exception as error:
        logging.error(f'get_usd_to_rub(): {error}')
        raise ValueError('Ошибка при получении данных из API')


def get_current_usd(request):
    """
    Эндпоинт получения данных при запросе курса доллара
    """

    try:
        # Получение данных из кэша
        usd_to_rub = cache.get("usd_to_rub")

        # Запрос к API при остутствии кэша
        if usd_to_rub is None:
            usd_to_rub = get_usd_to_rub()

            # Добавление данных ответа в кэш
            cache.set("usd_to_rub", usd_to_rub, CACHE_TIMEOUT)

            # Сохранение в БД ответ запроса
            CurrencyRequest.objects.create(usd_to_rub=usd_to_rub)

        # Получение последних 10 запросов
        latest_requests = list(CurrencyRequest.objects.order_by("-timestamp")[:10].values())

        response_data = {
            "status": "success",
            "status_code": 200,
            "detail": None,
            "current_usd_to_rub": usd_to_rub,
            "latest_requests": latest_requests,
        }
        return JsonResponse(response_data)

    # Обработчик ошибок API
    except ValueError as error:
        response_data = {
            "status": "error",
            "status_code": 400,
            "detail": str(error),
            "current_usd_to_rub": None,
            "latest_requests": None,
        }
        return JsonResponse(response_data)

    # Обработчик прочих ошибок
    except Exception as error:
        response_data = {
            "status": "error",
            "status_code": 500,
            "detail": str(error),
            "current_usd_to_rub": None,
            "latest_requests": None,
        }
        return JsonResponse(response_data)