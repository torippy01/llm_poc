import time
from typing import Callable, Any


def time_measurement(func: Callable, val: Any) -> Any:
    start = time.time()
    response = func(**val)
    elapsed_time = time.time() - start
    return response, elapsed_time
