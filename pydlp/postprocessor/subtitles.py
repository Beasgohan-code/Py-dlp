"""Subtitle downloading, parsing, and format conversion (VTT <-> SRT <-> TTML)."""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.exceptions import PostProcessingError
from pydlp.core.http import HttpClient
from pydlp.core.types import MediaInfo, MediaSubtitle
from pydlp.postprocessor.base import BasePostProcessor


def vtt_to_srt(vtt_text: str) -> str:
    """Converts WebVTT formatted subtitles into SubRip (.srt) format."""
    lines = vtt_text.splitlines()
    srt_lines = []
    cue_index = 1
    in_cue = False
    current_cue_lines = []

    time_pattern = re.compile(
        r"^(?:(\d{2}):)?(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(?:(\d{2}):)?(\d{2}):(\d{2})\.(\d{3})"
    )

    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("WEBVTT") or line_clean.startswith("NOTE"):
            if current_cue_lines:
                srt_lines.append(str(cue_index))
                cue_index += 1
                srt_lines.extend(current_cue_lines)
                srt_lines.append("")
                current_cue_lines = []
                in_cue = False
            continue

        match = time_pattern.match(line_clean)
        if match:
            in_cue = True
            h1, m1, s1, ms1, h2, m2, s2, ms2 = match.groups()
            h1 = h1 or "00"
            h2 = h2 or "00"
            srt_time = f"{h1}:{m1}:{s1},{ms1} --> {h2}:{m2}:{s2},{ms2}"
            current_cue_lines.append(srt_time)
        elif in_cue:
            # Strip VTT styling tags like <c>, <v Speaker>, <b>, <i>
            clean_text = re.sub(r"<[^>]+>", "", line_clean)
            if clean_text:
                current_cue_lines.append(clean_text)

    if current_cue_lines:
        srt_lines.append(str(cue_index))
        srt_lines.extend(current_cue_lines)
        srt_lines.append("")

    return "\n".join(srt_lines)


def ttml_to_srt(ttml_text: str) -> str:
    """Converts TTML/DFXP XML captions to SubRip (.srt) format."""
    clean_xml = re.sub(r'\sxmlns(?::\w+)?="[^"]+"', "", ttml_text)
    try:
        root = ET.fromstring(clean_xml)
    except Exception:
        return ""

    body = root.find("body")
    if body is None:
        return ""

    srt_lines = []
    cue_index = 1

    for p in body.iter("p"):
        begin = p.attrib.get("begin", "00:00:00.000").replace(".", ",")
        end = p.attrib.get("end", "00:00:00.000").replace(".", ",")
        text = "".join(p.itertext()).strip()
        if text:
            srt_lines.append(str(cue_index))
            cue_index += 1
            srt_lines.append(f"{begin} --> {end}")
            srt_lines.append(text)
            srt_lines.append("")

    return "\n".join(srt_lines)


class SubtitlePostProcessor(BasePostProcessor):
    """Downloads and converts subtitle streams to SRT/VTT files alongside media."""

    def __init__(self, http_client: HttpClient, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.http = http_client

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        files_to_delete: List[str] = []
        if not self.options.get("writesubtitles", False) and not self.options.get("writeautomaticsub", False):
            return files_to_delete, info

        filepath = info.filepath or info.filename
        if not filepath:
            return files_to_delete, info

        base_stem, _ = os.path.splitext(filepath)
        sub_langs = self.options.get("subtitleslangs", ["en"])
        all_subs = dict(info.subtitles)
        if self.options.get("writeautomaticsub", False):
            all_subs.update(info.automatic_captions)

        target_format = self.options.get("subtitlesformat", "srt")

        for lang in sub_langs:
            # Check exact match or language prefix
            matching_tracks: List[MediaSubtitle] = []
            for k, track_list in all_subs.items():
                if k == lang or k.startswith(f"{lang}-") or lang == "all":
                    matching_tracks.extend(track_list)

            for track in matching_tracks:
                content: Optional[str] = track.data
                if not content and track.url:
                    try:
                        resp = self.http.get(track.url)
                        content = resp.text()
                    except Exception:
                        continue

                if not content:
                    continue

                out_sub_path = f"{base_stem}.{lang}.{target_format}"
                if target_format == "srt":
                    if track.ext == "vtt" or "WEBVTT" in content:
                        content = vtt_to_srt(content)
                    elif track.ext == "ttml" or "<tt" in content:
                        content = ttml_to_srt(content)

                try:
                    with open(out_sub_path, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception:
                    pass

        return files_to_delete, info
