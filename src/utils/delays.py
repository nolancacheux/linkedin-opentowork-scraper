"""Human-like delay utilities."""

import random
import time
from ..config import config


def human_delay(min_sec: float = None, max_sec: float = None) -> None:
    """
    Wait for a random duration to simulate human behavior.

    Args:
        min_sec: Minimum delay in seconds (default: config.MIN_DELAY)
        max_sec: Maximum delay in seconds (default: config.MAX_DELAY)
    """
    min_sec = min_sec if min_sec is not None else config.MIN_DELAY
    max_sec = max_sec if max_sec is not None else config.MAX_DELAY
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def long_pause() -> None:
    """Take a longer pause to avoid detection."""
    base_duration = config.LONG_PAUSE_DURATION
    variation = random.uniform(-5, 10)
    duration = max(10, base_duration + variation)
    time.sleep(duration)


def scroll_pause() -> None:
    """Short pause after scrolling."""
    delay = random.uniform(config.SCROLL_PAUSE, config.SCROLL_PAUSE + 0.5)
    time.sleep(delay)
