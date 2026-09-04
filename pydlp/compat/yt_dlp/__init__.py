"""yt-dlp compatibility namespace."""

from pydlp.compat.yt_dlp.extractor.common import InfoExtractor
from pydlp.compat.yt_dlp.utils import ExtractorError

__all__ = ["InfoExtractor", "ExtractorError"]
