"""Правила предобработки: превращают сырые данные в флаги."""

# Пороги (можно менять в одном месте)
COLD_TEMPERATURE_C = 0.0
FROST_TEMPERATURE_C = -10.0
EXPENSIVE_RATE = 100.0


def add_warm_clothes_flag(temp_c: float) -> bool:
    """
    True, если температура ниже 0 — нужна тёплая одежда.
    """
    return temp_c < COLD_TEMPERATURE_C


def add_frost_flag(temp_c: float) -> bool:
    """
    True, если температура ниже -10 — сильный мороз.
    """
    return temp_c < FROST_TEMPERATURE_C


def add_expensive_flag(rate: float) -> bool:
    """
    True, если курс выше 100 — дорогой курс.
    """
    return rate > EXPENSIVE_RATE


def normalize_description(description: str | None) -> str:
    """
    Приводит описание погоды к непустой строке.
    Если пусто/None — возвращает 'unknown'.
    """
    if not description:
        return "unknown"
    return description.strip() or "unknown"
