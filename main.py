"""CLI-точка входа: сводка по городу."""

import argparse
import logging
import sys

from clients.exceptions import (
    CityNotFoundError,
    CurrencyNotFoundError,
    ExternalServiceError,
    InvalidResponseError,
)
from processing.service import build_city_summary

# Коды выхода (по требованию ДЗ)
EXIT_OK = 0
EXIT_ARGS_ERROR = 2
EXIT_NOT_FOUND = 3
EXIT_SERVICE_UNAVAILABLE = 4


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Сводка по городу: погода и курс валюты к рублю.",
    )
    parser.add_argument(
        "--city",
        required=True,
        help="Название города (например, Moscow)",
    )
    parser.add_argument(
        "--currency",
        default="USD",
        help="ISO-код валюты (по умолчанию USD)",
    )
    return parser.parse_args(argv)


def format_summary(summary: dict) -> str:
    """Форматирует сводку для печати в консоль."""
    weather = summary["weather"]
    rates = summary["rates"]

    lines = [
        f"Город: {summary['city']}",
        f"Погода: {weather['temp_c']}°C, {weather['description']}",
        f"Тёплая одежда: {'да' if weather['warm_clothes'] else 'нет'}",
        f"{rates['currency']} – RUB: {rates['rate_to_rub']}",
        f"Дорогой курс: {'да' if rates['expensive'] else 'нет'}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Главная функция CLI. Возвращает код выхода."""
    logging.basicConfig(level=logging.INFO)

    args = parse_args(argv)
    city = args.city.strip()
    currency = args.currency.strip().upper()

    if not city:
        print("Ошибка: --city не может быть пустым", file=sys.stderr)
        return EXIT_ARGS_ERROR

    if not (len(currency) == 3 and currency.isalpha()):
        print(
            f"Ошибка: --currency должен быть ISO-кодом из 3 букв, получено {currency!r}",
            file=sys.stderr,
        )
        return EXIT_ARGS_ERROR

    try:
        summary = build_city_summary(city, currency)
    except (CityNotFoundError, CurrencyNotFoundError) as exc:
        print(f"Не найдено: {exc}", file=sys.stderr)
        return EXIT_NOT_FOUND
    except ExternalServiceError as exc:
        print(f"Внешний сервис недоступен: {exc}", file=sys.stderr)
        return EXIT_SERVICE_UNAVAILABLE
    except InvalidResponseError as exc:
        print(f"Некорректный ответ сервиса: {exc}", file=sys.stderr)
        return EXIT_SERVICE_UNAVAILABLE
    except RuntimeError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return EXIT_ARGS_ERROR

    print(format_summary(summary))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
