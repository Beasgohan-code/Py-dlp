"""Configuration management and command-line argument parser for Py-dlp."""

from __future__ import annotations

import argparse
import sys
from typing import Any, Dict, List, Optional, Tuple

from pydlp.version import __description__, __version__

DEFAULT_OPTIONS: Dict[str, Any] = {
    "format": "bestvideo+bestaudio/best",
    "outtmpl": "%(title)s [%(id)s].%(ext)s",
    "quiet": False,
    "verbose": False,
    "no_warnings": False,
    "simulate": False,
    "dumpjson": False,
    "dumpsinglejson": False,
    "listformats": False,
    "listextractors": False,
    "extract_audio": False,
    "audio_format": "mp3",
    "audio_quality": "192k",
    "keep_video": False,
    "writethumbnail": False,
    "writesubtitles": False,
    "writeautomaticsub": False,
    "subtitleslangs": ["en"],
    "subtitlesformat": "srt",
    "writeinfojson": False,
    "writechapters": False,
    "addmetadata": False,
    "concurrent_fragments": 1,
    "turbo": False,
    "limit_rate": None,
    "retries": 3,
    "continue_dl": True,
    "nopart": False,
    "overwrite": True,
    "restrictfilenames": False,
    "nocheckcertificate": False,
    "timeout": 15.0,
    "user_agent": None,
    "referer": None,
    "cookiefile": None,
    "proxy": None,
    "headers": {},
    "playliststart": 1,
    "playlistend": None,
    "playlistitems": None,
    "noplaylist": False,
    "color": True,
    "sponsorblock_remove": None,
    "sponsorblock_mark": None,
    "time_range": None,
    "normalize_audio": False,
    "target_lufs": -14.0,
    "ai_summary": False,
    "auto_chapters": False,
    "download_archive": None,
    "plugin_dir": None,
}


