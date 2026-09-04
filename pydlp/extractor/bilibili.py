"""Bilibili video and animation extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import int_or_none, try_get
from pydlp.extractor.base import InfoExtractor


class BilibiliIE(InfoExtractor):
    """Extractor for Bilibili videos (BV/av)."""

    IE_NAME = "bilibili"
    IE_DESC = "Bilibili.com videos and anime"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?bilibili\.com/video/(?P<id>BV[a-zA-Z0-9]+|av\d+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id, headers={"Referer": "https://www.bilibili.com/"}, fatal=False)

        title = f"Bilibili Video {video_id}"
        description = None
        uploader = None
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []

        # Find window.__INITIAL_STATE__
        init_state_match = re.search(r"window\.__INITIAL_STATE__\s*=\s*({.+?});", webpage)
        if init_state_match:
            try:
                state_data = json.loads(init_state_match.group(1))
                video_data = state_data.get("videoData", {})
                title = video_data.get("title", title)
                description = video_data.get("desc")
                uploader = video_data.get("owner", {}).get("name")
                thumbnail = video_data.get("pic")
                duration = video_data.get("duration")
            except Exception:
                pass

        # Find window.__playinfo__
        play_info_match = re.search(r"window\.__playinfo__\s*=\s*({.+?});", webpage)
        if play_info_match:
            try:
                play_info = json.loads(play_info_match.group(1))
                dash_data = try_get(play_info, lambda x: x["data"]["dash"], dict)
                if dash_data:
                    # Video streams
                    for v in dash_data.get("video", []):
                        v_url = v.get("baseUrl") or v.get("backupUrl", [""])[0]
                        if v_url:
                            formats.append(
                                MediaFormat(
                                    format_id=f"dash-video-{v.get('id')}",
                                    url=v_url,
                                    ext="mp4",
                                    width=int_or_none(v.get("width")),
                                    height=int_or_none(v.get("height")),
                                    fps=float(v.get("frameRate", 30)),
                                    vcodec=v.get("codecs"),
                                    acodec="none",
                                    tbr=round(v.get("bandwidth", 0) / 1000.0, 1),
                                    http_headers={"Referer": "https://www.bilibili.com/"},
                                )
                            )
                    # Audio streams
                    for a in dash_data.get("audio", []):
                        a_url = a.get("baseUrl") or a.get("backupUrl", [""])[0]
                        if a_url:
                            formats.append(
                                MediaFormat(
                                    format_id=f"dash-audio-{a.get('id')}",
                                    url=a_url,
                                    ext="m4a",
                                    vcodec="none",
                                    acodec="aac",
                                    abr=round(a.get("bandwidth", 0) / 1000.0, 1),
                                    http_headers={"Referer": "https://www.bilibili.com/"},
                                )
                            )
            except Exception:
                pass

        if not formats:
            og_thumb = self._html_search_meta(["og:image"], webpage)
            og_title = self._html_search_meta(["og:title"], webpage)
            if og_title:
                title = og_title
            if og_thumb:
                thumbnail = og_thumb

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            description=description,
            uploader=uploader,
            duration=float(duration) if duration else None,
            thumbnail=thumbnail,
            formats=formats,
        )
