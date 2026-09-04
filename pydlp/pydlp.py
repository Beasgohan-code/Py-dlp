"""Main Py-dlp engine coordinating extraction, format selection, downloading, and post-processing."""

from __future__ import annotations

import copy
import json
import os
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Union

from pydlp.core.archive import DownloadArchive
from pydlp.core.cache import Cache
from pydlp.core.cookies import NetscapeCookieJar
from pydlp.core.exceptions import (
    CancelRequested,
    DownloadError,
    ExtractorError,
    FormatNotAvailableError,
    PostProcessingError,
    PyDLPError,
    UnsupportedURLError,
)
from pydlp.core.ascii_preview import TerminalMediaPreview
from pydlp.core.dedup import FuzzyDedupManager
from pydlp.core.format_selector import FormatSelector
from pydlp.core.http import HttpClient
from pydlp.core.interactive import InteractiveSelector
from pydlp.core.match_filter import MatchFilter
from pydlp.core.notifications import NotificationManager
from pydlp.core.plugins import get_custom_postprocessors, load_plugins_from_directory
from pydlp.core.progress import (
    ConsoleProgressBar,
    ProgressHookDispatcher,
    TerminalColors,
    colorize,
    print_format_table,
)
from pydlp.core.proxy_pool import ProxyPool
from pydlp.core.template import TemplateFormatter
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo
from pydlp.downloader.direct import get_downloader
from pydlp.extractor import find_extractor_for_url, list_extractors
from pydlp.options import DEFAULT_OPTIONS
from pydlp.postprocessor import (
    AISubtitleGeneratorPostProcessor,
    AISummaryPostProcessor,
    AudioDSPPostProcessor,
    AudioNormalizerPostProcessor,
    AudioStemSeparatorPostProcessor,
    ChapterPostProcessor,
    CloudUploaderPostProcessor,
    FFmpegPostProcessor,
    HighlightReelPostProcessor,
    MediaEmbedderPostProcessor,
    MediaEnhancerPostProcessor,
    MediaServerNfoPostProcessor,
    MetadataPostProcessor,
    SponsorBlockPostProcessor,
    SubtitlePostProcessor,
    ThumbnailPostProcessor,
    TimeRangeCutterPostProcessor,
    has_ffmpeg,
)


