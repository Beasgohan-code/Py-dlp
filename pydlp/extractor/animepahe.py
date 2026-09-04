"""AnimePahe episode and anime series extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get, urljoin
from pydlp.extractor.base import InfoExtractor


class AnimePaheIE(InfoExtractor):
    """Extractor for AnimePahe episodes and series."""

    IE_NAME = "animepahe"
    IE_DESC = "AnimePahe anime series and episodes"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?animepahe\.(?:ru|org|com)/(?:play/(?P<anime_id>[a-f0-9-]+)/(?P<session>[a-f0-9]+)|anime/(?P<id>[a-f0-9-]+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        anime_id = m.group("anime_id") or m.group("id")
        session = m.group("session")

        if not session:
            # Series page: fetch episodes list
            series_url = f"https://animepahe.ru/anime/{anime_id}"
            webpage = self._download_webpage(series_url, video_id=anime_id, fatal=False)
            title = self._html_search_meta(["og:title"], webpage, default=f"AnimePahe Series {anime_id}")
            thumb = self._html_search_meta(["og:image"], webpage)

            # Query API for episodes list: /api?m=release&id=...&sort=episode_asc&page=1
            api_url = f"https://animepahe.ru/api?m=release&id={anime_id}&sort=episode_asc&page=1"
            api_resp = self._download_json(api_url, video_id=anime_id, fatal=False)
            entries: List[MediaInfo] = []

            if api_resp and "data" in api_resp:
                for ep in api_resp["data"]:
                    ep_num = ep.get("episode")
                    ep_session = ep.get("session")
                    ep_title = f"{title} - Episode {ep_num}"
                    ep_url = f"https://animepahe.ru/play/{anime_id}/{ep_session}"
                    entries.append(
                        MediaInfo(
                            id=f"{anime_id}_{ep_session}",
                            title=ep_title,
                            extractor=self.IE_NAME,
                            extractor_key=self.ie_key(),
                            webpage_url=ep_url,
                            thumbnail=ep.get("snapshot"),
                            duration=parse_duration(ep.get("duration")),
                            playlist_index=int_or_none(ep_num),
                        )
                    )

            return MediaInfo(
                id=anime_id,
                title=title,
                extractor=self.IE_NAME,
                extractor_key=self.ie_key(),
                webpage_url=series_url,
                thumbnail=thumb,
                _type="playlist",
                playlist_id=anime_id,
                playlist_title=title,
                playlist_count=len(entries),
                entries=entries,
            )

        # Single episode page
        play_url = f"https://animepahe.ru/play/{anime_id}/{session}"
        webpage = self._download_webpage(play_url, video_id=session, fatal=False)

        title = f"AnimePahe Episode {session}"
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_title:
                title = og_title
            if og_thumb:
                thumbnail = og_thumb

            # Look for kwik server links or download buttons in html
            # <a href="https://kwik.cx/e/..." class="dropdown-item" data-src="..." data-resolution="720" data-fansub="...">
            kwik_matches = re.findall(
                r'href=["\'](https://kwik\.[a-z]+/e/[^"\']+)["\'][^>]*data-resolution=["\']?(\d+)["\']?[^>]*data-fansub=["\']?([^"\'>]+)?["\']?',
                webpage,
                re.IGNORECASE,
            )
            if not kwik_matches:
                # Alternative regex
                kwik_matches = re.findall(
                    r'data-src=["\'](https://kwik\.[a-z]+/e/[^"\']+)["\'][^>]*data-resolution=["\']?(\d+)["\']?',
                    webpage,
                    re.IGNORECASE,
                )

            for item in kwik_matches:
                if len(item) >= 2:
                    k_url = item[0]
                    res = item[1]
                    fansub = item[2] if len(item) >= 3 else "sub"
                    height = int_or_none(res)
                    fmt_id = f"kwik-{res}p-{fansub}"

                    formats.append(
                        MediaFormat(
                            format_id=fmt_id,
                            url=k_url,
                            ext="mp4",
                            height=height,
                            format_note=f"{res}p ({fansub})",
                            http_headers={"Referer": play_url},
                        )
                    )

        if not formats:
            formats.append(MediaFormat(format_id="play", url=play_url, ext="mp4"))

        return MediaInfo(
            id=f"{anime_id}_{session}",
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=play_url,
            thumbnail=thumbnail,
            formats=formats,
        )
