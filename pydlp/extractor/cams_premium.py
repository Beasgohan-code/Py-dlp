"""Live Cam and Creator Platform Extractors for Py-dlp.

Supports:
- Stripchat (stripchat.com)
- Bongacams (bongacams.com)
- Cam4 (cam4.com)
- MyFreeCams (myfreecams.com)
- LiveJasmin (livejasmin.com)
- OnlyFans Demo/Public (onlyfans.com)
- Fansly Demo/Public (fansly.com)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class StripchatIE(InfoExtractor):
    """Stripchat live stream extractor."""

    IE_NAME = "stripchat"
    IE_DESC = "Stripchat Live Model Streams"
    _VALID_URL = r"https?://(?:www\.)?stripchat\.com/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        model = self._match_id(url)
        webpage = self._download_webpage(url, video_id=model, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Stripchat Live - {model}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        formats = [
            MediaFormat(
                format_id="hls-live",
                url=f"https://b-hls-01.stripcdn.com/hls/{model}/master.m3u8",
                ext="mp4",
                protocol="m3u8_native",
                is_live=True,
                format_note="Stripchat Live HLS",
            )
        ]

        return MediaInfo(
            id=model,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=formats,
            thumbnail=thumbnail,
            is_live=True,
        )


class BongacamsIE(InfoExtractor):
    """Bongacams live stream extractor."""

    IE_NAME = "bongacams"
    IE_DESC = "Bongacams Live Model Streams"
    _VALID_URL = r"https?://(?:[a-z]{2}\.)?bongacams\.com/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        model = self._match_id(url)
        webpage = self._download_webpage(url, video_id=model, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Bongacams Live - {model}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=model,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="bonga-live",
                    url=f"https://stream.bcvcdn.com/live/{model}/playlist.m3u8",
                    ext="mp4",
                    protocol="m3u8_native",
                    is_live=True,
                )
            ],
            thumbnail=thumbnail,
            is_live=True,
        )


class Cam4IE(InfoExtractor):
    """Cam4 live stream extractor."""

    IE_NAME = "cam4"
    IE_DESC = "Cam4 Live Video Streams"
    _VALID_URL = r"https?://(?:www\.)?cam4\.com/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        model = self._match_id(url)
        webpage = self._download_webpage(url, video_id=model, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Cam4 Live - {model}")

        return MediaInfo(
            id=model,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="cam4-live",
                    url=f"https://video.cam4.com/live/{model}/playlist.m3u8",
                    ext="mp4",
                    protocol="m3u8_native",
                    is_live=True,
                )
            ],
            is_live=True,
        )


class MyFreeCamsIE(InfoExtractor):
    """MyFreeCams live model stream extractor."""

    IE_NAME = "myfreecams"
    IE_DESC = "MyFreeCams (MFC) Live Streaming"
    _VALID_URL = r"https?://(?:www\.)?myfreecams\.com/#(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        model = self._match_id(url)
        return MediaInfo(
            id=model,
            title=f"MyFreeCams - {model}",
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="mfc-live",
                    url=f"https://video.myfreecams.com/hls/{model}/master.m3u8",
                    ext="mp4",
                    protocol="m3u8_native",
                    is_live=True,
                )
            ],
            is_live=True,
        )


class LiveJasminIE(InfoExtractor):
    """LiveJasmin webcam stream extractor."""

    IE_NAME = "livejasmin"
    IE_DESC = "LiveJasmin Live Cam Network"
    _VALID_URL = r"https?://(?:www\.)?livejasmin\.com/(?:[a-z]{2}/)?(?:member/)?(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        model = self._match_id(url)
        return MediaInfo(
            id=model,
            title=f"LiveJasmin - {model}",
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="jasmin-live",
                    url=f"https://ps.livejasmin.com/hls/{model}/index.m3u8",
                    ext="mp4",
                    protocol="m3u8_native",
                    is_live=True,
                )
            ],
            is_live=True,
        )


class OnlyFansDemoIE(InfoExtractor):
    """OnlyFans public post/video extractor."""

    IE_NAME = "onlyfans"
    IE_DESC = "OnlyFans Public Posts & Clips"
    _VALID_URL = r"https?://(?:www\.)?onlyfans\.com/(?P<id>[0-9]+)/[a-zA-Z0-9_-]+"

    def _real_extract(self, url: str) -> MediaInfo:
        post_id = self._match_id(url)
        return MediaInfo(
            id=post_id,
            title=f"OnlyFans Media Post {post_id}",
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="of-original",
                    url=url,
                    ext="mp4",
                    format_note="OnlyFans Source Media",
                )
            ],
        )


class FanslyDemoIE(InfoExtractor):
    """Fansly public post/clip extractor."""

    IE_NAME = "fansly"
    IE_DESC = "Fansly Public Posts & Videos"
    _VALID_URL = r"https?://(?:www\.)?fansly\.com/post/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        post_id = self._match_id(url)
        return MediaInfo(
            id=post_id,
            title=f"Fansly Post {post_id}",
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="fansly-media",
                    url=url,
                    ext="mp4",
                    format_note="Fansly Source Media",
                )
            ],
        )
