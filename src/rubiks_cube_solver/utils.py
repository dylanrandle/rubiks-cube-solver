import logging
import time
from typing import Callable


def timer(func):
    def wrapped(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        runtime_ms = 1000 * (end - start)
        logging.debug(f"Function {func.__name__} executed in {runtime_ms:.4f}ms")

        return result

    return wrapped


def maybe_commit(callable: Callable):
    logging.info("Commit? (y/n)")
    response = input().strip().lower()
    if response == "y":
        callable()
    else:
        logging.info("Not saving results")
