from functools import wraps
from time import sleep

from retry import retry

from utils.logger import get_logger

logger = get_logger(__name__)


def backoff(exceptions: tuple, start_sleep_time: float = 0.1, factor: int = 2, border_sleep_time: int = 10):
    @retry(exceptions, delay=1)
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            n = 1

            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.info("An error %s occurred while executing the function %s", e, func.__name__)

                    if sleep_time >= border_sleep_time:
                        sleep_time = border_sleep_time
                    else:
                        sleep_time = min(sleep_time * (factor**n), border_sleep_time)
                    n += 1
                    sleep(sleep_time)

        return inner

    return func_wrapper
