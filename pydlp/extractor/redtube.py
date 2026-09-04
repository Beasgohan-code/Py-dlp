"""RedTube and YouPorn video extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class RedTubeIE(InfoExtractor):
    """Extractor for RedTube and YouPorn videos."""

    IE_NAME = "redtube"
    IE_DESC = "RedTube.com and YouPorn.com videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?(?:redtube\.com/(?P<id>\d+)|youporn\.com/watch/(?P<yp_id>\d+))"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        video_id = m.group("id") or m.group("yp_id")
        webpage = self._download_webpage(url, video_id=video_id, fatal=False)

        title = f"RedTube Video {video_id}"
        duration = None
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            dur_str = self._html_search_meta(["video:duration"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb
            if dur_str:
                duration = parse_duration(dur_str)

            # Look for mediaDefinitions
            media_match = re.search(r"mediaDefinitions\s*:\s*(\[.+?\])\s*,\s*", webpage)
            if media_match:
                try:
                    media_defs = json.loads(media_match.group(1))
                    for md in media_defs:
                        v_url = md.get("videoUrl")
                        q = md.get("quality")
                        if v_url:
                            if ".m3u8" in v_url:
                                formats.extend(self._extract_m3u8_formats(v_url, video_id))
                            else:
                                formats.append(
                                    MediaFormat(
                                        format_id=f"http-{q}" if q else f"mp4-{len(formats)}",
                                        url=v_url,
                                        ext="mp4",
                                        format_note=str(q) if q else None,
                                    )
                                )
                except Exception:
                    pass

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            thumbnail=thumbnail,
            duration=duration,
            age_limit=18,
            formats=formats,
        )
