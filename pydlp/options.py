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
    "batchfile": None,
    "live_record_duration": None,
    "external_downloader": None,
    "doctor": False,
    "search_sites": None,
    "play": False,
    "player": None,
    "cookies_from_browser": None,
    "geo_bypass": False,
    "geo_bypass_country": "US",
    "interactive": False,
    "notify_webhook": None,
    "notify_discord": None,
    "notify_telegram": None,
    "watch": False,
    "watch_interval": 60,
    "proxy_pool": None,
    "proxy_rotate": False,
    "import_bookmarks": None,
    "import_m3u": None,
    "audio_loudnorm": False,
    "audio_pitch": None,
    "audio_tempo": None,
    "video_speed": None,
    "video_denoise": False,
    "reencode_codec": None,
    "hardware_accel": None,
    "upload_s3": None,
    "upload_webdav": None,
    "upload_ftp": None,
    "vocal_removal": False,
    "audio_bass_boost": None,
    "audio_reverb": False,
    "ai_transcribe": False,
    "ai_transcribe_model": "base",
    "swarm_nodes": None,
    "update": False,
    "config_location": None,
    "ignore_config": False,
    "match_filter": None,
    "min_filesize": None,
    "max_filesize": None,
    "dateafter": None,
    "datebefore": None,
    "embed_thumbnail": False,
    "embed_metadata": False,
    "embed_subs": False,
    "embed_chapters": False,
    "generate_completion": None,
}


