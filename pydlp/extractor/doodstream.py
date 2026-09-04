"""DoodStream video extractor."""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html
from pydlp.extractor.base import InfoExtractor


class DoodStreamIE(InfoExtractor):
    """Extractor for DoodStream and mirror video hosts."""

    IE_NAME = "doodstream"
    IE_DESC = "DoodStream video hosting platform"
    _VALID_URL = r"^(?:https?://)?(?:www\.)?(?:dood\.(?:wf|la|so|to|sh|pm|cx|ws)|doodstream\.(?:com|co)|ds2play\.(?:com|org))/(?:d|e)/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        embed_url = f"https://dood.to/e/{video_id}"
        webpage = self._download_webpage(embed_url, video_id=video_id, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, fatal=False)

        title = f"DoodStream Video {video_id}"
        thumbnail = None
        formats: List[MediaFormat] = []

        if webpage:
            og_title = self._html_search_meta(["og:title"], webpage)
            og_thumb = self._html_search_meta(["og:image"], webpage)
            if og_title:
                title = clean_html(og_title)
            if og_thumb:
                thumbnail = og_thumb

            # Pass_md5 token pattern: /pass_md5/...
            pass_match = re.search(r"/(pass_md5/[^'\"?]+)", webpage)
            if pass_match:
                pass_path = pass_match.group(1)
                pass_url = f"https://dood.to/{pass_path}"
                pass_resp = self._download_webpage(pass_url, video_id=video_id, headers={"Referer": embed_url}, fatal=False)
                if pass_resp:
                    # Final direct download url: pass_resp + token_suffix + timestamp
                    token_suffix = "z1234567890abcdef"
                    direct_url = f"{pass_resp.strip()}{token_suffix}?{int(time.time() * 1000)}"
                    formats.append(
                        MediaFormat(
                            format_id="dood-mp4",
                            url=direct_url,
                            ext="mp4",
                            http_headers={"Referer": embed_url},
                        )
                    )

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=embed_url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=embed_url,
            thumbnail=thumbnail,
            formats=formats,
        )
