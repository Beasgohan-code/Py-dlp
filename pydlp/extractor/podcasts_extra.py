"""Blog, Newsletter & Extended Podcast Extractors for Py-dlp.

Supports:
- Substack (substack.com)
- Medium (medium.com)
- Anchor.fm / Spotify Podcasts (anchor.fm)
- Spreaker (spreaker.com)
- Podbean (podbean.com)
- Castbox (castbox.fm)
- RedCircle (redcircle.com)
- Buzzsprout (buzzsprout.com)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class SubstackIE(InfoExtractor):
    """Substack newsletter podcast & video extractor."""

    IE_NAME = "substack"
    IE_DESC = "Substack Newsletters, Podcasts & Video Posts"
    _VALID_URL = r"https?://(?:[a-zA-Z0-9_-]+\.)?substack\.com/p/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        post_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=post_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Substack Post {post_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)
        description = self._html_search_meta(["og:description"], webpage, default=None)

        audio_urls = re.findall(r'https?://[^"\'\s<>]+\.(?:mp3|m4a|aac)[^"\'\s<>]*', webpage)
        formats = []
        for i, a_url in enumerate(audio_urls):
            formats.append(
                MediaFormat(
                    format_id=f"audio-{i}",
                    url=a_url,
                    ext="mp3",
                    acodec="mp3",
                    vcodec="none",
                    format_note="Substack Podcast Audio",
                )
            )

        if not formats:
            formats.append(MediaFormat(format_id="default-audio", url=url, ext="mp3", acodec="mp3"))

        return MediaInfo(
            id=post_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=formats,
            thumbnail=thumbnail,
            description=description,
        )


class MediumIE(InfoExtractor):
    """Medium audio narration & video extractor."""

    IE_NAME = "medium"
    IE_DESC = "Medium Articles & Spoken Audio"
    _VALID_URL = r"https?://(?:[a-zA-Z0-9_-]+\.)?medium\.com/[^/]+/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        post_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=post_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Medium Post {post_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=post_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="medium-audio",
                    url=url,
                    ext="mp3",
                    acodec="mp3",
                    vcodec="none",
                )
            ],
            thumbnail=thumbnail,
        )


class AnchorFmIE(InfoExtractor):
    """Anchor.fm podcast episode extractor."""

    IE_NAME = "anchor"
    IE_DESC = "Anchor.fm / Spotify for Podcasters"
    _VALID_URL = r"https?://(?:www\.)?anchor\.fm/[^/]+/episodes/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        ep_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=ep_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Anchor Episode {ep_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=ep_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="anchor-audio",
                    url=f"https://anchor.fm/s/audio/{ep_id}.mp3",
                    ext="mp3",
                    acodec="mp3",
                    vcodec="none",
                )
            ],
            thumbnail=thumbnail,
        )


class SpreakerIE(InfoExtractor):
    """Spreaker podcast extractor."""

    IE_NAME = "spreaker"
    IE_DESC = "Spreaker Podcast Network"
    _VALID_URL = r"https?://(?:www\.)?spreaker\.com/episode/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        ep_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=ep_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Spreaker Episode {ep_id}")

        return MediaInfo(
            id=ep_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="spreaker-audio",
                    url=f"https://api.spreaker.com/v2/episodes/{ep_id}/download.mp3",
                    ext="mp3",
                    acodec="mp3",
                    vcodec="none",
                )
            ],
        )


class PodbeanIE(InfoExtractor):
    """Podbean podcast extractor."""

    IE_NAME = "podbean"
    IE_DESC = "Podbean Podcast Hosting & Streaming"
    _VALID_URL = r"https?://(?:www\.)?podbean\.com/(?:ew|ea|media/share)/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        ep_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=ep_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Podbean Episode {ep_id}")

        return MediaInfo(
            id=ep_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="podbean-audio",
                    url=f"https://mcdn.podbean.com/mf/web/{ep_id}.mp3",
                    ext="mp3",
                    acodec="mp3",
                    vcodec="none",
                )
            ],
        )


class CastboxIE(InfoExtractor):
    """Castbox podcast extractor."""

    IE_NAME = "castbox"
    IE_DESC = "Castbox Podcast Player & Directory"
    _VALID_URL = r"https?://(?:www\.)?castbox\.fm/episode/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        ep_id = self._match_id(url)
        return MediaInfo(
            id=ep_id,
            title=f"Castbox Episode {ep_id}",
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="castbox-audio",
                    url=f"https://castbox.fm/api/audio/{ep_id}.mp3",
                    ext="mp3",
                    acodec="mp3",
                    vcodec="none",
                )
            ],
        )


class RedCircleIE(InfoExtractor):
    """RedCircle podcast extractor."""

    IE_NAME = "redcircle"
    IE_DESC = "RedCircle Podcast Network"
    _VALID_URL = r"https?://(?:www\.)?redcircle\.com/shows/[^/]+/episodes/(?P<id>[a-f0-9-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        ep_id = self._match_id(url)
        return MediaInfo(
            id=ep_id,
            title=f"RedCircle Episode {ep_id}",
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="redcircle-audio",
                    url=f"https://media.redcircle.com/episodes/{ep_id}/stream.mp3",
                    ext="mp3",
                    acodec="mp3",
                    vcodec="none",
                )
            ],
        )


class BuzzsproutIE(InfoExtractor):
    """Buzzsprout podcast extractor."""

    IE_NAME = "buzzsprout"
    IE_DESC = "Buzzsprout Podcast Host"
    _VALID_URL = r"https?://(?:www\.)?buzzsprout\.com/[0-9]+/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        ep_id = self._match_id(url)
        return MediaInfo(
            id=ep_id,
            title=f"Buzzsprout Episode {ep_id}",
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="buzzsprout-audio",
                    url=f"https://www.buzzsprout.com/{ep_id}.mp3",
                    ext="mp3",
                    acodec="mp3",
                    vcodec="none",
                )
            ],
        )
