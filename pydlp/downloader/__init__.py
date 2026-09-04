"""Downloader package exposing all Py-dlp download engines and the Universal All-Rounder."""

from pydlp.downloader.allrounder import AllRounderDownloader
from pydlp.downloader.base import BaseDownloader
from pydlp.downloader.dash import DashDownloader
from pydlp.downloader.direct import DirectDownloader
from pydlp.downloader.external import ExternalDownloader
from pydlp.downloader.hls import HlsDownloader, HLSDownloader
from pydlp.downloader.hls_live import HLSLiveDownloader
from pydlp.downloader.http import HttpDownloader
from pydlp.downloader.multisegment import MultiSegmentDownloader
from pydlp.downloader.resumable import ResumableDownloader
from pydlp.downloader.turbo import TurboDownloader
from pydlp.downloader.websocket import WebSocketDownloader

__all__ = [
    "BaseDownloader",
    "AllRounderDownloader",
    "DirectDownloader",
    "HttpDownloader",
    "ResumableDownloader",
    "TurboDownloader",
    "MultiSegmentDownloader",
    "HlsDownloader",
    "HLSDownloader",
    "HLSLiveDownloader",
    "DashDownloader",
    "ExternalDownloader",
    "WebSocketDownloader",
]
