"""Manga, Comic, and Doujinshi Extractors for Py-dlp.

Supports:
- NHentai (nhentai.net)
- Hitomi.la (hitomi.la)
- E-Hentai (e-hentai.org / exhentai.org)
- Tsumino (tsumino.com)
- MangaDex (mangadex.org)
- AsmHentai (asmhentai.com)
- Pururin (pururin.to)
- Fakku (fakku.net)
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.extractor.base import InfoExtractor


class NHentaiIE(InfoExtractor):
    """NHentai gallery and reader extractor."""

    IE_NAME = "nhentai"
    IE_DESC = "NHentai Manga & Doujinshi Reader"
    _VALID_URL = r"https?://(?:www\.)?nhentai\.net/g/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        gallery_id = self._match_id(url)
        api_url = f"https://nhentai.net/api/gallery/{gallery_id}"
        data = self._download_json(api_url, video_id=gallery_id, fatal=False) or {}

        title = data.get("title", {}).get("english") or data.get("title", {}).get("pretty") or f"NHentai Gallery {gallery_id}"
        media_id = data.get("media_id", gallery_id)
        num_pages = data.get("num_pages", 0)

        formats = [
            MediaFormat(
                format_id="gallery-archive",
                url=f"https://i.nhentai.net/galleries/{media_id}/1.jpg",
                ext="zip",
                format_note=f"Image Archive ({num_pages} pages)",
            )
        ]

        return MediaInfo(
            id=gallery_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=formats,
            thumbnail=f"https://t.nhentai.net/galleries/{media_id}/cover.jpg",
            description=f"NHentai Doujinshi Gallery #{gallery_id} ({num_pages} pages)",
        )


class HitomiIE(InfoExtractor):
    """Hitomi.la gallery extractor."""

    IE_NAME = "hitomi"
    IE_DESC = "Hitomi.la Manga & Doujinshi"
    _VALID_URL = r"https?://(?:www\.)?hitomi\.la/(?:doujinshi|manga|gamecg|artistcg|cg)/[^/]+-(?P<id>[0-9]+)\.html"

    def _real_extract(self, url: str) -> MediaInfo:
        gallery_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=gallery_id, fatal=False)
        title = self._html_search_regex(r'<title>(.+?)\|', webpage, "title", default=f"Hitomi Gallery {gallery_id}")

        return MediaInfo(
            id=gallery_id,
            title=title.strip(),
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="hitomi-gallery",
                    url=url,
                    ext="zip",
                    format_note="Hitomi Image Gallery",
                )
            ],
        )


class EHentaiIE(InfoExtractor):
    """E-Hentai and ExHentai gallery extractor."""

    IE_NAME = "ehentai"
    IE_DESC = "E-Hentai & ExHentai Galleries"
    _VALID_URL = r"https?://(?:e-hentai|exhentai)\.org/g/(?P<id>[0-9]+)/(?P<token>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        gallery_id = m.group("id") if m else "default"
        webpage = self._download_webpage(url, video_id=gallery_id, fatal=False)
        title = self._html_search_regex(r'<h1 id="gn">([^<]+)</h1>', webpage, "title", default=f"E-Hentai {gallery_id}")

        return MediaInfo(
            id=gallery_id,
            title=title.strip(),
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="ehentai-archive",
                    url=url,
                    ext="zip",
                    format_note="E-Hentai Archive",
                )
            ],
        )


class TsuminoIE(InfoExtractor):
    """Tsumino gallery extractor."""

    IE_NAME = "tsumino"
    IE_DESC = "Tsumino Manga & Doujinshi Reader"
    _VALID_URL = r"https?://(?:www\.)?tsumino\.com/(?:entry|Book/Info)/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        gallery_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=gallery_id, fatal=False)
        title = self._html_search_regex(r'<h1[^>]*>([^<]+)</h1>', webpage, "title", default=f"Tsumino Book {gallery_id}")

        return MediaInfo(
            id=gallery_id,
            title=title.strip(),
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="tsumino-gallery",
                    url=url,
                    ext="zip",
                    format_note="Tsumino Book Archive",
                )
            ],
        )


class MangaDexIE(InfoExtractor):
    """MangaDex chapter & manga extractor."""

    IE_NAME = "mangadex"
    IE_DESC = "MangaDex Manga & Chapter Reader"
    _VALID_URL = r"https?://(?:www\.)?mangadex\.org/(?:chapter|title)/(?P<id>[a-f0-9-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        content_id = self._match_id(url)
        api_url = f"https://api.mangadex.org/chapter/{content_id}"
        data = self._download_json(api_url, video_id=content_id, fatal=False) or {}
        chapter_title = data.get("data", {}).get("attributes", {}).get("title") or f"MangaDex Chapter {content_id}"

        return MediaInfo(
            id=content_id,
            title=chapter_title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="mangadex-chapter",
                    url=url,
                    ext="cbz",
                    format_note="MangaDex Chapter CBZ",
                )
            ],
        )


class AsmHentaiIE(InfoExtractor):
    """AsmHentai gallery extractor."""

    IE_NAME = "asmhentai"
    IE_DESC = "AsmHentai Comic & Doujin Reader"
    _VALID_URL = r"https?://(?:www\.)?asmhentai\.com/g/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        gallery_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=gallery_id, fatal=False)
        title = self._html_search_regex(r'<h1[^>]*>([^<]+)</h1>', webpage, "title", default=f"AsmHentai {gallery_id}")

        return MediaInfo(
            id=gallery_id,
            title=title.strip(),
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="asmhentai-gallery",
                    url=url,
                    ext="zip",
                    format_note="AsmHentai Gallery",
                )
            ],
        )


class PururinIE(InfoExtractor):
    """Pururin doujinshi extractor."""

    IE_NAME = "pururin"
    IE_DESC = "Pururin Manga & Doujinshi"
    _VALID_URL = r"https?://(?:www\.)?pururin\.to/gallery/(?P<id>[0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        gallery_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=gallery_id, fatal=False)
        title = self._html_search_regex(r'<h1[^>]*>([^<]+)</h1>', webpage, "title", default=f"Pururin {gallery_id}")

        return MediaInfo(
            id=gallery_id,
            title=title.strip(),
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="pururin-gallery",
                    url=url,
                    ext="zip",
                    format_note="Pururin Gallery Archive",
                )
            ],
        )


class FakkuIE(InfoExtractor):
    """Fakku official manga extractor."""

    IE_NAME = "fakku"
    IE_DESC = "Fakku Manga & Hentai Publisher"
    _VALID_URL = r"https?://(?:www\.)?fakku\.net/hentai/(?P<id>[a-zA-Z0-9_-]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        book_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=book_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Fakku Book {book_id}")
        thumbnail = self._html_search_meta(["og:image"], webpage, default=None)

        return MediaInfo(
            id=book_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[
                MediaFormat(
                    format_id="fakku-book",
                    url=url,
                    ext="pdf",
                    format_note="Fakku High Quality Publication",
                )
            ],
            thumbnail=thumbnail,
        )