def build_arg_parser() -> argparse.ArgumentParser:
    """Builds yt-dlp compatible CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="pydlp",
        description=f"Py-dlp (v{__version__}) - {__description__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("urls", nargs="*", help="URL(s) or search queries to extract/download")

    # General options
    gen_group = parser.add_argument_group("General Options")
    gen_group.add_argument("-v", "--version", action="version", version=f"pydlp {__version__}")
    gen_group.add_argument("--verbose", action="store_true", help="Print debug information")
    gen_group.add_argument("-q", "--quiet", action="store_true", help="Activate quiet mode (hide progress and notices)")
    gen_group.add_argument("--no-warnings", action="store_true", help="Ignore warnings")
    gen_group.add_argument("-s", "--simulate", action="store_true", help="Do not download video, only simulate")
    gen_group.add_argument("-j", "--dump-json", action="store_true", help="Quiet, but print JSON information for each video")
    gen_group.add_argument("-J", "--dump-single-json", action="store_true", help="Quiet, but print JSON information for each URL or playlist")
    gen_group.add_argument("--list-extractors", action="store_true", help="List all supported extractors and exit")
    gen_group.add_argument("--no-color", action="store_true", help="Disable colored terminal output")

    # Web Dashboard & Server
    server_group = parser.add_argument_group("Web Dashboard & API Server")
    server_group.add_argument("--serve", "--web", action="store_true", help="Start the built-in modern Web UI dashboard and REST API server")
    server_group.add_argument("--port", type=int, default=8000, help="Port to bind the web server (default: 8000)")
    server_group.add_argument("--host", type=str, default="0.0.0.0", help="Host address to bind the web server (default: 0.0.0.0)")

    # Video Selection
    sel_group = parser.add_argument_group("Video Selection")
    sel_group.add_argument("--playlist-start", type=int, default=1, help="Playlist video to start at (default: 1)")
    sel_group.add_argument("--playlist-end", type=int, help="Playlist video to end at")
    sel_group.add_argument("--playlist-items", type=str, help="Playlist video items to download (e.g. 1,2,5-8)")
    sel_group.add_argument("--no-playlist", action="store_true", help="Download only the video, if the URL refers to a video and a playlist")
    sel_group.add_argument("--download-archive", type=str, help="Download only videos not listed in the archive file")

    # Download Options
    dl_group = parser.add_argument_group("Download Options")
    dl_group.add_argument("-N", "--concurrent-fragments", type=int, default=1, help="Number of concurrent chunk download threads (default: 1)")
    dl_group.add_argument("--turbo", action="store_true", help="Enable Adaptive Turbo multi-connection download engine")
    dl_group.add_argument("-r", "--limit-rate", type=str, help="Maximum download rate in bytes per second (e.g. 50K or 4.2M)")
    dl_group.add_argument("-R", "--retries", type=int, default=3, help="Number of retries (default: 3)")
    dl_group.add_argument("--no-continue", action="store_true", help="Do not resume partially downloaded files (restart from beginning)")
    dl_group.add_argument("--no-part", action="store_true", help="Do not use .part files (write directly to output file)")
    dl_group.add_argument("--no-overwrite", action="store_true", help="Do not overwrite existing output files")

    # Filesystem Options
    fs_group = parser.add_argument_group("Filesystem Options")
    fs_group.add_argument("-o", "--output", dest="outtmpl", type=str, default="%(title)s [%(id)s].%(ext)s", help="Output filename template (default: %%(title)s [%%(id)s].%%(ext)s)")
    fs_group.add_argument("-P", "--paths", type=str, help="The paths where the files should be downloaded")
    fs_group.add_argument("--restrict-filenames", action="store_true", help="Restrict filenames to only ASCII characters, and avoid spaces")
    fs_group.add_argument("-k", "--keep-video", action="store_true", help="Keep the intermediate video file on disk after post-processing")

    # Slicing & SponsorBlock (Advanced)
    adv_group = parser.add_argument_group("Smart Slicing & SponsorBlock Options")
    adv_group.add_argument("--sponsorblock-remove", type=str, help="SponsorBlock categories to cut out (e.g. 'sponsor,intro,outro,all')")
    adv_group.add_argument("--sponsorblock-mark", type=str, help="SponsorBlock categories to mark as chapters")
    adv_group.add_argument("--time-range", "--download-sections", dest="time_range", type=str, help="Download/trim specific time range (e.g. '*01:00-03:30' or '60-210')")
    adv_group.add_argument("--normalize-audio", action="store_true", help="Apply EBU R128 audio loudness normalization")
    adv_group.add_argument("--target-lufs", type=float, default=-14.0, help="Target LUFS for audio normalization (default: -14.0)")
    adv_group.add_argument("--ai-summary", action="store_true", help="Auto-generate structured Markdown summary & key takeaways from transcripts")
    adv_group.add_argument("--auto-chapters", action="store_true", help="Auto-detect topic transitions and generate smart chapter timestamps")
    adv_group.add_argument("--plugin-dir", type=str, help="Directory path to load custom Py-dlp plugin modules from")

    # Thumbnail Options
    thumb_group = parser.add_argument_group("Thumbnail Options")
    thumb_group.add_argument("--write-thumbnail", action="store_true", help="Write thumbnail image to disk")
    thumb_group.add_argument("--write-all-thumbnails", action="store_true", help="Write all thumbnail image formats to disk")

    # Subtitle Options
    sub_group = parser.add_argument_group("Subtitle Options")
    sub_group.add_argument("--write-sub", "--write-subs", dest="writesubtitles", action="store_true", help="Write subtitle file")
    sub_group.add_argument("--write-auto-sub", "--write-auto-subs", dest="writeautomaticsub", action="store_true", help="Write automatically generated subtitle file")
    sub_group.add_argument("--sub-lang", "--sub-langs", dest="subtitleslangs", type=str, default="en", help="Languages of the subtitles to download (comma-separated, default: en)")
    sub_group.add_argument("--sub-format", dest="subtitlesformat", type=str, default="srt", help="Subtitle format, accepts srt/vtt/ass (default: srt)")

    # Post-processing Options
    pp_group = parser.add_argument_group("Post-processing Options")
    pp_group.add_argument("-x", "--extract-audio", action="store_true", help="Convert video files to audio-only files")
    pp_group.add_argument("--audio-format", type=str, default="mp3", help="Specify audio format: 'mp3', 'aac', 'm4a', 'opus', 'flac', or 'wav' (default: mp3)")
    pp_group.add_argument("--audio-quality", type=str, default="192k", help="Specify ffmpeg audio quality (default: 192k)")
    pp_group.add_argument("--add-metadata", action="store_true", help="Write metadata to the media file")
    pp_group.add_argument("--write-info-json", action="store_true", help="Write video metadata to a .info.json file")
    pp_group.add_argument("--write-chapters", action="store_true", help="Export video chapters to a JSON file")
    pp_group.add_argument("--ffmpeg-location", type=str, help="Path to the ffmpeg binary")

    # Format Options
    fmt_group = parser.add_argument_group("Format Selection Options")
    fmt_group.add_argument("-f", "--format", type=str, default="bestvideo+bestaudio/best", help="Video format code (default: bestvideo+bestaudio/best)")
    fmt_group.add_argument("-F", "--list-formats", action="store_true", help="List available formats of each video")

    # Network Options
    net_group = parser.add_argument_group("Network Options")
    net_group.add_argument("--proxy", type=str, help="Use the specified HTTP/HTTPS/SOCKS proxy")
    net_group.add_argument("--socket-timeout", type=float, default=15.0, help="Time to wait before giving up, in seconds")
    net_group.add_argument("--user-agent", type=str, help="Specify a custom user agent")
    net_group.add_argument("--referer", type=str, help="Specify a custom referer")
    net_group.add_argument("--add-header", action="append", help="Specify a custom HTTP header (FIELD:VALUE)")
    net_group.add_argument("--cookies", dest="cookiefile", type=str, help="Netscape formatted file to read cookies from")
    net_group.add_argument("--no-check-certificates", dest="nocheckcertificate", action="store_true", help="Suppress HTTPS certificate validation")

    return parser


def parse_cli_args(args: Optional[List[str]] = None) -> Tuple[argparse.Namespace, Dict[str, Any]]:
    """Parses command line arguments and merges them with defaults."""
    parser = build_arg_parser()
    parsed = parser.parse_args(args)

    opts = dict(DEFAULT_OPTIONS)
    opts.update(vars(parsed))

    # Process custom headers
    if parsed.add_header:
        headers_dict = {}
        for h in parsed.add_header:
            if ":" in h:
                k, v = h.split(":", 1)
                headers_dict[k.strip()] = v.strip()
        opts["headers"] = headers_dict

    # Process subtitleslangs comma-separated
    if isinstance(opts.get("subtitleslangs"), str):
        opts["subtitleslangs"] = [lang.strip() for lang in opts["subtitleslangs"].split(",") if lang.strip()]

    # Process sponsorblock categories
    if parsed.sponsorblock_remove:
        opts["sponsorblock_remove"] = [c.strip() for c in parsed.sponsorblock_remove.split(",") if c.strip()]
    if parsed.sponsorblock_mark:
        opts["sponsorblock_mark"] = [c.strip() for c in parsed.sponsorblock_mark.split(",") if c.strip()]

    # Parse limit rate
    if parsed.limit_rate:
        from pydlp.core.utils import parse_filesize
        opts["rate_limit_bytes_per_sec"] = parse_filesize(parsed.limit_rate)
    else:
        opts["rate_limit_bytes_per_sec"] = None

    if parsed.no_color:
        opts["color"] = False

    if parsed.no_continue:
        opts["continue_dl"] = False

    if parsed.no_overwrite:
        opts["overwrite"] = False

    return parsed, opts
