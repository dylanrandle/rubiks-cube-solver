import time


def timer(func):
    def wrapped(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        runtime_ms = 100 * (end - start)
        print(f"Function {func.__name__} executed in {runtime_ms:.4f}ms")

        return result

    return wrapped
