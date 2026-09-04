"""Plex, Jellyfin, Emby, and Kodi XML NFO metadata and artwork exporter for Py-dlp."""

from __future__ import annotations

import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.http import HttpClient
from pydlp.core.types import MediaInfo
from pydlp.postprocessor.base import BasePostProcessor


class MediaServerNfoPostProcessor(BasePostProcessor):
    """Generates Jellyfin / Plex / Kodi compliant .nfo metadata files and fanart/posters."""

    def __init__(self, http: Optional[HttpClient] = None, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.http = http or HttpClient()

    @property
    def is_needed(self) -> bool:
        return bool(
            self.options.get("export_plex")
            or self.options.get("export_jellyfin")
            or self.options.get("write_nfo")
        )

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        if not self.is_needed or not info.filepath or not os.path.exists(info.filepath):
            return [], info

        target_path = Path(info.filepath)
        base_stem = target_path.stem
        parent_dir = target_path.parent

        # 1. Generate XML .nfo
        nfo_path = parent_dir / f"{base_stem}.nfo"
        self._generate_nfo(info, nfo_path)

        # 2. Save Jellyfin/Plex Poster and Fanart
        if info.thumbnail:
            self._save_artwork(info.thumbnail, parent_dir, base_stem)

        return [], info

    def _generate_nfo(self, info: MediaInfo, output_path: Path) -> None:
        """Writes structured XML NFO file."""
        root = ET.Element("movie")

        # Title & Original Title
        title_elem = ET.SubElement(root, "title")
        title_elem.text = info.title or "Untitled"

        original_title = ET.SubElement(root, "originaltitle")
        original_title.text = info.title or "Untitled"

        # Plot & Summary
        plot_elem = ET.SubElement(root, "plot")
        plot_elem.text = info.description or "No description available."

        outline_elem = ET.SubElement(root, "outline")
        outline_elem.text = (info.description or "")[:200]

        # Runtime in minutes
        if info.duration:
            runtime_elem = ET.SubElement(root, "runtime")
            runtime_elem.text = str(int(info.duration // 60))

        # Year and Premiered Date
        if info.upload_date and len(info.upload_date) >= 8:
            year = info.upload_date[:4]
            formatted_date = f"{info.upload_date[:4]}-{info.upload_date[4:6]}-{info.upload_date[6:8]}"
            year_elem = ET.SubElement(root, "year")
            year_elem.text = year
            premiered_elem = ET.SubElement(root, "premiered")
            premiered_elem.text = formatted_date

        # Studio / Channel / Uploader
        if info.uploader:
            studio_elem = ET.SubElement(root, "studio")
            studio_elem.text = info.uploader

        # Director / Artist
        if info.channel or info.uploader:
            director_elem = ET.SubElement(root, "director")
            director_elem.text = info.channel or info.uploader

        # Categories & Tags
        if info.categories:
            for cat in info.categories:
                genre_elem = ET.SubElement(root, "genre")
                genre_elem.text = cat

        if info.tags:
            for tag in info.tags:
                tag_elem = ET.SubElement(root, "tag")
                tag_elem.text = tag

        # Unique ID & URL
        uniqueid_elem = ET.SubElement(root, "uniqueid", type=info.extractor or "pydlp", default="true")
        uniqueid_elem.text = str(info.id)

        if info.webpage_url:
            url_elem = ET.SubElement(root, "website")
            url_elem.text = info.webpage_url

        # Format XML with indentation
        xml_str = ET.tostring(root, encoding="utf-8")
        try:
            import xml.dom.minidom
            dom = xml.dom.minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent="  ")
        except Exception:
            pretty_xml = xml_str.decode("utf-8")

        output_path.write_text(pretty_xml, encoding="utf-8")

    def _save_artwork(self, thumbnail_url: str, parent_dir: Path, base_stem: str) -> None:
        """Downloads and writes poster.jpg and fanart.jpg for the media server."""
        try:
            art_data = self.http.get(thumbnail_url).read()
            if not art_data:
                return

            # Save per-item poster and fanart
            poster_path = parent_dir / f"{base_stem}-poster.jpg"
            fanart_path = parent_dir / f"{base_stem}-fanart.jpg"
            generic_poster = parent_dir / "poster.jpg"

            poster_path.write_bytes(art_data)
            fanart_path.write_bytes(art_data)
            if not generic_poster.exists():
                generic_poster.write_bytes(art_data)
        except Exception:
            pass
