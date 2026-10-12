"""Клиент погоды через OpenWeatherMap."""

import logging
import os

from clients.exceptions import (
    CityNotFoundError,
    InvalidResponseError,
)
from clients.http import get

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str) -> dict:
    """
    Возвращает погоду для города:
        {
            "city": "Moscow",
            "temp_c": -3.2,
            "description": "ясно",
        }

    Бросает:
        CityNotFoundError — если город не найден.
        InvalidResponseError — если ответ не соответствует ожиданиям.
        RuntimeError — если не задана переменная WEATHER_API_KEY.
    """
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("Не задана переменная окружения WEATHER_API_KEY")

    response = get(
        BASE_URL,
        params={
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "ru",
        },
    )

    if response.status_code == 404:
        raise CityNotFoundError(f"Город {city!r} не найден")

    if response.status_code == 401:
        raise InvalidResponseError(
            "OpenWeatherMap вернул 401 — неверный или неактивный API-ключ"
        )

    if response.status_code != 200:
        raise InvalidResponseError(f"Сервис погоды вернул {response.status_code}")

    try:
        data = response.json()
    except ValueError as exc:
        raise InvalidResponseError("Сервис погоды вернул не-JSON ответ") from exc

    # Достаём температуру
    try:
        temp_c = float(data["main"]["temp"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidResponseError("В ответе погоды нет поля main.temp") from exc

    # Достаём описание
    try:
        description = str(data["weather"][0]["description"])
    except (KeyError, IndexError, TypeError) as exc:
        raise InvalidResponseError(
            "В ответе погоды нет поля weather[0].description"
        ) from exc

    # Название города, как его вернул сервис
    resolved_name = str(data.get("name") or city)

    logger.info("weather city=%s temp=%s desc=%s", resolved_name, temp_c, description)

    return {
        "city": resolved_name,
        "temp_c": temp_c,
        "description": description,
    }
