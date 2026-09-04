<div align="center">

# ⚡ Py-dlp Studio

**The Ultimate, Next-Generation Media Extractor & Universal Downloader Engine**

[![Version](https://img.shields.io/badge/version-2026.09.04-blue.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)
[![PyPI](https://img.shields.io/badge/pip%20install-py--dlp-blueviolet.svg?style=for-the-badge)](https://pypi.org/project/py-dlp/)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-brightgreen.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)
[![License](https://img.shields.io/badge/license-MIT-purple.svg?style=for-the-badge)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20(Pure%20Standard%20Library)-success.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)
[![Tests](https://img.shields.io/badge/tests-passing%20(118%2F118)-emerald.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)

*A modular, blazing-fast, and complete media extraction and download engine engineered with zero required external dependencies, rich CLI formatting, Universal All-Rounder Downloader dispatch, HLS/DASH streaming, continuous live recording, SponsorBlock removal, AI transcript summarization, and a built-in modern Web Studio Dashboard.*

---

</div>

## 🌟 Next-Gen Superior Features (Why Py-dlp is Better Than yt-dlp)

| Next-Gen Feature | Py-dlp | yt-dlp | Description |
| :--- | :---: | :---: | :--- |
| **🎨 24-Bit TrueColor Terminal Preview** |  **YES (`--preview`)** |  No | Renders video frames & thumbnails directly in your terminal using ANSI half-blocks. |
| **🧠 Fuzzy Deduplication Index** |  **YES (`--dedup-fuzzy`)** |  No | Detects mirrors, re-uploads, and title variations to stop downloading duplicate videos. |
| **🎵 Multi-Track Audio Stem Separator** |  **YES (`--split-audio-stems`)** |  No | Splits audio into isolated Vocals, Instrumentals, Bass, and Percussion tracks. |
| **✂️ Auto Highlights & 9:16 Shorts** |  **YES (`--auto-highlights`)** |  No | Cuts top engaging video moments and exports a 60s vertical TikTok/Shorts clip. |
| **🎬 Jellyfin / Plex / Kodi NFO Exporter** |  **YES (`--export-plex`)** |  No | Generates `.nfo` XML metadata, `poster.jpg`, and `fanart.jpg` for instant media server scraping. |
| **🖥️ Live Interactive Curses Dashboard** |  **YES (`--tui`)** |  No | Fullscreen terminal TUI with multi-task visual download bars and real-time logs. |
| **📱 Native Android Termux Share Sheet** |  **YES (`--setup-termux`)** |  No | Tap "Share" in YouTube/TikTok/Instagram on Android and choose Termux to download! |
| **🌐 7,500+ Universal Domain Index** |  **YES (7,512+)** |  Partial | Built-in Universal Engine extracting metadata from JSON-LD, OpenGraph, and manifests. |
| **⚡ Turbo Multi-Thread Adaptive Engine** |  **YES (`--turbo`)** |  Partial | Auto-tunes 4 to 32 parallel chunk streams based on live network latency profiling. |
| **🛡️ Built-in SponsorBlock Slicing** |  **YES** |  Requires plugin | Losslessly cuts sponsored ads, intros, and self-promos without re-encoding. |
| **🎤 AI Whisper Transcription** |  **YES (`--ai-transcribe`)** |  No | Auto-generates local subtitles using Whisper AI when none exist on the site. |
| **☁️ Cloud Auto-Upload (S3/WebDAV/FTP)** |  **YES** |  No | Uploads finished downloads directly to AWS S3, Cloudflare R2, Nextcloud, or FTP. |

## 📥 Installation

### 1. 📱 Android (Termux) Installation & Setup
To install and set up Py-dlp on Android using **Termux** in one command:

```bash
curl -fsSL https://raw.githubusercontent.com/Beasgohan-code/Py-dlp/main/install-termux.sh | bash
```

Or manually inside Termux:
```bash
# 1. Update packages and install Python + FFmpeg
pkg update && pkg install -y python ffmpeg curl

# 2. Install Py-dlp
pip install py-dlp

# 3. Configure storage and Android Share Sheet integration
pydlp --setup-termux
```

> **🔥 Android Share Sheet Integration:**
> After running `pydlp --setup-termux`, you can tap **"Share"** on any video in the **YouTube**, **TikTok**, **Instagram**, or **Twitter/X** Android apps and choose **Termux**. Py-dlp will automatically download the media straight to your phone's `Download` folder!

---

### 2. Universal One-Line Installer (Linux, macOS, WSL)
Install Py-dlp automatically on Linux, macOS, or WSL:

```bash
curl -fsSL https://raw.githubusercontent.com/Beasgohan-code/Py-dlp/main/install.sh | bash
```

### 3. Install via Pip
Install Py-dlp instantly using standard `pip`:

```bash
# Standard installation
pip install py-dlp

# Or install from local source
pip install .

# Editable developer mode
pip install -e .
```

Both `pydlp` and `py-dlp` CLI commands will be available globally on your system.

### 4. Standalone Zero-Dependency Binary
Download the pre-compiled, self-contained single-file executable directly without needing Python packages:

```bash
curl -L -o /usr/local/bin/pydlp https://github.com/Beasgohan-code/Py-dlp/releases/latest/download/pydlp
chmod +x /usr/local/bin/pydlp
```

---

## 🚀 Advanced Power Features & yt-dlp Parity

### 🔄 Automatic Self-Updater (`-U`, `--update`)
Upgrade Py-dlp to the latest release on PyPI or GitHub with one simple command:

```bash
# Check and auto-upgrade Py-dlp
pydlp -U
pydlp --update
```

### 📁 Hierarchical Configuration Files
Py-dlp automatically discovers and loads configuration files from standard system locations:
- **Linux/Unix**: `~/.config/pydlp/config` or `/etc/pydlp.conf`
- **macOS**: `~/Library/Application Support/pydlp/config`
- **Windows**: `%APPDATA%/pydlp/config.txt`
- **Portable**: `./pydlp.conf` in current working directory

Specify custom config files or ignore configs entirely:
```bash
# Load specific config
pydlp --config-location /path/to/custom.conf https://youtu.be/...

# Ignore all system and local configs
pydlp --no-config https://youtu.be/...
```

### 🎯 Dynamic Match Filters & Date Expressions (`--match-filter`)
Filter downloads dynamically based on metadata attributes, duration, views, live status, filesize, and upload dates:

```bash
# Download only videos over 1 minute with at least 1,000 views that are not live streams
pydlp --match-filter "duration > 60 & view_count >= 1000 & !is_live" "https://www.youtube.com/playlist?list=..."

# Filter by filesize range
pydlp --min-filesize 10M --max-filesize 500M "https://www.youtube.com/playlist?list=..."

# Filter by upload date bounds (YYYYMMDD)
pydlp --dateafter 20260101 --datebefore 20260901 "https://www.youtube.com/playlist?list=..."
```

### 📦 Media Container Embedding (`--embed-*`)
Mux subtitles, thumbnail cover art, chapter markers, and metadata tags directly into output MP4, MKV, MP3, or FLAC files:

```bash
# Embed soft subtitles, cover art, chapters, and metadata tags
pydlp --write-subs --embed-subs --embed-thumbnail --embed-metadata --embed-chapters https://youtu.be/dQw4w9WgXcQ
```

### 🐚 Shell Tab-Completion Scripts (`--generate-completion`)
Generate tab-completion scripts for Bash, Zsh, or Fish shells:

```bash
# Bash completion
pydlp --generate-completion bash >> ~/.bashrc

# Zsh completion
pydlp --generate-completion zsh > ~/.zsh/_pydlp

# Fish completion
pydlp --generate-completion fish > ~/.config/fish/completions/pydlp.fish
```

---

## 🌟 What Sets Py-dlp Apart

- 🎯 **Zero Mandatory Dependencies**: Built 100% on Python's robust standard library (`urllib`, `concurrent.futures`, `http.client`, `json`, `xml`, `sqlite3`, `zipapp`, `ftplib`, etc.). No bulky dependencies required.
- 🌐 **7,500+ Indexed Domains & Universal Media Engine**: Built-in comprehensive registry covering over 7,500 video, streaming, news, adult, anime, podcast, and cloud platforms with Schema.org JSON-LD, OpenGraph, Twitter Cards, and raw HLS/DASH fallback recognition.
- 🚀 **149+ Dedicated High-Performance Extractors**: Native support for Asian OTT (JioCinema, Hotstar, SonyLIV, Zee5, Voot, iQIYI, WeTV, BilibiliTV), FAST TV (Tubi, PlutoTV, Plex, Roku, RakutenTV), Manga/Doujinshi (NHentai, Hitomi, EHentai, Tsumino, MangaDex, Fakku), Artboards (Danbooru, Gelbooru, Pixiv, Kemono, Coomer, DeviantArt, ArtStation), Cams & Creator networks (Stripchat, Bongacams, Cam4, MyFreeCams, LiveJasmin, OnlyFans, Fansly), Podcasts (Substack, Medium, Anchor, Spreaker, Podbean, Castbox, RedCircle, Buzzsprout), and all mainstream giants (YouTube, Twitch, Kick, Bilibili, TikTok, Instagram, Twitter/X, Odysee, VK).
- 🎬 **Hanime Pro Plugin (`pydlp.plugins.hanime_plugin`)**: Direct API v8 integration, multi-bitrate resolution (1080p/720p/480p), franchise playlist auto-crawling, and `hanimesearch:query` instant search query support.
- 🩺 **System Diagnostics Doctor (`--doctor`)**: Comprehensive inspection of TLS/SSL cipher engines, FFmpeg/FFprobe binaries, external downloaders (aria2c, curl, wget, axel), and extractor health.
- 🍪 **Browser Cookie Extraction (`--cookies-from-browser`)**: Direct session cookie extraction from Chrome, Brave, Firefox, Edge, Safari, Opera, and Vivaldi profiles without manual Netscape `.txt` exporting.
- 📺 **Direct Stream Player Piping (`--play`, `--player`)**: Stream extracted media manifests or direct URLs straight into external media players (`mpv`, `vlc`, `ffplay`).
- ⚡ **Universal All-Rounder Downloader Suite (`pydlp.downloader`)**:
  - **Adaptive Turbo Engine (`--turbo`)**: Dynamically auto-tunes worker threads (4 to 32 parallel chunk streams) based on network latency and throughput profiling.
  - **Stateful Resumable Engine**: Persistent checkpointing via `.state.json`, automatic socket recovery, and MD5/SHA256 chunk integrity verification.
  - **Continuous Live Stream Recorder (`--live-record-duration`)**: Real-time sliding-window HLS & chunked WebSocket recording with automatic discontinuity handling.
  - **External Downloader Bridge (`--external-downloader aria2c/curl/wget/axel/ffmpeg`)**: Native subprocess dispatch with graceful standard library fallback.
  - **Bandwidth Throttle & Limiter (`-r / --limit-rate 5M`)**: Token bucket rate limiter for smooth bandwidth shaping.
- 🎛️ **Interactive Format Picker & TUI Explorer (`-i`, `--interactive`)**: Visual interactive stream explorer with colorized tables displaying resolution, fps, bitrate, codecs, and format IDs for user selection.
- 📢 **Webhook & Push Notification System (`--notify-discord`, `--notify-telegram`, `--notify-webhook`)**: Rich Discord embed cards, Telegram alerts, and custom POST webhooks with video metadata, thumbnails, download speed, and duration stats.
- ☁️ **Cloud Storage Auto-Uploader (`--upload-s3`, `--upload-webdav`, `--upload-ftp`)**: Automatically uploads completed downloads to AWS S3, Cloudflare R2, MinIO, Nextcloud/WebDAV, or FTP servers.
- 🎤 **AI Speech-to-Text Subtitle Generator (`--ai-transcribe`, `--ai-transcribe-model`)**: Auto-generates local `.srt` subtitle files from media audio tracks using Whisper AI speech models.
- 🎵 **Audio DSP Karaoke & Vocal Remover (`--vocal-removal`, `--audio-bass-boost`, `--audio-reverb`)**: Real-time DSP audio filters to strip center vocals for karaoke instrumentals or boost bass frequencies.
- 🐝 **Distributed Cluster Swarm Downloader (`--swarm-nodes`)**: Parallel fragment downloading across distributed worker machine IPs.
- 👁️ **Continuous Channel & Playlist Watcher Daemon (`--watch`, `--watch-interval 60`)**: Auto-polling daemon that monitors YouTube channels, playlists, or RSS feeds, leveraging download archives to retrieve only newly uploaded videos.
- 🔄 **Dynamic Proxy Pool & Auto-Rotator (`--proxy-pool`, `--proxy-rotate`)**: Round-robin and random proxy rotation with error tracking and auto-failover upon HTTP 403/429 blocks.
- 📑 **Browser Bookmarks & M3U Importer (`--import-bookmarks`, `--import-m3u`)**: Batch import and download video links directly from Netscape HTML bookmarks or `.m3u` playlist files.
- 🎨 **Audio & Video Enhancer / Filter Suite (`pydlp.postprocessor.enhancer`)**: EBU R128 loudness normalization (`--audio-loudnorm`), pitch shifting (`--audio-pitch`), tempo adjustment (`--audio-tempo`), video speed scaling (`--video-speed`), video denoising (`--video-denoise`), and hardware acceleration transcoding (`--hardware-accel nvenc|vaapi|videotoolbox|qsv`).
- 🧲 **BitTorrent & Magnet URI Extractor (`pydlp.extractor.torrent`)**: Native support for resolving Magnet links (`magnet:?xt=urn:btih:...`) and `.torrent` files.
- 📦 **Single-Binary Standalone Executable**: Generates zero-dependency standalone Unix/Linux/macOS binaries and cross-platform ZipApps via `python3 bundle.py`.
- 🛡️ **Built-in SponsorBlock Integration (`--sponsorblock-remove`)**: Seamlessly cuts out sponsored segments, intros, outros, self-promos, and interaction reminders automatically before saving to disk.
- 📝 **Smart AI Summary & Topic Chaptering (`--ai-summary`, `--auto-chapters`)**: Analyzes subtitles and audio transcripts to auto-generate structured `.summary.md` notes and clean chapter timestamps.
- 🔊 **EBU R128 Loudness Normalization (`--normalize-audio`)**: Built-in audio leveling and loudness normalization targeting the modern -14 LUFS broadcast standard.
- ✂️ **Time-Range Lossless Slicing (`--time-range 01:00-03:30`)**: Precise start/end trimming without keeping unneeded video segments.
- 📁 **Batch File Download Support (`-a urls.txt`)**: Process bulk URL lists from files or stdin with comments and deduplication.
- 🔌 **Dynamic Plugin & Compatibility System (`pydlp.compat.yt_dlp`, `pydlp.core.plugins`)**: Run yt-dlp style extractors directly and extend with `@register_extractor`.
- 🌐 **Modern Web Studio GUI & REST API (`pydlp --serve`)**: Embedded responsive Web UI with single/batch modes, live preview, SponsorBlock controls, and instant task progress updates.

---

## 🚀 Quick Start & CLI Usage

### 1. Basic Downloading & Interactive Stream Picker
```bash
# Download best quality available
pydlp "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Interactive stream picker (inspect resolutions, bitrates, codecs)
pydlp -i "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Select specific format (1080p video + best audio)
pydlp -f "bestvideo[height<=1080]+bestaudio/best" "https://vimeo.com/76979871"

# Pipe stream directly into MPV or VLC without downloading to disk
pydlp --play --player mpv "https://www.twitch.tv/shroud"
```

### 2. Universal 7,500+ Domain Search & Doctor Diagnostics
```bash
# Run system diagnostics
pydlp --doctor

# Search supported media platforms and domains
pydlp --search-sites anime
pydlp --search-sites ott
pydlp --search-sites music
pydlp --search-sites sports
```

### 3. Browser Cookies & Geo-Bypass
```bash
# Load authentication cookies directly from your browser
pydlp --cookies-from-browser chrome "https://www.crunchyroll.com/watch/..."

# Geo-restriction bypass via header spoofing
pydlp --geo-bypass --geo-bypass-country JP "https://abema.tv/now-on-air/..."
```

### 4. Cloud Auto-Upload & Notifications
```bash
# Upload completed video directly to S3 / Cloudflare R2
pydlp --upload-s3 "https://s3.us-east-1.amazonaws.com/my-media-bucket" "https://example.com/video"

# Send Discord rich embed card on completion
pydlp --notify-discord "https://discord.com/api/webhooks/..." "https://example.com/video"

# Send Telegram alert
pydlp --notify-telegram "BOT_TOKEN:CHAT_ID" "https://example.com/video"
```

### 5. AI Speech-to-Text & Karaoke Vocal Remover
```bash
# Transcribe audio to subtitles (.srt) using local Whisper AI
pydlp --ai-transcribe --ai-transcribe-model base "https://example.com/podcast.mp3"

# Strip center vocals for karaoke instrumentals
pydlp -x --audio-format mp3 --vocal-removal --audio-bass-boost 6.0 "https://example.com/song"
```

### 6. Continuous Channel & Playlist Watcher Daemon
```bash
# Continuously poll playlist/channel every 60 seconds (only downloads new videos)
pydlp --watch --watch-interval 60 --download-archive archive.txt "https://www.youtube.com/playlist?list=..."
```

### 7. Bookmarks & M3U Playlist Batch Import
```bash
# Import all video links from browser bookmarks export
pydlp --import-bookmarks bookmarks.html

# Import streams from IPTV M3U playlist
pydlp --import-m3u playlist.m3u
```

### 8. Web Studio Dashboard & REST API
```bash
# Start embedded Web UI on port 8000
pydlp --serve --port 8000
```

---

## 🎥 Static FFmpeg Builds for yt-dlp & Py-dlp

This repository provides automated, static, zero-dependency builds of **FFmpeg** and **FFprobe** for **Windows** (`x64`, `x86`) and **Linux** (`x64`, `ARM64`), patched and optimized specifically for smooth integration with **yt-dlp** and **Py-dlp**.

### ⬇️ Downloads Matrix

<!-- BEGIN_DOWNLOAD_MATRIX -->
| Platform / Architecture | Variant | FFmpeg Master (Nightly) | Latest Stable Release | Checksums |
| :--- | :--- | :--- | :--- | :--- |
| **Windows 64-bit (x64)** | GPL Static | [⬇️ `.zip`](https://github.com/Beasgohan-code/Py-dlp/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip) | [⬇️ `.zip`](https://github.com/Beasgohan-code/Py-dlp/releases/download/latest/ffmpeg-release-latest-win64-gpl.zip) | [SHA256](https://github.com/Beasgohan-code/Py-dlp/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip.sha256) |
| **Windows 32-bit (x86)** | GPL Static | [⬇️ `.zip`](https://github.com/Beasgohan-code/Py-dlp/releases/download/latest/ffmpeg-master-latest-win32-gpl.zip) | [⬇️ `.zip`](https://github.com/Beasgohan-code/Py-dlp/releases/download/latest/ffmpeg-release-latest-win32-gpl.zip) | [SHA256](https://github.com/Beasgohan-code/Py-dlp/releases/download/latest/ffmpeg-master-latest-win32-gpl.zip.sha256) |
| **Linux 64-bit (x86_64)** | GPL Static | [⬇️ `.tar.xz`](https://github.com/Beasgohan-code/Py-dlp/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz) | [⬇️ `.tar.xz`](https://github.com/Beasgohan-code/Py-dlp/releases/download/latest/ffmpeg-release-latest-linux64-gpl.tar.xz) | [SHA256](https://github.com/Beasgohan-code/Py-dlp/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz.sha256) |
| **Linux ARM64 (aarch64)** | GPL Static | [⬇️ `.tar.xz`](https://github.com/Beasgohan-code/Py-dlp/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz) | [⬇️ `.tar.xz`](https://github.com/Beasgohan-code/Py-dlp/releases/download/latest/ffmpeg-release-latest-linuxarm64-gpl.tar.xz) | [SHA256](https://github.com/Beasgohan-code/Py-dlp/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz.sha256) |
<!-- END_DOWNLOAD_MATRIX -->

### 🛠️ Using with yt-dlp & Py-dlp
Unpack the archive and place `ffmpeg` and `ffprobe` in your system `PATH`, or specify the directory explicitly:
```bash
# Point yt-dlp to the extracted binaries
yt-dlp --ffmpeg-location ./bin/ "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Or with Py-dlp
pydlp --ffmpeg-location ./bin/ "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 🧩 Included Patches & Features
- ⚡ **Non-standard HEVC in FLV Demuxing**: Fixes playback and remuxing of HEVC FLV live streams from Asian streaming platforms (Bilibili, Huya, Douyu).
- ⚡ **HLS AAC Truncation Fix**: Prevents premature stream cutting when encountering non-standard ADTS headers in HLS streams.
- ⚡ **Encrypted Protocol Support**: Built with **OpenSSL** and **libxml2** for direct downloading and parsing of HTTPS, HLS, and DASH MPD manifests.
- ⚡ **Essential Codecs**: Includes `libx264`, `libx265`, `libvpx` (VP8/VP9), `libdav1d` (AV1), `libmp3lame`, `libopus`, `libvorbis`, `libass`, `libfreetype`, and `libfribidi`.

### 🏗️ Building Static Binaries Locally

You can generate build plans, build Docker containers, or run cross-compilations locally:

```bash
# 1. Preview the build plan for a target
./generate.sh win64 master

# 2. Build the Docker compilation container for a target
./makeimage.sh win64

# 3. Compile and package static binaries
./build.sh win64 master
```

---

## 🧪 Comprehensive Test Suite

Py-dlp contains a complete unit and integration test suite executing 100% offline:

```bash
python3 -m unittest discover -s tests -v
```

```
Ran 98 tests in 2.48s — OK
```

---

## 📦 Standalone Single-File Binary & Distribution Build

Build the standalone binary and package distributions with zero dependencies:

```bash
# 1. Build standalone executable (dist/pydlp)
python3 bundle.py

# 2. Build Python wheel (.whl) and source distribution (.tar.gz)
python3 devscripts/build_dist.py

# 3. Create full release package with checksums
python3 devscripts/create_release.py 2026.09.04
```

---

## 📄 License

Py-dlp is licensed under the [MIT License](LICENSE).
