"""Free Ad-Supported Streaming TV (FAST) Extractors for Py-dlp.

Supports:
- Tubi TV (tubitv.com)
- Pluto TV (pluto.tv)
- Plex TV (plex.tv / watch.plex.tv)
- The Roku Channel (therokuchannel.roku.com)
- Rakuten TV (rakuten.tv)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class TubiTVIE(InfoExtractor):
    """Tubi TV movies and live TV extractor."""

    IE_NAME = "tubitv"
    IE_DESC = "Tubi TV Movies, TV Shows & Live TV"
    _VALID_URL = r"https?://(?:www\.)?tubitv\.com/(?:movies|tv-shows)/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Tubi Video {video_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)
        description = self._html_search_meta(["og:description"], webpage, default=None)

        formats = [
            MediaFormat(
                format_id="tubi-hls",
                url=f"https://tubitv.com/oz/videos/{video_id}/index.m3u8",
                ext="mp4",
                protocol="m3u8_native",
                format_note="Tubi HLS Stream",
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
            description=description,
        )


class PlutoTVIE(InfoExtractor):
    """Pluto TV live channels and on-demand video extractor."""

    IE_NAME = "plutotv"
    IE_DESC = "Pluto TV Live & On Demand"
    _VALID_URL = r"https?://(?:www\.)?pluto\.tv/(?:en/)?(?:on-demand|live-tv)/[^/]+/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"PlutoTV Channel {video_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="pluto-hls",
                    url=f"https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/{video_id}/master.m3u8",
                    ext="mp4",
                    protocol="m3u8_native",
                    format_note="Pluto HLS Master",
                )
            ],
            thumbnail=thumbnail,
        )


class PlexIE(InfoExtractor):
    """Plex Live TV and Free Movies extractor."""

    IE_NAME = "plex"
    IE_DESC = "Plex Free Movies & Live TV"
    _VALID_URL = r"https?://(?:watch\.)?plex\.tv/(?:movie|show|live-tv)/[^/]+/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Plex Media {video_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="plex-hls",
                    url=f"https://vod.provider.plex.tv/library/parts/{video_id}/master.m3u8",
                    ext="mp4",
                    protocol="m3u8_native",
                )
            ],
            thumbnail=thumbnail,
        )


class RokuIE(InfoExtractor):
    """The Roku Channel streaming extractor."""

    IE_NAME = "roku"
    IE_DESC = "The Roku Channel Movies & Shows"
    _VALID_URL = r"https?://(?:therokuchannel\.)?roku\.com/(?:watch|details)/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Roku Stream {video_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="roku-hls",
                    url=f"https://roku.video.stream/vod/{video_id}/master.m3u8",
                    ext="mp4",
                    protocol="m3u8_native",
                )
            ],
            thumbnail=thumbnail,
        )


class RakutenTVIE(InfoExtractor):
    """Rakuten TV Movies & Live Channels extractor."""

    IE_NAME = "rakutentv"
    IE_DESC = "Rakuten TV Movies & Channels"
    _VALID_URL = r"https?://(?:www\.)?rakuten\.tv/(?:[a-z]{2}/)?(?:movies|tv-shows|live)/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Rakuten TV {video_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="rakuten-hls",
                    url=f"https://stream.rakuten.tv/live/{video_id}/master.m3u8",
                    ext="mp4",
                    protocol="m3u8_native",
                )
            ],
            thumbnail=thumbnail,
        )
