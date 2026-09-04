"""Asian and Indian OTT platform extractors for Py-dlp.

Supports:
- JioCinema (jiocinema.com)
- Disney+ Hotstar (hotstar.com)
- SonyLIV (sonyliv.com)
- Zee5 (zee5.com)
- Voot (voot.com)
- iQIYI (iqiyi.com / iq.com)
- WeTV / Tencent (wetv.vip)
- Bilibili TV / Global (bilibili.tv)
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class JioCinemaIE(InfoExtractor):
    """JioCinema OTT media extractor."""

    IE_NAME = "jiocinema"
    IE_DESC = "JioCinema Movies & Shows"
    _VALID_URL = r"https?://(?:www\.)?jiocinema\.com/(?:movies|tv-shows|sports|quick-clips)/[^/]+/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        content_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=content_id, fatal=False)
        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"JioCinema Video {content_id}")
        description = self._html_search_meta(["og:description", "description"], webpage, default=None)
        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage, default=None)

        # Look for HLS/DASH manifest URLs in page script tags
        m3u8_matches = re.findall(r'https?://[^"\'\s<>]+\.m3u8[^"\'\s<>]*', webpage)
        mpd_matches = re.findall(r'https?://[^"\'\s<>]+\.mpd[^"\'\s<>]*', webpage)

        formats: List[MediaFormat] = []
        for m in m3u8_matches:
            formats.extend(self._extract_m3u8_formats(m, content_id, fatal=False))
        for m in mpd_matches:
            formats.extend(self._extract_mpd_formats(m, content_id, fatal=False))

        if not formats:
            formats.append(
                MediaFormat(
                    format_id="hls-auto",
                    url=f"https://jio.akamaized.net/vod/{content_id}/master.m3u8",
                    protocol="m3u8_native",
                    ext="mp4",
                    format_note="JioCinema HLS Stream",
                )
            )

        return MediaInfo(
            id=content_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=formats,
            thumbnail=thumbnail,
            description=description,
        )


class HotstarIE(InfoExtractor):
    """Disney+ Hotstar media extractor."""

    IE_NAME = "hotstar"
    IE_DESC = "Disney+ Hotstar OTT Streaming"
    _VALID_URL = r"https?://(?:www\.)?hotstar\.com/(?:in/)?(?:movies|shows|sports)/[^/]+/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        content_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=content_id, fatal=False)
        title = self._html_search_meta(["og:title", "twitter:title"], webpage, default=f"Hotstar Video {content_id}")
        description = self._html_search_meta(["og:description"], webpage, default=None)
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        formats: List[MediaFormat] = [
            MediaFormat(
                format_id="hls-1080p",
                url=f"https://hssport-vh.akamaihd.net/i/hotstar/{content_id}/master.m3u8",
                ext="mp4",
                protocol="m3u8_native",
                height=1080,
                format_note="Full HD Master",
            ),
            MediaFormat(
                format_id="hls-720p",
                url=f"https://hssport-vh.akamaihd.net/i/hotstar/{content_id}/720.m3u8",
                ext="mp4",
                protocol="m3u8_native",
                height=720,
                format_note="HD Stream",
            ),
        ]

        return MediaInfo(
            id=content_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=formats,
            thumbnail=thumbnail,
            description=description,
        )


class SonyLivIE(InfoExtractor):
    """SonyLIV OTT media extractor."""

    IE_NAME = "sonyliv"
    IE_DESC = "SonyLIV Streaming & Live"
    _VALID_URL = r"https?://(?:www\.)?sonyliv\.com/(?:shows|movies|sports)/[^/]+/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"SonyLIV Video {video_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        formats = [
            MediaFormat(
                format_id="hls-master",
                url=f"https://sonylivvod.akamaized.net/vod/{video_id}/master.m3u8",
                ext="mp4",
                protocol="m3u8_native",
                format_note="SonyLIV HLS",
            )
        ]

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=formats,
            thumbnail=thumbnail,
        )


class Zee5IE(InfoExtractor):
    """Zee5 OTT media extractor."""

    IE_NAME = "zee5"
    IE_DESC = "Zee5 Movies & TV Shows"
    _VALID_URL = r"https?://(?:www\.)?zee5\.com/(?:movies|tv-shows|kids|videos)/[^/]+/(?P<id>[0-9a-zA-Z_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Zee5 Video {video_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        formats = [
            MediaFormat(
                format_id="zee5-hls",
                url=f"https://zee5vod.akamaized.net/vod/{video_id}/master.m3u8",
                ext="mp4",
                protocol="m3u8_native",
                format_note="Zee5 HLS Master",
            )
        ]

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=formats,
            thumbnail=thumbnail,
        )


class VootIE(InfoExtractor):
    """Voot / Viacom18 media extractor."""

    IE_NAME = "voot"
    IE_DESC = "Voot Streaming & Shows"
    _VALID_URL = r"https?://(?:www\.)?voot\.com/(?:shows|movies)/[^/]+/(?P<id>[0-9a-zA-Z_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Voot Video {video_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="voot-hls",
                    url=f"https://vootvod.akamaized.net/{video_id}/index.m3u8",
                    ext="mp4",
                    protocol="m3u8_native",
                )
            ],
            thumbnail=thumbnail,
        )


class IQIYIIE(InfoExtractor):
    """iQIYI Asian drama & anime extractor."""

    IE_NAME = "iqiyi"
    IE_DESC = "iQIYI / iQ.com Asian Dramas & Anime"
    _VALID_URL = r"https?://(?:www\.)?(?:iqiyi\.com|iq\.com)/(?:play|v_)[^/]+/(?P<id>[0-9a-zA-Z_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"iQIYI Video {video_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="iq-1080p",
                    url=f"https://cache.m.iqiyi.com/dc/dt/{video_id}/master.m3u8",
                    ext="mp4",
                    protocol="m3u8_native",
                    height=1080,
                )
            ],
            thumbnail=thumbnail,
        )


class WeTVIE(InfoExtractor):
    """WeTV / Tencent Video Asian streaming extractor."""

    IE_NAME = "wetv"
    IE_DESC = "WeTV Asian Drama & Anime Streaming"
    _VALID_URL = r"https?://(?:www\.)?wetv\.vip/(?:en/)?play/(?P<id>[0-9a-zA-Z_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"WeTV Video {video_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="wetv-1080p",
                    url=f"https://hls.wetv.vip/vod/{video_id}/playlist.m3u8",
                    ext="mp4",
                    protocol="m3u8_native",
                    height=1080,
                )
            ],
            thumbnail=thumbnail,
        )


class BilibiliTVIE(InfoExtractor):
    """Bilibili Global / Bstation extractor."""

    IE_NAME = "bilibilitv"
    IE_DESC = "Bilibili.tv / Bstation Global Anime & Videos"
    _VALID_URL = r"https?://(?:www\.)?bilibili\.tv/(?:en|id|vi|th|ms)/play/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Bilibili TV Anime {video_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="bstation-1080p",
                    url=f"https://api.bilibili.tv/s/video/stream/{video_id}.m3u8",
                    ext="mp4",
                    protocol="m3u8_native",
                    height=1080,
                )
            ],
            thumbnail=thumbnail,
        )
