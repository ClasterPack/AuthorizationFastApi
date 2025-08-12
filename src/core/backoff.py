import asyncio
import logging
import time
from functools import wraps

# Настройка логирования
logger = logging.getLogger(__name__)


def create_backoff_decorator(
    exceptions, is_async=False, start_sleep_time=0.1, factor=2, border_sleep_time=10
):
    """
    Универсальный backoff декоратор для синхронных и асинхронных функций.
    Повторяет выполнение функции с экспоненциальной задержкой, если произошла ошибка.

    Args:
        exceptions: Исключения, при которых будет выполняться повтор.
        is_async: Указывает, является ли функция асинхронной.
        start_sleep_time: Начальное время ожидания.
        factor: Во сколько раз нужно увеличивать время ожидания на каждой итерации.
        border_sleep_time: Максимальное время ожидания.
    """

    def decorator(func):
        if is_async:

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                attempt = 0
                delay = start_sleep_time
                while True:
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as err:
                        logger.error(
                            f"[Backoff] Попытка {attempt + 1} выполнить async-функцию '{func.__name__}' "
                            f"вызвала ошибку: {err}. Повтор через {delay:.2f} сек."
                        )
                        await asyncio.sleep(delay)
                        attempt += 1
                        delay = min(
                            start_sleep_time * (factor**attempt), border_sleep_time
                        )

        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                attempt = 0
                delay = start_sleep_time
                while True:
                    try:
                        return func(*args, **kwargs)
                    except exceptions as err:
                        logger.error(
                            f"[Backoff] Попытка {attempt + 1} выполнить функцию '{func.__name__}' "
                            f"вызвала ошибку: {err}. Повтор через {delay:.2f} сек."
                        )
                        time.sleep(delay)
                        attempt += 1
                        delay = min(
                            start_sleep_time * (factor**attempt), border_sleep_time
                        )

        return async_wrapper if is_async else sync_wrapper

    return decorator


def backoff(
    func=None,
    *,
    exceptions=(TransportError, ConnectionError, ConnectionTimeout),
    is_async=False,
    start_sleep_time=0.1,
    factor=2,
    border_sleep_time=10,
):
    """
    Декоратор, который автоматически применяет backoff стратегию для синхронных или асинхронных функций.

    Пример:
        @backoff(exceptions=(TransportError, ConnectionError), is_async=True)
        async def my_function():
            pass
    """
    if func is None:
        return lambda f: create_backoff_decorator(
            exceptions, is_async, start_sleep_time, factor, border_sleep_time
        )(f)
    else:
        return create_backoff_decorator(
            exceptions, is_async, start_sleep_time, factor, border_sleep_time
        )(func)


pg_backoff = create_backoff_decorator(
    exceptions=(Exception,),
    is_async=False,
    start_sleep_time=25,
    factor=5,
    border_sleep_time=1,
)
