"""Plugin architecture and dynamic extension registry for Py-dlp."""

from __future__ import annotations

import importlib.util
import os
import sys
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type

if TYPE_CHECKING:
    from pydlp.downloader.base import BaseDownloader
    from pydlp.extractor.base import InfoExtractor
    from pydlp.postprocessor.base import BasePostProcessor

_CUSTOM_EXTRACTORS: List[Type[Any]] = []
_CUSTOM_DOWNLOADERS: Dict[str, Type[Any]] = {}
_CUSTOM_POSTPROCESSORS: List[Type[Any]] = []


def register_extractor(cls: Type[Any]) -> Type[Any]:
    """Decorator to register a custom extractor class into Py-dlp."""
    if cls not in _CUSTOM_EXTRACTORS:
        _CUSTOM_EXTRACTORS.insert(0, cls)
    return cls


def register_downloader(proto: str) -> Callable[[Type[Any]], Type[Any]]:
    """Decorator to register a custom downloader for a protocol."""
    def decorator(cls: Type[Any]) -> Type[Any]:
        _CUSTOM_DOWNLOADERS[proto.lower()] = cls
        return cls
    return decorator


def register_postprocessor(cls: Type[Any]) -> Type[Any]:
    """Decorator to register a custom post-processor."""
    if cls not in _CUSTOM_POSTPROCESSORS:
        _CUSTOM_POSTPROCESSORS.append(cls)
    return cls


def get_custom_extractors() -> List[Type[Any]]:
    return list(_CUSTOM_EXTRACTORS)


def get_custom_downloaders() -> Dict[str, Type[Any]]:
    return dict(_CUSTOM_DOWNLOADERS)


def get_custom_postprocessors() -> List[Type[Any]]:
    return list(_CUSTOM_POSTPROCESSORS)


def load_plugins_from_directory(dir_path: str) -> int:
    """Dynamically loads and registers all Python plugin modules from a directory."""
    if not os.path.isdir(dir_path):
        return 0

    count = 0
    for fname in os.listdir(dir_path):
        if fname.endswith(".py") and not fname.startswith("__"):
            fpath = os.path.join(dir_path, fname)
            mod_name = f"pydlp_plugin_{os.path.splitext(fname)[0]}"
            try:
                spec = importlib.util.spec_from_file_location(mod_name, fpath)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = mod
                    spec.loader.exec_module(mod)
                    count += 1
            except Exception:
                pass
    return count
