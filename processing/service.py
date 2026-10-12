"""Сборка итоговой сводки по городу."""

import logging

from clients.rates import get_rate
from clients.weather import get_weather
from processing.preprocessing import (
    add_expensive_flag,
    add_frost_flag,
    add_warm_clothes_flag,
    normalize_description,
)

logger = logging.getLogger(__name__)


def build_city_summary(city: str, currency: str = "USD") -> dict:
    """
    Собирает сводку по городу: погода + курс валюты + флаги.

    Args:
        city: название города (например, "Moscow").
        currency: ISO-код валюты (по умолчанию "USD").

    Returns:
        dict с полями: city, weather, rates.
    """
    logger.info("building summary city=%s currency=%s", city, currency)

    # 1. Погода
    weather_data = get_weather(city)
    temp_c = weather_data["temp_c"]
    description = normalize_description(weather_data.get("description"))

    weather = {
        "temp_c": temp_c,
        "description": description,
        "warm_clothes": add_warm_clothes_flag(temp_c),
        "frost": add_frost_flag(temp_c),
    }

    # 2. Курс валюты
    rate = get_rate(currency)
    rates = {
        "currency": currency.upper(),
        "rate_to_rub": rate,
        "expensive": add_expensive_flag(rate),
    }

    summary = {
        "city": weather_data.get("city", city),
        "weather": weather,
        "rates": rates,
    }
    logger.info("summary built city=%s", summary["city"])
    return summary
