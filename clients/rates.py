"""Клиент курсов валют через Frankfurter (без API-ключа)."""

import logging

from clients.exceptions import (
    CurrencyNotFoundError,
    InvalidResponseError,
)
from clients.http import get

logger = logging.getLogger(__name__)

BASE_URL = "https://api.frankfurter.dev/v2/rate"


def get_rate(currency: str) -> float:
    """
    Возвращает курс currency → RUB.

    Например, для currency="USD" вернёт что-то вроде 84.84.

    Бросает:
        CurrencyNotFoundError — если код валюты не найден.
        InvalidResponseError — если ответ не соответствует ожиданиям.
    """
    currency = currency.upper()

    response = get(f"{BASE_URL}/{currency}/RUB")

    if response.status_code in (404, 422):
        raise CurrencyNotFoundError(f"Код валюты {currency!r} не найден")

    if response.status_code != 200:
        raise InvalidResponseError(f"Сервис курсов вернул {response.status_code}")

    try:
        data = response.json()
    except ValueError as exc:
        raise InvalidResponseError("Сервис курсов вернул не-JSON ответ") from exc

    try:
        rate = float(data["rate"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidResponseError("В ответе сервиса курсов нет поля rate") from exc

    logger.info("rate %s -> RUB = %s", currency, rate)
    return rate
