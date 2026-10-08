import time


def wait_for(predicate, timeout=10, interval=0.2):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if predicate():
            return

        time.sleep(interval)

    raise TimeoutError(
        f"Condition was not satisfied within {timeout} seconds"
    )
