"""SpankBang video extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class SpankBangIE(InfoExtractor):
    """Extractor for SpankBang videos."""

    IE_NAME = "spankbang"
    IE_DESC = "SpankBang.com videos"
    _VALID_URL = r"^(?:https?://)?(?:www\.|[a-z]{2}\.)?spankbang\.com/(?P<id>[a-zA-Z0-9]+)/video/(?P<slug>[^/?#]+)?"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, headers={"Cookie": "age_verified=1"}, fatal=False)

        title = f"SpankBang Video {video_id}"
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

            # Stream data embedded in var stream_data = { ... };
            stream_match = re.search(r"var\s+stream_data\s*=\s*({.+?});", webpage)
            if stream_match:
                try:
                    stream_data = json.loads(stream_match.group(1))
                    for res_key, stream_urls in stream_data.items():
                        if isinstance(stream_urls, list):
                            for s_url in stream_urls:
                                if s_url:
                                    height = int_or_none(res_key.replace("p", "").replace("k", ""))
                                    formats.append(
                                        MediaFormat(
                                            format_id=f"http-{res_key}",
                                            url=s_url,
                                            ext="mp4",
                                            height=height,
                                            format_note=res_key,
                                        )
                                    )
                        elif isinstance(stream_urls, str) and stream_urls:
                            height = int_or_none(res_key.replace("p", "").replace("k", ""))
                            formats.append(
                                MediaFormat(
                                    format_id=f"http-{res_key}",
                                    url=stream_urls,
                                    ext="mp4",
                                    height=height,
                                    format_note=res_key,
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
