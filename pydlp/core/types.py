"""Type definitions and dataclasses for Py-dlp."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union


@dataclass
class MediaThumbnail:
    """Represents a media thumbnail."""
    url: str
    id: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    resolution: Optional[str] = None
    filesize: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class MediaSubtitle:
    """Represents a subtitle or closed caption track."""
    ext: str = "vtt"
    url: Optional[str] = None
    data: Optional[str] = None
    name: Optional[str] = None
    language: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class MediaChapter:
    """Represents a video/audio chapter marker."""
    title: str
    start_time: float
    end_time: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MediaFormat:
    """Represents an individual media format/stream available for download."""
    format_id: str
    url: str
    ext: str = "mp4"
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    vcodec: Optional[str] = None  # e.g., 'avc1.640028', 'vp9', 'av01', 'none'
    acodec: Optional[str] = None  # e.g., 'mp4a.40.2', 'opus', 'none'
    abr: Optional[float] = None   # Audio bitrate (kbps)
    vbr: Optional[float] = None   # Video bitrate (kbps)
    tbr: Optional[float] = None   # Total bitrate (kbps)
    filesize: Optional[int] = None
    filesize_approx: Optional[int] = None
    format_note: Optional[str] = None
    protocol: str = "https"       # 'https', 'http', 'm3u8', 'm3u8_native', 'mpd', 'dash'
    http_headers: Dict[str, str] = field(default_factory=dict)
    quality: int = 0
    preference: Optional[int] = None
    language: Optional[str] = None
    container: Optional[str] = None
    dynamic_range: Optional[str] = None
    manifest_url: Optional[str] = None
    downloader_options: Dict[str, Any] = field(default_factory=dict)
    extra_info: Dict[str, Any] = field(default_factory=dict)

    @property
    def resolution(self) -> str:
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        elif self.height:
            return f"{self.height}p"
        elif self.has_audio and not self.has_video:
            return "audio only"
        return "unknown"

    @property
    def has_video(self) -> bool:
        if self.vcodec is not None:
            return self.vcodec.lower() != "none"
        if self.height or self.width:
            return True
        if self.ext in ("mp3", "m4a", "aac", "opus", "ogg", "flac", "wav"):
            return False
        return self.ext in ("mp4", "mkv", "webm", "flv", "avi", "mov", "ts")

    @property
    def has_audio(self) -> bool:
        if self.acodec is not None:
            return self.acodec.lower() != "none"
        if self.abr is not None and self.abr > 0:
            return True
        if self.ext in ("mp3", "m4a", "aac", "opus", "ogg", "flac", "wav"):
            return True
        return self.ext in ("mp4", "mkv", "webm", "flv", "avi", "mov", "ts")

    @property
    def is_video_only(self) -> bool:
        return self.has_video and not self.has_audio

    @property
    def acodec_only(self) -> bool:
        return self.has_audio and not self.has_video

    @property
    def is_hls(self) -> bool:
        return "m3u8" in self.protocol or ".m3u8" in self.url.lower()

    @property
    def is_dash(self) -> bool:
        return "dash" in self.protocol or "mpd" in self.protocol or ".mpd" in self.url.lower()

    def get_effective_bitrate(self) -> float:
        if self.tbr:
            return float(self.tbr)
        total = 0.0
        if self.vbr:
            total += float(self.vbr)
        if self.abr:
            total += float(self.abr)
        return total

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["resolution"] = self.resolution
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MediaFormat:
        d = dict(data)
        d.pop("resolution", None)
        valid_fields = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**filtered)


@dataclass
class MediaInfo:
    """Represents a media item or playlist extracted from a URL."""
    id: str
    title: str
    extractor: str
    extractor_key: str
    webpage_url: str = ""
    url: Optional[str] = None
    formats: List[MediaFormat] = field(default_factory=list)
    thumbnails: List[MediaThumbnail] = field(default_factory=list)
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    uploader: Optional[str] = None
    uploader_id: Optional[str] = None
    uploader_url: Optional[str] = None
    channel: Optional[str] = None
    channel_id: Optional[str] = None
    channel_url: Optional[str] = None
    upload_date: Optional[str] = None  # Format: YYYYMMDD
    timestamp: Optional[int] = None    # Unix timestamp
    duration: Optional[float] = None   # In seconds
    duration_string: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    subtitles: Dict[str, List[MediaSubtitle]] = field(default_factory=dict)
    automatic_captions: Dict[str, List[MediaSubtitle]] = field(default_factory=dict)
    chapters: List[MediaChapter] = field(default_factory=list)
    is_live: bool = False
    was_live: bool = False
    age_limit: int = 0
    ext: Optional[str] = None
    playlist_id: Optional[str] = None
    playlist_title: Optional[str] = None
    playlist_index: Optional[int] = None
    playlist_count: Optional[int] = None
    entries: Optional[List[MediaInfo]] = None
    _type: str = "video"  # 'video', 'playlist', 'multi_video', 'url'
    requested_formats: List[MediaFormat] = field(default_factory=list)
    selected_format: Optional[MediaFormat] = None
    filename: Optional[str] = None
    filepath: Optional[str] = None
    http_headers: Dict[str, str] = field(default_factory=dict)
    extra_info: Dict[str, Any] = field(default_factory=dict)

    def is_playlist(self) -> bool:
        return self._type in ("playlist", "multi_video") or self.entries is not None

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "extractor": self.extractor,
            "extractor_key": self.extractor_key,
            "webpage_url": self.webpage_url,
            "url": self.url,
            "description": self.description,
            "uploader": self.uploader,
            "uploader_id": self.uploader_id,
            "uploader_url": self.uploader_url,
            "channel": self.channel,
            "channel_id": self.channel_id,
            "channel_url": self.channel_url,
            "upload_date": self.upload_date,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "duration_string": self.duration_string,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "tags": list(self.tags),
            "categories": list(self.categories),
            "is_live": self.is_live,
            "was_live": self.was_live,
            "age_limit": self.age_limit,
            "ext": self.ext,
            "thumbnail": self.thumbnail,
            "_type": self._type,
            "playlist_id": self.playlist_id,
            "playlist_title": self.playlist_title,
            "playlist_index": self.playlist_index,
            "playlist_count": self.playlist_count,
            "filename": self.filename,
            "filepath": self.filepath,
            "formats": [f.to_dict() for f in self.formats],
            "thumbnails": [t.to_dict() for t in self.thumbnails],
            "chapters": [c.to_dict() for c in self.chapters],
            "subtitles": {
                lang: [s.to_dict() for s in subs]
                for lang, subs in self.subtitles.items()
            },
            "automatic_captions": {
                lang: [s.to_dict() for s in subs]
                for lang, subs in self.automatic_captions.items()
            },
            "http_headers": dict(self.http_headers),
            "extra_info": dict(self.extra_info),
        }
        if self.selected_format:
            res["selected_format"] = self.selected_format.to_dict()
        if self.requested_formats:
            res["requested_formats"] = [f.to_dict() for f in self.requested_formats]
        if self.entries is not None:
            res["entries"] = [e.to_dict() for e in self.entries]
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MediaInfo:
        d = copy.deepcopy(data)
        formats = [MediaFormat.from_dict(f) for f in d.pop("formats", [])]
        thumbnails = [
            MediaThumbnail(**t) if isinstance(t, dict) else t
            for t in d.pop("thumbnails", [])
        ]
        chapters = [
            MediaChapter(**c) if isinstance(c, dict) else c
            for c in d.pop("chapters", [])
        ]
        subtitles_dict = {}
        for lang, subs in d.pop("subtitles", {}).items():
            subtitles_dict[lang] = [
                MediaSubtitle(**s) if isinstance(s, dict) else s for s in subs
            ]
        auto_caps_dict = {}
        for lang, subs in d.pop("automatic_captions", {}).items():
            auto_caps_dict[lang] = [
                MediaSubtitle(**s) if isinstance(s, dict) else s for s in subs
            ]
        entries_data = d.pop("entries", None)
        entries = None
        if entries_data is not None:
            entries = [cls.from_dict(e) for e in entries_data]

        selected_format_data = d.pop("selected_format", None)
        selected_format = (
            MediaFormat.from_dict(selected_format_data)
            if selected_format_data
            else None
        )

        requested_formats_data = d.pop("requested_formats", [])
        requested_formats = [MediaFormat.from_dict(f) for f in requested_formats_data]

        valid_keys = cls.__dataclass_fields__.keys()
        kwargs = {k: v for k, v in d.items() if k in valid_keys}
        return cls(
            formats=formats,
            thumbnails=thumbnails,
            chapters=chapters,
            subtitles=subtitles_dict,
            automatic_captions=auto_caps_dict,
            entries=entries,
            selected_format=selected_format,
            requested_formats=requested_formats,
            **kwargs,
        )


@dataclass
class DownloadProgress:
    """Represents current download status and telemetry."""
    status: str = "downloading"  # 'starting', 'downloading', 'finished', 'error', 'processing', 'cancelled'
    downloaded_bytes: int = 0
    total_bytes: Optional[int] = None
    total_bytes_estimate: Optional[int] = None
    speed: Optional[float] = None  # bytes per second
    eta: Optional[float] = None    # seconds remaining
    elapsed: float = 0.0          # seconds elapsed
    percentage: float = 0.0       # 0.0 to 100.0
    filename: str = ""
    tmp_filename: Optional[str] = None
    fragment_index: Optional[int] = None
    fragment_count: Optional[int] = None
    info_dict: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "downloaded_bytes": self.downloaded_bytes,
            "total_bytes": self.total_bytes,
            "total_bytes_estimate": self.total_bytes_estimate,
            "speed": self.speed,
            "eta": self.eta,
            "elapsed": round(self.elapsed, 2),
            "percentage": round(self.percentage, 2),
            "filename": self.filename,
            "fragment_index": self.fragment_index,
            "fragment_count": self.fragment_count,
            "error": self.error,
        }
