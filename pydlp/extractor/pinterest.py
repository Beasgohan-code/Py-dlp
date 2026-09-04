"""Pinterest pin and video extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, try_get
from pydlp.extractor.base import InfoExtractor


class PinterestIE(InfoExtractor):
    """Extractor for Pinterest pins, videos, and idea pins."""

    IE_NAME = "pinterest"
    IE_DESC = "Pinterest.com video and image pins"
    _VALID_URL = r"^(?:https?://)?(?:www\.|[a-z]{2}\.)?pinterest\.(?:com|co\.[a-z]{2}|[a-z]{2})/(?:pin/(?P<id>\d+)|pin/[a-zA-Z0-9_-]+/)"

    def _real_extract(self, url: str) -> MediaInfo:
        pin_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=pin_id, fatal=False)

        title = f"Pinterest Pin {pin_id}"
        thumbnail = None
        formats: List[MediaFormat] = []

        # Find initial-data JSON
        json_match = re.search(r'<script id="__PJS_PAGE_DATA__" type="application/json">([^<]+)</script>', webpage) or re.search(r'<script id="__PWS_DATA__" type="application/json">([^<]+)</script>', webpage)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                # Search recursively for video_list
                def find_video_list(obj: Any) -> Optional[Dict]:
                    if isinstance(obj, dict):
                        if "video_list" in obj and isinstance(obj["video_list"], dict):
                            return obj["video_list"]
                        for v in obj.values():
                            res = find_video_list(v)
                            if res:
                                return res
                    elif isinstance(obj, list):
                        for item in obj:
                            res = find_video_list(item)
                            if res:
                                return res
                    return None

                video_list = find_video_list(data)
                if video_list:
                    for quality_name, vdata in video_list.items():
                        v_url = vdata.get("url")
                        if v_url:
                            w = int_or_none(vdata.get("width"))
                            h = int_or_none(vdata.get("height"))
                            if ".m3u8" in v_url:
                                formats.extend(self._extract_m3u8_formats(v_url, pin_id, note=quality_name))
                            else:
                                formats.append(
                                    MediaFormat(
                                        format_id=quality_name,
                                        url=v_url,
                                        ext="mp4",
                                        width=w,
                                        height=h,
                                        format_note=quality_name,
                                    )
                                )
            except Exception:
                pass

        if not formats:
            og_video = self._html_search_meta(["og:video", "og:video:secure_url"], webpage)
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_video:
                formats.append(MediaFormat(format_id="og-video", url=og_video, ext="mp4"))
            if og_title:
                title = og_title
            if og_thumb:
                thumbnail = og_thumb

        return MediaInfo(
            id=pin_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            thumbnail=thumbnail,
            formats=formats,
        )
