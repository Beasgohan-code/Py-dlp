<div align="center">

# ⚡ Py-dlp

**The Ultimate, Next-Generation Media Extractor and Downloader Suite**

[![Version](https://img.shields.io/badge/version-2026.09.04-blue.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-brightgreen.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)
[![License](https://img.shields.io/badge/license-MIT-purple.svg?style=for-the-badge)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20(Pure%20Standard%20Library)-success.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)
[![Tests](https://img.shields.io/badge/tests-passing%20(46%2F46)-emerald.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)

*A modular, blazing-fast, and complete media extraction and download engine engineered with zero required dependencies, rich CLI formatting, multi-threaded chunking, HLS/DASH streaming, and a built-in modern Web Dashboard.*

---

</div>

## 🌟 Key Highlights

- 🎯 **Zero Mandatory Dependencies**: Built entirely on Python's robust standard library (`urllib`, `concurrent.futures`, `http.client`, `json`, `xml`, etc.). Works out-of-the-box anywhere.
- 🚀 **Multi-Engine Download Architecture**:
  - **Single & Resumable HTTP/HTTPS Downloader**: Range resume support (`.part` files), rolling average speed calculation, ETA estimation.
  - **Multi-Segmented Chunk Downloader**: Multi-threaded parallel byte-range chunking for accelerated downloading.
  - **HLS / M3U8 Downloader**: Complete HLS master/media playlist parsing, segment batch concurrency, fMP4 init map support, and AES-128 decryption.
  - **MPEG-DASH MPD Downloader**: XML manifest representation parsing, dynamic segment templating, and timeline resolution.
- 🧩 **Comprehensive Platform Extractors**:
  - **YouTube**: Videos, Shorts, Playlists, Channels, Search queries (`ytsearch:`), Innertube client emulation, adaptive stream muxing, subtitles, and captions.
  - **TikTok**: HD watermark-free streams, user feeds, audio tracks.
  - **Instagram**: Reels, Posts, Stories, Carousels, IGTV.
  - **Twitter / X**: Video tweets, adaptive quality streams, Syndication API fallback.
  - **Reddit**: Native `v.redd.it` audio+video multiplexing.
  - **Vimeo**: Player configuration parsing, progressive MP4, HLS streams.
  - **Twitch**: VODs, clips, live stream manifests.
  - **SoundCloud**: Tracks, playlists, MP3/Opus transcodings.
  - **Bilibili**: BV/av video resolution, DASH stream separation.
  - **Dailymotion**: Video metadata and HLS stream resolution.
  - **Facebook**: Public videos and reels.
  - **Bandcamp**: Tracks and albums with tracklist enumeration.
  - **Podcast & RSS**: Universal podcast RSS feeds (Apple Podcasts, generic RSS) with enclosure discovery.
  - **Archive.org**: Historical media, file directories, metadata.
  - **PeerTube / Fediverse**: Federated instances and WebTorrent streams.
  - **Generic / Direct**: Universal fallback for direct media files, HTML5 `<video>` / `<audio>` tags, OpenGraph, Twitter Cards, and Schema.org JSON-LD.
- 🎨 **Powerful Format Selection DSL**:
  - Full compatibility with yt-dlp syntax: `bestvideo+bestaudio/best`, `best[height<=1080]`, `worst`, `bestaudio`, exact format ID matching (`137+140`), extension matching (`mp4`, `m4a`), and fallback chains.
- 🛠️ **Post-Processing & Media Manipulation**:
  - **FFmpeg Integration**: Automatic stream merging, audio transcoding (`mp3`, `aac`, `m4a`, `opus`, `flac`, `wav`), soft/hard subtitle embedding.
  - **Pure Python Metadata Tagging**: ID3v2 tags for MP3, MP4 atom metadata, and `.info.json` export without external dependencies.
  - **Subtitle Conversion**: Real-time cross-conversion between WebVTT (`.vtt`), SubRip (`.srt`), and TTML.
  - **Thumbnail & Chapter Export**: Automated thumbnail saving and `.chapters.json` generation.
- 🌐 **Built-in Web Dashboard & REST API**:
  - Run `pydlp --serve` to launch a modern dark-mode Web UI with live progress indicators, format picker, active queue manager, and REST API.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Beasgohan-code/Py-dlp.git
cd Py-dlp

# Install in editable mode
pip install -e .
```

---

## 🚀 Quick Start

### 1. Command Line Interface (CLI)

```bash
# Basic download (best video + best audio auto-muxed)
pydlp "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# List available video & audio formats
pydlp -F "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Select a specific resolution or format
pydlp -f "bestvideo[height<=1080]+bestaudio/best" "https://vimeo.com/76979871"

# Extract audio to MP3 with custom quality
pydlp -x --audio-format mp3 --audio-quality 320k "https://soundcloud.com/artist/track"

# Accelerated multi-threaded chunk download (8 concurrent fragments)
pydlp -N 8 "https://example.com/large_video.mp4"

# Dump metadata as clean JSON
pydlp -j "https://www.tiktok.com/@user/video/123456789"

# Download with custom output template
pydlp -o "%(uploader)s/%(upload_date)s - %(title)s [%(id)s].%(ext)s" "https://x.com/user/status/12345"

# Save subtitles and thumbnails
pydlp --write-sub --sub-lang en --write-thumbnail "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 2. Launching the Web UI Dashboard & REST API

```bash
pydlp --serve --port 8000
```
Open `http://localhost:8000/` in your browser to access the graphical dashboard.

---

## 🐍 Python API Usage

### Synchronous API

```python
from pydlp import PyDLP

# Initialize with custom options
dlp = PyDLP({
    "format": "bestvideo+bestaudio/best",
    "outtmpl": "downloads/%(title)s.%(ext)s",
    "concurrent_fragments": 4,
    "writesubtitles": True,
    "subtitleslangs": ["en"],
})

# Register a custom progress callback
def on_progress(p):
    if p.status == "downloading":
        print(f"[{p.percentage:.1f}%] Speed: {p.speed} B/s - ETA: {p.eta}s")
    elif p.status == "finished":
        print(f"Download complete: {p.filename}")

dlp.add_progress_hook(on_progress)

# Extract metadata without downloading (simulate)
info = dlp.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False)
print("Title:", info.title)
print("Duration:", info.duration)
print("Formats Count:", len(info.formats))

# Download media
dlp.download(["https://www.youtube.com/watch?v=dQw4w9WgXcQ"])
```

### Asynchronous API (`AsyncPyDLP`)

```python
import asyncio
from pydlp import AsyncPyDLP

async def main():
    adlp = AsyncPyDLP({"quiet": True})
    info = await adlp.extract_info("https://vimeo.com/76979871", download=False)
    print(f"Extracted asynchronously: {info.title}")

asyncio.run(main())
```

---

## 📊 Supported Extractors

| Extractor | URL Pattern Examples | Features |
| :--- | :--- | :--- |
| **YouTube** | `youtube.com/watch?v=...`, `youtu.be/...`, `youtube.com/shorts/...` | 4K/1080p60 adaptive streams, audio only, captions, playlists |
| **YouTube Playlist** | `youtube.com/playlist?list=...` | Batch item enumeration, range filtering (`--playlist-start`) |
| **YouTube Search** | `ytsearch:query`, `ytsearch5:query` | Direct CLI search and download |
| **TikTok** | `tiktok.com/@user/video/...`, `tiktok.com/v/...` | No-watermark HD MP4, audio tracks |
| **Instagram** | `instagram.com/reel/...`, `instagram.com/p/...` | Reels, posts, stories, carousels |
| **Twitter / X** | `twitter.com/.../status/...`, `x.com/.../status/...` | Adaptive video resolutions, syndication API |
| **Reddit** | `reddit.com/r/.../comments/...`, `v.redd.it/...` | Native DASH audio + video automatic multiplexing |
| **Vimeo** | `vimeo.com/...`, `player.vimeo.com/video/...` | Progressive MP4, master HLS |
| **Twitch** | `twitch.tv/videos/...`, `clips.twitch.tv/...` | VODs, Clips, live broadcast manifests |
| **SoundCloud** | `soundcloud.com/artist/track` | MP3 / Opus audio streams, artwork |
| **Bilibili** | `bilibili.com/video/BV...` / `av...` | DASH video + audio stream extraction |
| **Dailymotion** | `dailymotion.com/video/...` | SD/HD progressive and HLS streams |
| **Facebook** | `facebook.com/watch/?v=...`, `facebook.com/reel/...` | SD and HD streams |
| **Bandcamp** | `artist.bandcamp.com/track/...`, `/album/...` | Full quality audio tracks |
| **Podcast / RSS** | `feeds.podcast.com/rss`, `*.rss`, `*.xml` | Universal podcast RSS audio enclosures & metadata |
| **Archive.org** | `archive.org/details/...` | Item files catalog, videos, audio |
| **PeerTube** | `peertube.tv/videos/watch/...` | Federated Fediverse video instances |
| **Generic** | Any URL | Direct media files, OpenGraph, HTML5 tags, Schema.org |

---

## 💻 CLI Options Reference

```text
General Options:
  -v, --version         Show version and exit
  --verbose             Print detailed debug information
  -q, --quiet           Quiet mode (suppress progress output)
  -s, --simulate        Simulate extraction only (do not write to disk)
  -j, --dump-json       Output video metadata as JSON
  -J, --dump-single-json Output playlist metadata as a single JSON object
  --list-extractors     List all 18 supported extractors
  --no-color            Disable terminal ANSI color formatting

Web Dashboard & Server:
  --serve, --web        Start built-in Web UI & REST API server
  --port PORT           Server port (default: 8000)
  --host HOST           Host address (default: 0.0.0.0)

Video Selection:
  --playlist-start NUM  Playlist video index to start at (default: 1)
  --playlist-end NUM    Playlist video index to stop at
  --playlist-items STR  Specific items (e.g. 1,3,5-10)
  --no-playlist         Download only single video if URL has playlist param

Download Options:
  -N, --concurrent-fragments NUM  Number of worker threads for chunked downloads
  -r, --limit-rate RATE Maximum download rate (e.g. 500K or 5M)
  -R, --retries NUM     Number of connection retry attempts (default: 3)
  --no-continue         Do not resume partially downloaded files
  --no-part             Write directly to output file without .part
  --no-overwrite        Do not overwrite existing destination files

Filesystem Options:
  -o, --output TEMPLATE Output path template (default: %(title)s [%(id)s].%(ext)s)
  -P, --paths PATH      Output directory path
  --restrict-filenames  Restrict filenames to ASCII safe characters
  -k, --keep-video      Keep intermediate video files after post-processing

Format Options:
  -f, --format FORMAT   Format selection expression (default: bestvideo+bestaudio/best)
  -F, --list-formats    Print available formats table

Post-Processing Options:
  -x, --extract-audio   Convert video to audio-only file
  --audio-format FORMAT Target audio codec ('mp3', 'aac', 'm4a', 'opus', 'flac', 'wav')
  --audio-quality QUAL  FFmpeg audio quality/bitrate (default: 192k)
  --add-metadata        Write ID3 / MP4 tags into media
  --write-info-json     Write full video metadata to .info.json
  --write-chapters      Export chapter markers to JSON
```

---

## 🌐 REST API Endpoints

When running `pydlp --serve`, the following REST API endpoints are available:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/status` | `GET` | Health check, server version, and extractor count |
| `/api/extractors` | `GET` | List all supported extractor modules and descriptions |
| `/api/extract` | `POST` | Analyze a media URL (`{"url": "..."}`) and return all metadata and formats |
| `/api/download` | `POST` | Enqueue background download task (`{"url": "...", "format": "..."}`) |
| `/api/tasks` | `GET` | Retrieve real-time progress, speed, ETA, and status of all tasks |
| `/api/tasks/<id>` | `GET` | Retrieve status of a single task |

---

## 🧪 Running Tests

Py-dlp includes a comprehensive unit test suite with 100% standard library compliance:

```bash
# Run all tests
python3 -m unittest discover -s tests -v
```

---

## 📄 License

Released under the permissive [MIT License](LICENSE).
