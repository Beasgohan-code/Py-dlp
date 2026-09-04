"""Downloader subsystem for Py-dlp."""

from pydlp.downloader.base import BaseDownloader
from pydlp.downloader.dash import DashDownloader
from pydlp.downloader.direct import get_downloader
from pydlp.downloader.hls import HlsDownloader
from pydlp.downloader.http import HttpDownloader
from pydlp.downloader.multisegment import MultiSegmentDownloader

__all__ = [
    "BaseDownloader",
    "HttpDownloader",
    "MultiSegmentDownloader",
    "HlsDownloader",
    "DashDownloader",
    "get_downloader",
]
