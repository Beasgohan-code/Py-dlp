<div align="center">

# ⚡ Py-dlp Studio

**The Ultimate, Next-Generation Media Extractor & Downloader Engine**

[![Version](https://img.shields.io/badge/version-2026.09.04-blue.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-brightgreen.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)
[![License](https://img.shields.io/badge/license-MIT-purple.svg?style=for-the-badge)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20(Pure%20Standard%20Library)-success.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)
[![Tests](https://img.shields.io/badge/tests-passing%20(58%2F58)-emerald.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)

*A modular, blazing-fast, and complete media extraction and download engine engineered with zero required external dependencies, rich CLI formatting, adaptive turbo multi-connection chunking, HLS/DASH streaming, SponsorBlock removal, AI transcript summarization, and a built-in modern Web Studio Dashboard.*

---

</div>

## 🌟 What Sets Py-dlp Apart

- 🎯 **Zero Mandatory Dependencies**: Built 100% on Python's robust standard library (`urllib`, `concurrent.futures`, `http.client`, `json`, `xml`, etc.). No bulky dependencies required.
- ⚡ **Adaptive Turbo Multi-Connection Downloader (`--turbo`)**:
  - Dynamically profiles latency and throughput across concurrent chunks.
  - Automatically auto-tunes worker threads (from 4 to 32 parallel connections) to maximize bandwidth.
- 🛡️ **Built-in SponsorBlock Integration (`--sponsorblock-remove`)**:
  - Direct integration with SponsorBlock API to seamlessly cut out sponsored segments, intros, outros, self-promos, and interaction reminders automatically before saving to disk.
- 📝 **Smart AI Summary & Topic Chaptering (`--ai-summary`, `--auto-chapters`)**:
  - Ingests video subtitles & audio transcripts, analyzes speech density and topic transitions, and auto-generates structured `.summary.md` notes and clean chapter timestamps.
- 🔊 **EBU R128 Loudness Normalization (`--normalize-audio`)**:
  - Built-in audio leveling and loudness normalization targeting modern -14 LUFS standard.
- ✂️ **Time-Range Lossless Slicing (`--time-range 01:00-03:30`)**:
  - Precise start/end trimming without requiring you to keep unneeded video segments.
- 📦 **Download Archive & Deduplication (`--download-archive`)**:
  - Skip previously downloaded videos across channel/playlist batch jobs.
- 🔌 **Dynamic Plugin System (`pydlp.core.plugins`)**:
  - Extend Py-dlp with custom extractors, downloaders, and post-processors using simple `@register_extractor` decorators.
- 🌐 **Modern Web Studio GUI & REST API (`pydlp --serve`)**:
  - Embedded responsive Web UI with single/batch modes, live preview, SponsorBlock controls, and instant task progress updates.

---

## 📊 24+ Supported Extractors

| Extractor | URL Pattern Examples | Key Features |
| :--- | :--- | :--- |
| **YouTube** | `youtube.com/watch?v=...`, `youtu.be/...`, `youtube.com/shorts/...` | 4K/1080p60 adaptive streams, audio only, captions, playlists |
| **YouTube Playlist** | `youtube.com/playlist?list=...` | Batch item enumeration, range filtering (`--playlist-start`) |
| **YouTube Search** | `ytsearch:query`, `ytsearch5:query` | Direct CLI search and download |
| **TikTok** | `tiktok.com/@user/video/...`, `tiktok.com/v/...` | No-watermark HD MP4, audio tracks |
| **Instagram** | `instagram.com/reel/...`, `instagram.com/p/...` | Reels, posts, stories, carousels |
| **Twitter / X** | `twitter.com/.../status/...`, `x.com/.../status/...` | Adaptive video resolutions, syndication API |
| **Reddit** | `reddit.com/r/.../comments/...`, `v.redd.it/...` | Native DASH audio + video automatic multiplexing |
| **Spotify** | `open.spotify.com/track/...`, `/album/...`, `/playlist/...` | Track/playlist metadata & stream resolution |
| **Vimeo** | `vimeo.com/...`, `player.vimeo.com/video/...` | Progressive MP4, master HLS |
| **Twitch** | `twitch.tv/videos/...`, `clips.twitch.tv/...` | VODs, Clips, live broadcast manifests |
| **SoundCloud** | `soundcloud.com/artist/track` | MP3 / Opus audio streams, artwork |
| **Bilibili** | `bilibili.com/video/BV...` / `av...` | DASH video + audio stream extraction |
| **Rumble** | `rumble.com/v...` | Rumble video stream extraction |
| **Pinterest** | `pinterest.com/pin/...` | Pin videos, idea pins |
| **Threads** | `threads.net/@user/post/...` | Meta Threads videos and posts |
| **Bluesky** | `bsky.app/profile/.../post/...` | ATProto video embeds and HLS streams |
| **Streamable** | `streamable.com/...` | High quality clip extraction |
| **Dailymotion** | `dailymotion.com/video/...` | SD/HD progressive and HLS streams |
| **Facebook** | `facebook.com/watch/?v=...`, `facebook.com/reel/...` | SD and HD streams |
| **Bandcamp** | `artist.bandcamp.com/track/...`, `/album/...` | Full quality audio tracks |
| **Podcast / RSS** | `feeds.podcast.com/rss`, `*.rss`, `*.xml` | Universal podcast RSS audio enclosures & metadata |
| **Archive.org** | `archive.org/details/...` | Item files catalog, videos, audio |
| **PeerTube** | `peertube.tv/videos/watch/...` | Federated Fediverse video instances |
| **Generic** | Any URL | Direct media files, OpenGraph, HTML5 tags, Schema.org |

---

## 🚀 Quick Start (CLI)

```bash
# Basic download
pydlp "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Turbo multi-connection acceleration
pydlp --turbo "https://example.com/large_video.mp4"

# Remove sponsors, intros, and outros automatically
pydlp --sponsorblock-remove sponsor,intro,outro "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Trim specific time range (e.g. from 01:00 to 03:30)
pydlp --time-range 01:00-03:30 "https://vimeo.com/76979871"

# Extract audio with EBU R128 loudness normalization
pydlp -x --audio-format mp3 --normalize-audio "https://soundcloud.com/artist/track"

# Auto-generate AI summary notes and smart chapters
pydlp --ai-summary --auto-chapters "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# List available formats
pydlp -F "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Launch the Web Studio Dashboard
pydlp --serve --port 8000
```

---

## 🐍 Python SDK Examples

```python
from pydlp import PyDLP, AsyncPyDLP

# Initialize PyDLP with advanced options
dlp = PyDLP({
    "format": "bestvideo+bestaudio/best",
    "outtmpl": "%(title)s.%(ext)s",
    "turbo": True,
    "sponsorblock_remove": ["sponsor", "intro"],
    "ai_summary": True,
})

# Progress Hook
dlp.add_progress_hook(lambda p: print(f"Progress: {p.percentage:.1f}% @ {p.speed} B/s"))

# Extract and download
info = dlp.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=True)
print(f"Downloaded: {info.filepath}")
```

---

## 🔌 Dynamic Plugin Example

```python
from pydlp.core.plugins import register_extractor
from pydlp.extractor.base import InfoExtractor
from pydlp.core.types import MediaInfo, MediaFormat

@register_extractor
class MyCustomPlatformIE(InfoExtractor):
    IE_NAME = "custom_platform"
    _VALID_URL = r"https?://custom-platform\.com/watch/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        media_id = self._match_id(url)
        return MediaInfo(
            id=media_id,
            title=f"Custom Media {media_id}",
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            formats=[MediaFormat(format_id="hd", url=f"https://cdn.custom-platform.com/{media_id}.mp4", ext="mp4")]
        )
```

---

## 🧪 Running Tests

```bash
# Run all 58 comprehensive unit & integration tests
python3 -m unittest discover -s tests -v
```

---

## 📄 License
MIT License. Free for personal, commercial, and open-source use.
