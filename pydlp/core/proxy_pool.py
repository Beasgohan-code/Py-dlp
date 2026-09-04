"""Dynamic Proxy Pool & Auto-Rotator for Py-dlp."""

from __future__ import annotations

import logging
import os
import random
from typing import Dict, List, Optional

logger = logging.getLogger("pydlp.proxy_pool")


class ProxyPool:
    """Manages dynamic proxy list rotation and error failover."""

    def __init__(self, proxies: Optional[List[str] | str] = None, mode: str = "round-robin"):
        self.proxies: List[str] = []
        self.mode = mode.lower()  # 'round-robin' or 'random'
        self._current_index = 0
        self._failure_counts: Dict[str, int] = {}

        if proxies:
            if isinstance(proxies, str):
                if os.path.exists(proxies):
                    self.load_from_file(proxies)
                else:
                    self.proxies = [p.strip() for p in proxies.split(",") if p.strip()]
            elif isinstance(proxies, list):
                self.proxies = list(proxies)

    def load_from_file(self, filepath: str) -> None:
        """Load proxies from a plain text file (one per line)."""
        if not os.path.isfile(filepath):
            return
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    self.proxies.append(line)

    def add_proxy(self, proxy: str) -> None:
        p = proxy.strip()
        if p and p not in self.proxies:
            self.proxies.append(p)

    def get_proxy(self) -> Optional[str]:
        """Get next available active proxy."""
        if not self.proxies:
            return None

        # Filter out proxies with > 5 consecutive failures
        active = [p for p in self.proxies if self._failure_counts.get(p, 0) < 5]
        if not active:
            # Reset failures if all failed
            self._failure_counts.clear()
            active = list(self.proxies)

        if self.mode == "random":
            return random.choice(active)

        # Round-robin
        self._current_index = (self._current_index) % len(active)
        chosen = active[self._current_index]
        self._current_index = (self._current_index + 1) % len(active)
        return chosen

    def report_failure(self, proxy: str) -> None:
        """Record failure for a proxy."""
        self._failure_counts[proxy] = self._failure_counts.get(proxy, 0) + 1
        logger.debug(f"[proxy_pool] Proxy {proxy} failure count: {self._failure_counts[proxy]}")

    def report_success(self, proxy: str) -> None:
        """Record success for a proxy."""
        if proxy in self._failure_counts:
            self._failure_counts[proxy] = 0
