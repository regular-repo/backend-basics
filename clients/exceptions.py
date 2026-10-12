class ExternalServiceError(Exception):
    """Внешний сервис недоступен после всех попыток."""


class CityNotFoundError(Exception):
    """Город не найден в геокодере."""


class CurrencyNotFoundError(Exception):
    """Код валюты не найден в сервисе курсов."""


class InvalidResponseError(Exception):
    """Ответ внешнего сервиса не соответствует ожиданиям."""
