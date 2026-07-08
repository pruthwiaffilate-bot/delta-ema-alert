"""Utility helpers: retry decorator and helpers."""
from __future__ import annotations

import time
import functools
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable[..., object])


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Simple retry decorator with exponential backoff.

    Args:
        max_attempts: max attempts
        delay: initial delay
        backoff: multiplicative backoff
    """

    def deco(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001 - broad retry is intentional
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper  # type: ignore[return-value]

    return deco