def build_arg_parser() -> argparse.ArgumentParser:
    """Builds yt-dlp compatible CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="pydlp",
        description=f"Py-dlp (v{__version__}) - {__description__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("urls", nargs="*", help="URL(s) or search queries to extract/download")
    parser.add_argument("-a", "--batch-file", dest="batchfile", type=str, help="File containing URLs to download ('-' for stdin)")

    # General options
    gen_group = parser.add_argument_group("General Options")
    gen_group.add_argument("-v", "--version", action="version", version=f"pydlp {__version__}")
    gen_group.add_argument("-U", "--update", action="store_true", help="Update this program to the latest version")
    gen_group.add_argument("--config-location", type=str, help="Location of the configuration file")
    gen_group.add_argument("--no-config", "--ignore-config", dest="ignore_config", action="store_true", help="Do not load any configuration files")
    gen_group.add_argument("--generate-completion", type=str, choices=["bash", "zsh", "fish"], help="Generate shell auto-completion script and exit")
    gen_group.add_argument("--verbose", action="store_true", help="Print debug information")
    gen_group.add_argument("-q", "--quiet", action="store_true", help="Activate quiet mode (hide progress and notices)")
    gen_group.add_argument("--no-warnings", action="store_true", help="Ignore warnings")
    gen_group.add_argument("-s", "--simulate", action="store_true", help="Do not download video, only simulate")
    gen_group.add_argument("-j", "--dump-json", action="store_true", help="Quiet, but print JSON information for each video")
    gen_group.add_argument("-J", "--dump-single-json", action="store_true", help="Quiet, but print JSON information for each URL or playlist")
    gen_group.add_argument("--list-extractors", action="store_true", help="List all supported extractors and exit")
    gen_group.add_argument("--search-sites", type=str, help="Search across 2,000+ indexed domains and platforms")
    gen_group.add_argument("--doctor", action="store_true", help="Run system diagnostics and check health of dependencies")
    gen_group.add_argument("--play", action="store_true", help="Stream video directly into external media player (mpv, vlc, ffplay)")
    gen_group.add_argument("--player", type=str, help="Specify player executable for direct streaming (e.g. mpv, vlc)")
    gen_group.add_argument("-i", "--interactive", action="store_true", help="Interactively inspect and select streams/formats before downloading")
    gen_group.add_argument("--import-bookmarks", type=str, help="Import and download URLs from browser HTML bookmarks file")
    gen_group.add_argument("--import-m3u", type=str, help="Import and download stream URLs from .m3u/.m3u8 playlist file")
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
    sel_group.add_argument("--match-filter", type=str, help="Generic video filter expression (e.g. 'duration > 60 & view_count >= 1000')")
    sel_group.add_argument("--min-filesize", type=str, help="Do not download any videos smaller than SIZE (e.g. 50k or 44.6m)")
    sel_group.add_argument("--max-filesize", type=str, help="Do not download any videos larger than SIZE (e.g. 50k or 44.6m)")
    sel_group.add_argument("--dateafter", type=str, help="Download only videos uploaded on or after this date (YYYYMMDD)")
    sel_group.add_argument("--datebefore", type=str, help="Download only videos uploaded on or before this date (YYYYMMDD)")

    # Download Options
    dl_group = parser.add_argument_group("Download Options")
    dl_group.add_argument("--external-downloader", type=str, help="Use the specified external downloader (aria2c, curl, wget, axel, ffmpeg)")
    dl_group.add_argument("--live-record-duration", type=float, help="Record live stream for specified duration in seconds and exit")
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
    sub_group = parser.add_argument_group("Subtitle & AI Transcription Options")
    sub_group.add_argument("--write-sub", "--write-subs", dest="writesubtitles", action="store_true", help="Write subtitle file")
    sub_group.add_argument("--write-auto-sub", "--write-auto-subs", dest="writeautomaticsub", action="store_true", help="Write automatically generated subtitle file")
    sub_group.add_argument("--ai-transcribe", action="store_true", help="Generate local AI subtitle transcriptions using Whisper speech models")
    sub_group.add_argument("--ai-transcribe-model", type=str, default="base", help="Whisper transcription model size: tiny, base, small, medium, large (default: base)")
    sub_group.add_argument("--sub-lang", "--sub-langs", dest="subtitleslangs", type=str, default="en", help="Languages of the subtitles to download (comma-separated, default: en)")
    sub_group.add_argument("--sub-format", dest="subtitlesformat", type=str, default="srt", help="Subtitle format, accepts srt/vtt/ass (default: srt)")

    # Post-processing Options
    pp_group = parser.add_argument_group("Post-processing, DSP & Filter Options")
    pp_group.add_argument("-x", "--extract-audio", action="store_true", help="Convert video files to audio-only files")
    pp_group.add_argument("--audio-format", type=str, default="mp3", help="Specify audio format: 'mp3', 'aac', 'm4a', 'opus', 'flac', or 'wav' (default: mp3)")
    pp_group.add_argument("--audio-quality", type=str, default="192k", help="Specify ffmpeg audio quality (default: 192k)")
    pp_group.add_argument("--audio-loudnorm", action="store_true", help="Apply EBU R128 loudness normalization")
    pp_group.add_argument("--audio-pitch", type=float, help="Adjust audio pitch multiplier (e.g. 1.2 or 0.85)")
    pp_group.add_argument("--audio-tempo", type=float, help="Adjust audio playback tempo/speed without changing pitch (e.g. 1.25)")
    pp_group.add_argument("--vocal-removal", action="store_true", help="Apply center vocal removal filter for karaoke/instrumentals")
    pp_group.add_argument("--audio-bass-boost", type=float, help="Apply bass boost filter with gain in dB (e.g. 8.0)")
    pp_group.add_argument("--audio-reverb", action="store_true", help="Apply stereo audio reverberation effect")
    pp_group.add_argument("--video-speed", type=float, help="Adjust video speed multiplier (e.g. 1.5 or 0.75)")
    pp_group.add_argument("--video-denoise", action="store_true", help="Apply high-quality 3D video denoising filter")
    pp_group.add_argument("--reencode-codec", type=str, help="Re-encode output with codec (e.g. h264, hevc, av1, vp9, mp3, flac)")
    pp_group.add_argument("--hardware-accel", type=str, help="Hardware acceleration backend (cuda, nvenc, vaapi, videotoolbox, qsv)")
    pp_group.add_argument("--embed-subs", "--embed-subtitles", dest="embed_subs", action="store_true", help="Embed subtitles into video container (mp4, mkv)")
    pp_group.add_argument("--embed-thumbnail", action="store_true", help="Embed thumbnail image into video/audio container as cover art")
    pp_group.add_argument("--embed-metadata", "--add-metadata", dest="embed_metadata", action="store_true", help="Write and embed metadata tags into the media file")
    pp_group.add_argument("--embed-chapters", action="store_true", help="Embed chapter markers into the video container")
    pp_group.add_argument("--write-info-json", action="store_true", help="Write video metadata to a .info.json file")
    pp_group.add_argument("--write-chapters", action="store_true", help="Export video chapters to a JSON file")
    pp_group.add_argument("--ffmpeg-location", type=str, help="Path to the ffmpeg binary")

    # Cloud & Remote Upload Options
    cloud_group = parser.add_argument_group("Cloud & Remote Storage Upload Options")
    cloud_group.add_argument("--upload-s3", type=str, help="Auto-upload completed download to S3/R2 REST PUT endpoint or bucket URL")
    cloud_group.add_argument("--upload-webdav", type=str, help="Auto-upload completed download to Nextcloud/WebDAV URL")
    cloud_group.add_argument("--upload-ftp", type=str, help="Auto-upload completed download to FTP URL (ftp://user:pass@host/path)")

    # Distributed Cluster Swarm
    swarm_group = parser.add_argument_group("Distributed Cluster Swarm Options")
    swarm_group.add_argument("--swarm-nodes", type=str, help="Comma-separated list of remote Py-dlp worker nodes for distributed chunk swarm")

    # Format Options
    fmt_group = parser.add_argument_group("Format Selection Options")
    fmt_group.add_argument("-f", "--format", type=str, default="bestvideo+bestaudio/best", help="Video format code (default: bestvideo+bestaudio/best)")
    fmt_group.add_argument("-F", "--list-formats", action="store_true", help="List available formats of each video")

    # Continuous Watcher & Daemon
    watch_group = parser.add_argument_group("Watcher & Daemon Options")
    watch_group.add_argument("--watch", action="store_true", help="Continuously monitor and watch URLs/channels for new items")
    watch_group.add_argument("--watch-interval", type=int, default=60, help="Interval in seconds between watcher poll cycles (default: 60)")

    # Notifications & Webhooks
    notify_group = parser.add_argument_group("Notification & Webhook Options")
    notify_group.add_argument("--notify-webhook", type=str, help="Send HTTP POST webhook events on download progress and completion")
    notify_group.add_argument("--notify-discord", type=str, help="Send Discord rich embed notification cards on download completion/failure")
    notify_group.add_argument("--notify-telegram", type=str, help="Send Telegram notifications on download completion (TOKEN:CHAT_ID)")
    notify_group.add_argument("--notify-termux", action="store_true", default=True, help="Send native Android Termux push notifications")
    notify_group.add_argument("--setup-termux", action="store_true", help="Auto-configure Android Termux permissions, share-sheet url-opener, and storage paths")

    # Network Options
    net_group = parser.add_argument_group("Network Options")
    net_group.add_argument("--proxy", type=str, help="Use the specified HTTP/HTTPS/SOCKS proxy")
    net_group.add_argument("--proxy-pool", type=str, help="File or comma-separated list of proxy servers to rotate through")
    net_group.add_argument("--proxy-rotate", action="store_true", help="Enable automatic proxy rotation on failures")
    net_group.add_argument("--geo-bypass", action="store_true", help="Bypass geographic restriction via headers spoofing")
    net_group.add_argument("--geo-bypass-country", type=str, default="US", help="Country code for geo-bypass spoofing (default: US)")
    net_group.add_argument("--cookies-from-browser", type=str, help="Load cookies from browser (chrome, firefox, brave, edge, safari, opera, vivaldi)")
    net_group.add_argument("--socket-timeout", type=float, default=15.0, help="Time to wait before giving up, in seconds")
    net_group.add_argument("--user-agent", type=str, help="Specify a custom user agent")
    net_group.add_argument("--referer", type=str, help="Specify a custom referer")
    net_group.add_argument("--add-header", action="append", help="Specify a custom HTTP header (FIELD:VALUE)")
    net_group.add_argument("--cookies", dest="cookiefile", type=str, help="Netscape formatted file to read cookies from")
    net_group.add_argument("--no-check-certificates", dest="nocheckcertificate", action="store_true", help="Suppress HTTPS certificate validation")

    return parser


def parse_cli_args(args: Optional[List[str]] = None) -> Tuple[argparse.Namespace, Dict[str, Any]]:
    """Parses command line arguments and merges them with defaults and configuration files."""
    from pydlp.core.config import ConfigFileParser

    raw_args = list(args) if args is not None else sys.argv[1:]

    # Check for config bypass or custom location
    ignore_config = "--no-config" in raw_args or "--ignore-config" in raw_args
    custom_config = None
    for i, a in enumerate(raw_args):
        if a == "--config-location" and i + 1 < len(raw_args):
            custom_config = raw_args[i + 1]
            break

    config_args = ConfigFileParser.load_config_args(custom_config, ignore_config=ignore_config)
    combined_args = config_args + raw_args

    parser = build_arg_parser()
    parsed = parser.parse_args(combined_args)

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
