"""Local cache management for extractors, player keys, and sessions."""

from __future__ import annotations

import json
import os
import time
from typing import Any, Optional


class Cache:
    """Provides persistent caching for extractor signatures, tokens, and metadata."""

    def __init__(self, cache_dir: Optional[str] = None, enabled: bool = True):
        self.enabled = enabled
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
            self.cache_dir = os.path.join(base, "pydlp")

        if self.enabled:
            os.makedirs(self.cache_dir, exist_ok=True)

    def _get_path(self, section: str, key: str) -> str:
        safe_section = section.replace("/", "_").replace("\\", "_")
        safe_key = key.replace("/", "_").replace("\\", "_")
        return os.path.join(self.cache_dir, f"{safe_section}_{safe_key}.json")

    def get(self, section: str, key: str, default: Any = None) -> Any:
        if not self.enabled:
            return default
        path = self._get_path(section, key)
        if not os.path.isfile(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            expires_at = data.get("expires_at")
            if expires_at and expires_at < time.time():
                try:
                    os.remove(path)
                except OSError:
                    pass
                return default
            return data.get("value", default)
        except Exception:
            return default

    def set(self, section: str, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        if not self.enabled:
            return
        path = self._get_path(section, key)
        expires_at = (time.time() + ttl_seconds) if ttl_seconds else None
        data = {
            "value": value,
            "expires_at": expires_at,
            "saved_at": time.time(),
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass

    def delete(self, section: str, key: str) -> None:
        path = self._get_path(section, key)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass

    def clear(self) -> None:
        if not self.enabled or not os.path.isdir(self.cache_dir):
            return
        for fname in os.listdir(self.cache_dir):
            if fname.endswith(".json"):
                try:
                    os.remove(os.path.join(self.cache_dir, fname))
                except OSError:
                    pass
