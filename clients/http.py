"""Общий HTTP GET с timeout и retry."""

import logging
import random
import time

import requests

from clients.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

# Настройки по умолчанию
DEFAULT_TIMEOUT = (3, 7)  # (connect, read) — суммарно ≤ 10 с
MAX_ATTEMPTS = 3  # 1 попытка + 2 повтора
RETRYABLE_STATUS_CODES = {500, 502, 503, 504}


def _backoff_delay(attempt: int) -> float:
    """Exponential backoff с jitter: 1s, 2s, 4s + случайная добавка."""
    return 2 ** (attempt - 1) + random.uniform(0, 0.5)


def _retry_after_seconds(response: requests.Response) -> float | None:
    """Читает Retry-After из ответа (только числовой)."""
    value = response.headers.get("Retry-After")
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def get(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: tuple[int, int] = DEFAULT_TIMEOUT,
) -> requests.Response:
    """
    Выполняет GET с retry.

    Повторяет при:
      - requests.exceptions.Timeout
      - requests.exceptions.ConnectionError
      - 500/502/503/504
      - 429 (с учётом Retry-After)

    Бросает ExternalServiceError, если все попытки неудачны.
    """
    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
            )
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ) as exc:
            last_error = exc
            logger.warning(
                "attempt %s/%s failed url=%s error=%s",
                attempt,
                MAX_ATTEMPTS,
                url,
                type(exc).__name__,
            )
            if attempt == MAX_ATTEMPTS:
                break
            time.sleep(_backoff_delay(attempt))
            continue

        # 5xx — retry
        if response.status_code in RETRYABLE_STATUS_CODES:
            last_error = ExternalServiceError(f"Сервис вернул {response.status_code}")
            logger.warning(
                "attempt %s/%s got %s url=%s",
                attempt,
                MAX_ATTEMPTS,
                response.status_code,
                url,
            )
            if attempt == MAX_ATTEMPTS:
                break
            time.sleep(_backoff_delay(attempt))
            continue

        # 429 — retry с учётом Retry-After
        if response.status_code == 429:
            retry_after = _retry_after_seconds(response) or _backoff_delay(attempt)
            last_error = ExternalServiceError("Превышен rate limit (429)")
            logger.warning(
                "attempt %s/%s got 429 url=%s retry_after=%.1fs",
                attempt,
                MAX_ATTEMPTS,
                url,
                retry_after,
            )
            if attempt == MAX_ATTEMPTS:
                break
            time.sleep(retry_after)
            continue

        # Успех или 4xx — возвращаем как есть, разбираться будет вызывающий код
        return response

    raise ExternalServiceError(
        f"Не удалось получить ответ от {url} после {MAX_ATTEMPTS} попыток"
    ) from last_error
