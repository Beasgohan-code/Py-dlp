"""Rate limiting and bandwidth throttling utilities for Py-dlp."""

from __future__ import annotations

import re
import time
from typing import Optional


def parse_rate_limit(rate_str: Optional[str | int | float]) -> Optional[float]:
    """Parse a rate limit string (e.g. '500K', '2.5M', '10MB/s', '1024000') into bytes per second."""
    if rate_str is None:
        return None

    if isinstance(rate_str, (int, float)):
        return float(rate_str) if rate_str > 0 else None

    rate_str = str(rate_str).strip()
    if not rate_str:
        return None

    # Remove '/s' or '/sec' if present
    rate_str = re.sub(r"/(?:s|sec)$", "", rate_str, flags=re.IGNORECASE).strip()

    match = re.match(r"^([0-9.]+)\s*([KMGTkmgt]?(?:i?B)?)$", rate_str, re.IGNORECASE)
    if not match:
        try:
            val = float(rate_str)
            return val if val > 0 else None
        except ValueError:
            return None

    val_num = float(match.group(1))
    unit = match.group(2).upper()

    multipliers = {
        "": 1,
        "B": 1,
        "K": 1024,
        "KB": 1024,
        "KIB": 1024,
        "M": 1024 * 1024,
        "MB": 1024 * 1024,
        "MIB": 1024 * 1024,
        "G": 1024 * 1024 * 1024,
        "GB": 1024 * 1024 * 1024,
        "GIB": 1024 * 1024 * 1024,
        "T": 1024 * 1024 * 1024 * 1024,
        "TB": 1024 * 1024 * 1024 * 1024,
        "TIB": 1024 * 1024 * 1024 * 1024,
    }

    multiplier = multipliers.get(unit, 1)
    bytes_per_sec = val_num * multiplier
    return bytes_per_sec if bytes_per_sec > 0 else None


class RateLimiter:
    """Token-bucket rate limiter with smooth sleep pacing."""

    def __init__(self, bytes_per_second: Optional[float] = None):
        self.bytes_per_second = bytes_per_second
        self.last_check = time.monotonic()
        self.bucket = float(bytes_per_second) if bytes_per_second else float("inf")
        self.capacity = float(bytes_per_second) if bytes_per_second else float("inf")

    def set_rate(self, bytes_per_second: Optional[float]) -> None:
        self.bytes_per_second = bytes_per_second
        self.bucket = float(bytes_per_second) if bytes_per_second else float("inf")
        self.capacity = float(bytes_per_second) if bytes_per_second else float("inf")
        self.last_check = time.monotonic()

    def throttle(self, bytes_transferred: int) -> None:
        """Throttle execution to maintain the configured bytes/sec limit."""
        if not self.bytes_per_second or self.bytes_per_second <= 0:
            return

        now = time.monotonic()
        elapsed = now - self.last_check
        self.last_check = now

        # Add new tokens based on elapsed time
        self.bucket = min(self.capacity, self.bucket + elapsed * self.bytes_per_second)

        # Consume tokens
        self.bucket -= bytes_transferred

        # If bucket is in deficit, sleep until it reaches zero
        if self.bucket < 0:
            sleep_time = -self.bucket / self.bytes_per_second
            if sleep_time > 0.001:
                time.sleep(sleep_time)
                self.last_check = time.monotonic()
                self.bucket = 0.0