class PyDLP:
    """The central Py-dlp extraction and download orchestrator."""

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = dict(DEFAULT_OPTIONS)
        if params:
            self.params.update(params)

        # Load dynamic plugins from directory if specified
        plugin_dir = self.params.get("plugin_dir")
        if plugin_dir:
            load_plugins_from_directory(plugin_dir)

        # Cookie Jar
        self.cookie_jar = NetscapeCookieJar()
        cookiefile = self.params.get("cookiefile")
        if cookiefile and os.path.isfile(cookiefile):
            try:
                self.cookie_jar.load_from_file(cookiefile)
            except Exception as e:
                self._report_warning(f"Could not load cookies from {cookiefile}: {e}")

        # HTTP Client
        self.http = HttpClient(
            user_agent=self.params.get("user_agent"),
            timeout=float(self.params.get("timeout", 15.0)),
            max_retries=int(self.params.get("retries", 3)),
            proxy=self.params.get("proxy"),
            verify_ssl=not self.params.get("nocheckcertificate", False),
            rate_limit_bytes_per_sec=self.params.get("rate_limit_bytes_per_sec"),
            cookie_jar=self.cookie_jar,
            headers=self.params.get("headers", {}),
        )

        # Cache
        self.cache = Cache(enabled=self.params.get("cachedir") is not False)
        self.http.cache = self.cache

        # Download Archive
        self.archive = DownloadArchive(self.params.get("download_archive"))

        # Progress hooks and dispatcher
        self.progress_dispatcher = ProgressHookDispatcher()
        if (
            not self.params.get("quiet", False)
            and not self.params.get("dumpjson", False)
            and not self.params.get("dump_json", False)
            and not self.params.get("dumpsinglejson", False)
            and not self.params.get("dump_single_json", False)
        ):
            self.progress_dispatcher.add_hook(
                ConsoleProgressBar(enable_colors=self.params.get("color", True))
            )

        # Format selector & Template formatter
        self.format_selector = FormatSelector(self.params.get("format"))
        self.template_formatter = TemplateFormatter(
            template=self.params.get("outtmpl", "%(title)s [%(id)s].%(ext)s"),
            restricted=self.params.get("restrictfilenames", False),
        )

        # Proxy Pool
        self.proxy_pool = None
        if self.params.get("proxy_pool"):
            self.proxy_pool = ProxyPool(self.params.get("proxy_pool"))
            current_p = self.proxy_pool.get_proxy()
            if current_p:
                self.http.proxy = current_p

        # Notification Manager
        self.notifier = NotificationManager(self.params)

        # Match Filter
        self.match_filter = MatchFilter(
            match_filter_str=self.params.get("match_filter"),
            min_filesize=self.params.get("min_filesize"),
            max_filesize=self.params.get("max_filesize"),
            dateafter=self.params.get("dateafter"),
            datebefore=self.params.get("datebefore"),
        )

        # Smart Fuzzy Deduplicator
        self.dedup_manager = (
            FuzzyDedupManager() if self.params.get("dedup_fuzzy") else None
        )

        # Built-in and custom post-processors
        self._postprocessors = [
            SubtitlePostProcessor(self.http, self.params),
            AISubtitleGeneratorPostProcessor(self.params),
            ThumbnailPostProcessor(self.http, self.params),
            MetadataPostProcessor(self.params),
            SponsorBlockPostProcessor(self.http, self.params),
            TimeRangeCutterPostProcessor(self.params),
            AudioNormalizerPostProcessor(self.params),
            AudioDSPPostProcessor(self.params),
            AudioStemSeparatorPostProcessor(self.params),
            HighlightReelPostProcessor(self.params),
            MediaEnhancerPostProcessor(self.params),
            AISummaryPostProcessor(self.http, self.params),
            ChapterPostProcessor(self.params),
            FFmpegPostProcessor(self.params),
            MediaEmbedderPostProcessor(self.params),
            MediaServerNfoPostProcessor(self.http, self.params),
            CloudUploaderPostProcessor(self.params),
        ]
        # Append registered custom post-processors
        for custom_pp_cls in get_custom_postprocessors():
            self._postprocessors.append(custom_pp_cls(self.params))

    def add_progress_hook(self, hook: Callable[[DownloadProgress], None]) -> None:
        """Registers a custom progress event listener."""
        self.progress_dispatcher.add_hook(hook)

    def remove_progress_hook(self, hook: Callable[[DownloadProgress], None]) -> None:
        """Removes a registered progress event listener."""
        self.progress_dispatcher.remove_hook(hook)

    def _report_info(self, msg: str) -> None:
        if (
            not self.params.get("quiet", False)
            and not self.params.get("dumpjson", False)
            and not self.params.get("dump_json", False)
            and not self.params.get("dumpsinglejson", False)
            and not self.params.get("dump_single_json", False)
        ):
            tag = colorize("[info]", TerminalColors.BRIGHT_BLUE, self.params.get("color", True))
            print(f"{tag} {msg}")

    def _report_warning(self, msg: str) -> None:
        if (
            not self.params.get("no_warnings", False)
            and not self.params.get("quiet", False)
            and not self.params.get("dumpjson", False)
            and not self.params.get("dump_json", False)
            and not self.params.get("dumpsinglejson", False)
            and not self.params.get("dump_single_json", False)
        ):
            tag = colorize("[warning]", TerminalColors.BRIGHT_YELLOW, self.params.get("color", True))
            print(f"{tag} {msg}")

    def _report_error(self, msg: str) -> None:
        tag = colorize("[error]", TerminalColors.RED, self.params.get("color", True))
        print(f"{tag} {msg}", file=sys.stderr)

    def extract_info(
        self,
        url: str,
        download: bool = True,
        extra_info: Optional[Dict[str, Any]] = None,
    ) -> Optional[MediaInfo]:
        """Extracts media metadata for a URL and optionally executes downloads and post-processing."""
        extractor = find_extractor_for_url(url, self.http, self.params)
        self._report_info(f"Extracting URL: {url} using [{extractor.IE_NAME}]")

        try:
            info = extractor.extract(url)
        except Exception as e:
            self._report_error(f"Extraction failed: {e}")
            raise

        if extra_info:
            info.extra_info.update(extra_info)

        # Check Download Archive
        if self.archive.contains(info):
            self._report_info(f"[{info.id}] has already been recorded in archive; skipping download")
            return info

        # Check Smart Fuzzy Deduplicator
        if self.dedup_manager:
            is_dup, dup_reason = self.dedup_manager.is_duplicate(info)
            if is_dup:
                self._report_info(f"[{info.id}] Skipping download: {dup_reason}")
                return info

        # Terminal ASCII TrueColor Preview
        if self.params.get("preview") and info.title:
            preview_str = TerminalMediaPreview.render_thumbnail_url_or_file(
                info.thumbnail or info.webpage_url or "", info.title
            )
            if preview_str:
                print(f"\n{preview_str}\n")

        # Handle Playlist
        if info.is_playlist():
            return self._process_playlist(info, download=download)

        # Dump JSON if requested
        if (
            self.params.get("dumpjson", False)
            or self.params.get("dump_json", False)
            or self.params.get("dumpsinglejson", False)
            or self.params.get("dump_single_json", False)
        ):
            print(json.dumps(info.to_dict(), indent=2, ensure_ascii=False))
            return info

        # List Formats if requested
        if self.params.get("listformats", False) or self.params.get("list_formats", False):
            print_format_table(info, enable_colors=self.params.get("color", True))
            return info

        if self.params.get("simulate", False) or not download:
            return info

        # Check Match Filter
        passes_match, filter_reason = self.match_filter.matches(info)
        if not passes_match:
            self._report_info(f"[{info.id}] Skipping video ({filter_reason})")
            return info

        # Process and download single video
        self._process_video_download(info)

        # Record in archive & dedup index
        self.archive.record(info)
        if self.dedup_manager:
            self.dedup_manager.record_media(info)
        return info

    def _process_playlist(self, info: MediaInfo, download: bool = True) -> MediaInfo:
        """Processes and filters playlist entries."""
        self._report_info(f"Downloading playlist: {info.title} ({len(info.entries or [])} items)")

        if self.params.get("dumpsinglejson", False) or self.params.get("dump_single_json", False):
            print(json.dumps(info.to_dict(), indent=2, ensure_ascii=False))
            return info

        entries = info.entries or []
        start_idx = self.params.get("playliststart", 1) - 1
        end_idx = self.params.get("playlistend")

        filtered_entries = entries[start_idx:end_idx] if end_idx else entries[start_idx:]

        for i, entry in enumerate(filtered_entries, 1):
            entry_url = entry.webpage_url or entry.url
            if entry_url:
                try:
                    self._report_info(f"[{i}/{len(filtered_entries)}] Downloading {entry.title or entry_url}")
                    self.extract_info(entry_url, download=download, extra_info={"playlist_index": i})
                except Exception as e:
                    self._report_warning(f"Failed to process playlist item {entry.title}: {e}")

        return info

    def _process_video_download(self, info: MediaInfo) -> None:
        """Selects format, runs download engines, merges audio/video if needed, and applies post-processors."""
        if self.params.get("interactive", False):
            user_fmts = InteractiveSelector(color=self.params.get("color", True)).display_and_select(info)
            if user_fmts:
                selected_formats = user_fmts
            else:
                selected_formats = self.format_selector.select_formats(info)
        else:
            selected_formats = self.format_selector.select_formats(info)

        if not selected_formats:
            raise FormatNotAvailableError(f"No formats available for {info.title}")

        info.requested_formats = selected_formats
        info.selected_format = selected_formats[0]

        # Determine target file path using template
        raw_out_path = self.template_formatter.format(info, ext=info.selected_format.ext)
        paths_prefix = self.params.get("paths")
        if paths_prefix:
            raw_out_path = os.path.join(paths_prefix, raw_out_path)

        info.filepath = os.path.abspath(raw_out_path)
        info.filename = os.path.basename(raw_out_path)

        # Ensure destination directory exists
        dest_dir = os.path.dirname(info.filepath)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)

        downloaded_files: List[str] = []
        dl_start_time = time.monotonic()

        # Notify download start
        self.notifier.notify_download_start(info)

        # Simplify selected formats if both video and audio already exist in a single stream
        if len(selected_formats) >= 2:
            if (
                selected_formats[0].format_id == selected_formats[1].format_id
                or (selected_formats[0].has_video and selected_formats[0].has_audio)
            ):
                selected_formats = [selected_formats[0]]

        # Download selected stream(s)
        if len(selected_formats) == 1:
            fmt = selected_formats[0]
            downloader = get_downloader(fmt, self.http, self.params)
            for hook in self.progress_dispatcher._hooks:
                downloader.add_progress_hook(hook)

            self._report_info(f"Downloading format [{fmt.format_id}] to {info.filepath}")
            downloader.download(info.filepath, info, fmt)
            downloaded_files.append(info.filepath)

        elif len(selected_formats) >= 2:
            # Separate video and audio streams to merge
            video_fmt = selected_formats[0]
            audio_fmt = selected_formats[1]

            base_stem, ext = os.path.splitext(info.filepath)
            video_part = f"{base_stem}.f{video_fmt.format_id}.{video_fmt.ext}"
            audio_part = f"{base_stem}.f{audio_fmt.format_id}.{audio_fmt.ext}"

            # Download Video
            self._report_info(f"Downloading video stream [{video_fmt.format_id}] to {video_part}")
            dl_video = get_downloader(video_fmt, self.http, self.params)
            for hook in self.progress_dispatcher._hooks:
                dl_video.add_progress_hook(hook)
            dl_video.download(video_part, info, video_fmt)

            # Download Audio
            self._report_info(f"Downloading audio stream [{audio_fmt.format_id}] to {audio_part}")
            dl_audio = get_downloader(audio_fmt, self.http, self.params)
            for hook in self.progress_dispatcher._hooks:
                dl_audio.add_progress_hook(hook)
            dl_audio.download(audio_part, info, audio_fmt)

            # Check for FFmpeg to merge
            ffmpeg_pp = FFmpegPostProcessor(self.params)
            if ffmpeg_pp.is_available:
                try:
                    self._report_info(f"Merging video and audio into {info.filepath}")
                    ffmpeg_pp.merge_video_audio(video_part, audio_part, info.filepath)
                    if not self.params.get("keep_video", False):
                        for p in (video_part, audio_part):
                            if os.path.exists(p):
                                try:
                                    os.remove(p)
                                except OSError:
                                    pass
                    downloaded_files.append(info.filepath)
                except Exception as e:
                    self._report_warning(f"FFmpeg merging encountered an issue ({e}); preserving video and audio files.")
                    downloaded_files.extend([video_part, audio_part])
                    info.filepath = video_part
            else:
                self._report_warning("FFmpeg not found; leaving video and audio as separate tracks")
                downloaded_files.extend([video_part, audio_part])
                info.filepath = video_part

        # Run Post-Processors
        for pp in self._postprocessors:
            try:
                files_to_del, info = pp.run(info)
                for f_del in files_to_del:
                    if os.path.exists(f_del):
                        try:
                            os.remove(f_del)
                        except OSError:
                            pass
            except Exception as e:
                self._report_warning(f"Post-processor {pp.__class__.__name__} failed: {e}")

        elapsed_sec = time.monotonic() - dl_start_time
        final_size = os.path.getsize(info.filepath) if os.path.exists(info.filepath) else None
        self.notifier.notify_download_complete(info, info.filepath, elapsed_sec, final_size)
        self._report_info(f"Finished processing: {info.filepath}")

    def download(self, url_list: Union[str, List[str]]) -> int:
        """Downloads a list of URLs. Returns 0 if all succeeded, 1 if any failed."""
        if isinstance(url_list, str):
            url_list = [url_list]

        exit_code = 0
        for url in url_list:
            try:
                self.extract_info(url, download=True)
            except Exception as e:
                self._report_error(f"Failed to download {url}: {e}")
                self.notifier.notify_download_error(url, str(e))
                exit_code = 1

        return exit_code

    def __enter__(self) -> PyDLP:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass
