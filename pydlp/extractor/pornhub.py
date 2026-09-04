"""Pornhub video and album extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration, try_get
from pydlp.extractor.base import InfoExtractor


class PornhubIE(InfoExtractor):
    """Extractor for Pornhub videos and playlists."""

    IE_NAME = "pornhub"
    IE_DESC = "Pornhub.com videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.|[a-z]{2}\.)?pornhub\.com/(?:view_video\.php\?viewkey=|embed/)(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        viewkey = self._match_id(url)
        webpage_url = f"https://www.pornhub.com/view_video.php?viewkey={viewkey}"
        webpage = self._download_webpage(webpage_url, video_id=viewkey, headers={"Cookie": "age_verified=1; platform=pc"}, fatal=False)

        title = f"Pornhub Video {viewkey}"
        uploader = None
        duration = None
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title", "twitter:title"], webpage)
            og_thumb = self._html_search_meta(["og:image", "twitter:image"], webpage)
            dur_str = self._html_search_meta(["video:duration"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb
            if dur_str:
                duration = parse_duration(dur_str)

            # Find flashvars JSON: flashvars_\d+ = { ... };
            flashvars_match = re.search(r"flashvars_\d+\s*=\s*({.+?});\s*var\s", webpage) or re.search(r"flashvars_\d+\s*=\s*({.+?});", webpage)
            if flashvars_match:
                try:
                    flashvars = json.loads(flashvars_match.group(1))
                    title = flashvars.get("video_title", title)
                    thumbnail = flashvars.get("image_url", thumbnail)
                    duration = float(flashvars.get("video_duration", 0)) or duration

                    # 1. Check mediaDefinitions
                    media_defs = flashvars.get("mediaDefinitions", [])
                    for md in media_defs:
                        video_url = md.get("videoUrl")
                        quality = md.get("quality")
                        format_type = md.get("format", "")

                        if not video_url:
                            continue

                        if format_type == "hls" or ".m3u8" in video_url:
                            formats.extend(self._extract_m3u8_formats(video_url, viewkey, note="HLS"))
                        elif format_type == "mp4" or ".mp4" in video_url:
                            height = int_or_none(quality[0]) if isinstance(quality, list) and quality else int_or_none(quality)
                            formats.append(
                                MediaFormat(
                                    format_id=f"http-{height}p" if height else "mp4",
                                    url=video_url,
                                    ext="mp4",
                                    height=height,
                                    format_note=f"{height}p" if height else None,
                                )
                            )
                except Exception:
                    pass

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=webpage_url, ext="mp4"))

        return MediaInfo(
            id=viewkey,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=webpage_url,
            uploader=uploader,
            thumbnail=thumbnail,
            duration=duration,
            age_limit=18,
            formats=formats,
        )
