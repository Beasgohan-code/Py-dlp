"""Imageboard, Art, and Creator Archive Extractors for Py-dlp.

Supports:
- Danbooru (danbooru.donmai.us)
- Gelbooru (gelbooru.com)
- Pixiv (pixiv.net)
- Kemono (kemono.su / kemono.party)
- Coomer (coomer.su / coomer.party)
- DeviantArt (deviantart.com)
- ArtStation (artstation.com)
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class DanbooruIE(InfoExtractor):
    """Danbooru anime image and video extractor."""

    IE_NAME = "danbooru"
    IE_DESC = "Danbooru Anime Image & Video Board"
    _VALID_URL = r"https?://(?:www\.)?danbooru\.donmai\.us/posts/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        post_id = self._match_id(url)
        api_url = f"https://danbooru.donmai.us/posts/{post_id}.json"
        data = self._download_json(api_url, video_id=post_id, fatal=False) or {}

        file_url = data.get("file_url") or data.get("large_file_url") or url
        ext = data.get("file_ext", "jpg")
        title = f"Danbooru Post {post_id} ({data.get('tag_string_character', 'Artwork')})"
        tags = data.get("tag_string", "").split()

        return MediaInfo(
            id=post_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="original",
                    url=file_url,
                    ext=ext,
                    width=data.get("image_width"),
                    height=data.get("image_height"),
                    filesize=data.get("file_size"),
                )
            ],
            thumbnail=data.get("preview_file_url"),
            tags=tags,
        )


class GelbooruIE(InfoExtractor):
    """Gelbooru anime media board extractor."""

    IE_NAME = "gelbooru"
    IE_DESC = "Gelbooru Anime Media Board"
    _VALID_URL = r"https?://(?:www\.)?gelbooru\.com/index\.php\?(?:.+&)?id=(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        post_id = self._match_id(url)
        api_url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&id={post_id}&json=1"
        data = self._download_json(api_url, video_id=post_id, fatal=False) or {}
        posts = data.get("post", [])
        post = posts[0] if posts else {}

        file_url = post.get("file_url", url)
        title = f"Gelbooru Post {post_id}"

        return MediaInfo(
            id=post_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="original",
                    url=file_url,
                    ext="jpg",
                    width=post.get("width"),
                    height=post.get("height"),
                )
            ],
            thumbnail=post.get("preview_url"),
        )


class PixivIE(InfoExtractor):
    """Pixiv illustration and animation extractor."""

    IE_NAME = "pixiv"
    IE_DESC = "Pixiv Illustrations, Manga & Ugoira"
    _VALID_URL = r"https?://(?:www\.)?pixiv\.net/(?:en/)?artworks/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        art_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=art_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Pixiv Artwork {art_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=art_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="pixiv-original",
                    url=thumbnail or url,
                    ext="jpg",
                    format_note="Pixiv High Resolution Art",
                )
            ],
            thumbnail=thumbnail,
        )


class KemonoIE(InfoExtractor):
    """Kemono creator archive extractor."""

    IE_NAME = "kemono"
    IE_DESC = "Kemono Creator Media Archive"
    _VALID_URL = r"https?://(?:www\.)?(?:kemono\.su|kemono\.party)/[^/]+/user/[^/]+/post/(?P<id>[0-9a-zA-Z_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        post_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=post_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Kemono Post {post_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=post_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="kemono-media",
                    url=thumbnail or url,
                    ext="mp4",
                    format_note="Kemono Source Media",
                )
            ],
            thumbnail=thumbnail,
        )


class CoomerIE(InfoExtractor):
    """Coomer creator archive extractor."""

    IE_NAME = "coomer"
    IE_DESC = "Coomer Creator Media Archive"
    _VALID_URL = r"https?://(?:www\.)?(?:coomer\.su|coomer\.party)/[^/]+/user/[^/]+/post/(?P<id>[0-9a-zA-Z_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        post_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=post_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Coomer Post {post_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=post_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="coomer-media",
                    url=thumbnail or url,
                    ext="mp4",
                    format_note="Coomer Source Media",
                )
            ],
            thumbnail=thumbnail,
        )


class DeviantArtIE(InfoExtractor):
    """DeviantArt artwork and animation extractor."""

    IE_NAME = "deviantart"
    IE_DESC = "DeviantArt Digital Art & Animation"
    _VALID_URL = r"https?://(?:www\.)?deviantart\.com/[^/]+/art/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        art_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=art_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"DeviantArt {art_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=art_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="da-full",
                    url=thumbnail or url,
                    ext="jpg",
                    format_note="DeviantArt Full Resolution",
                )
            ],
            thumbnail=thumbnail,
        )


class ArtStationIE(InfoExtractor):
    """ArtStation portfolio & artwork extractor."""

    IE_NAME = "artstation"
    IE_DESC = "ArtStation Portfolio & Digital Media"
    _VALID_URL = r"https?://(?:www\.)?artstation\.com/artwork/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        art_id = self._match_id(url)
        api_url = f"https://www.artstation.com/projects/{art_id}.json"
        data = self._download_json(api_url, video_id=art_id, fatal=False) or {}
        title = data.get("title") or f"ArtStation Artwork {art_id}"
        assets = data.get("assets", [])

        formats = []
        for i, asset in enumerate(assets):
            image_url = asset.get("image_url")
            if image_url:
                formats.append(
                    MediaFormat(
                        format_id=f"asset-{i}",
                        url=image_url,
                        ext="jpg",
                        width=asset.get("width"),
                        height=asset.get("height"),
                    )
                )

        if not formats:
            formats.append(MediaFormat(format_id="default", url=url, ext="jpg"))

        return MediaInfo(
            id=art_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=formats,
            thumbnail=data.get("cover_url"),
            description=data.get("description"),
        )
