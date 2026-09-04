<div align="center">

# ⚡ Py-dlp Studio

**The Ultimate, Next-Generation Media Extractor & Downloader Engine**

[![Version](https://img.shields.io/badge/version-2026.09.04-blue.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-brightgreen.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)
[![License](https://img.shields.io/badge/license-MIT-purple.svg?style=for-the-badge)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20(Pure%20Standard%20Library)-success.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)
[![Tests](https://img.shields.io/badge/tests-passing%20(68%2F68)-emerald.svg?style=for-the-badge)](https://github.com/Beasgohan-code/Py-dlp)

*A modular, blazing-fast, and complete media extraction and download engine engineered with zero required external dependencies, rich CLI formatting, adaptive turbo multi-connection chunking, HLS/DASH streaming, SponsorBlock removal, AI transcript summarization, and a built-in modern Web Studio Dashboard.*

---

</div>

## 🌟 What Sets Py-dlp Apart

- 🎯 **Zero Mandatory Dependencies**: Built 100% on Python's robust standard library (`urllib`, `concurrent.futures`, `http.client`, `json`, `xml`, `zipapp`, etc.). No bulky dependencies required.
- 🚀 **85+ Native Built-in Extractors**: Comprehensive support covering mainstream video platforms, Anime streaming, Adult video/cam networks, Cyberlockers & cloud storage, Global streaming/Live, and Music platforms.
- 📦 **Single-Binary Standalone Executable**: Generates zero-dependency standalone Unix/Linux/macOS binaries and cross-platform ZipApps via `python3 bundle.py`.
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
- 🔌 **Dynamic Plugin & Compatibility System (`pydlp.core.plugins`, `pydlp.compat.yt_dlp`)**:
  - Compatible with `yt-dlp` extractor conventions with zero modifications, and extendable via `@register_extractor`.
- 🌐 **Modern Web Studio GUI & REST API (`pydlp --serve`)**:
  - Embedded responsive Web UI with single/batch modes, live preview, SponsorBlock controls, and instant task progress updates.

---

## 📊 85+ Supported Extractors Across Categories

### 🎬 Mainstream Video & Social
- **YouTube** (`youtube.com/watch?v=...`, `youtu.be/...`, `youtube.com/shorts/...`, playlists & search)
- **TikTok** (`tiktok.com/@user/video/...`, `tiktok.com/v/...`)
- **Instagram** (`instagram.com/p/...`, `/reel/...`, `/tv/...`)
- **Twitter / X** (`twitter.com/.../status/...`, `x.com/.../status/...`)
- **Reddit** (`reddit.com/r/...`, `v.redd.it/...` with native DASH multiplexing)
- **Vimeo** (`vimeo.com/...`, `player.vimeo.com/video/...`)
- **Twitch** (`twitch.tv/...`, `clips.twitch.tv/...`)
- **Dailymotion** (`dailymotion.com/video/...`)
- **Facebook** (`facebook.com/watch/?v=...`, `facebook.com/reel/...`)
- **Rumble** (`rumble.com/v...`)
- **Bilibili** (`bilibili.com/video/BV...` / `av...`)
- **Pinterest** (`pinterest.com/pin/...`)
- **Threads** (`threads.net/@user/post/...`)
- **Bluesky** (`bsky.app/profile/.../post/...`)
- **Streamable** (`streamable.com/...`)
- **Likee & Triller** (`likee.video/@...`, `triller.co/@...`, `kwai.com/...`)
- **LinkedIn** (`linkedin.com/posts/...`, `linkedin.com/feed/...`, `linkedin.com/learning/...`)
- **Imgur** (`imgur.com/gallery/...`, `imgur.com/a/...`, `i.imgur.com/...`)
- **Giphy** (`giphy.com/gifs/...`, `media.giphy.com/...`)
- **9GAG** (`9gag.com/gag/...`)
- **Coub** (`coub.com/view/...`)
- **PeerTube** (`peertube.tv/videos/watch/...`)
- **Archive.org** (`archive.org/details/...`)

### 🎌 Anime & Animation Platforms
- **AnimePahe** (`animepahe.ru/play/...`, `animepahe.org/play/...`, `animepahe.com/play/...`)
- **Crunchyroll** (`crunchyroll.com/watch/...`, `crunchyroll.com/series/...`)
- **Aniwave / 9anime / Zoro / HiAnime** (`aniwave.to/watch/...`, `9anime.to/...`, `hianime.to/...`)
- **Gogoanime / Anitaku** (`gogoanime3.co/...`, `anitaku.to/...`, `anitaku.pe/...`)
- **HentaiHaven** (`hentaihaven.xxx/episode/...`, `hentaihaven.com/...`)
- **Hanime** (`hanime.tv/videos/hentai/...`)

### 🔒 Video Hosts & Cyberlockers
- **Streamtape** (`streamtape.com/v/...`, `streamtape.net/v/...`, `streamta.pe/v/...`)
- **Mixdrop** (`mixdrop.co/e/...`, `mixdrop.co/f/...`, `mixdrop.ag/...`)
- **Doodstream** (`doodstream.com/d/...`, `doodstream.com/e/...`, `dood.so/...`, `dood.pm/...`, `dood.li/...`)
- **Voe** (`voe.sx/e/...`, `voe.sx/...`, `reputationsickly.com/...`, `20demidistance4.com/...`)
- **Filemoon** (`filemoon.sx/e/...`, `filemoon.sx/d/...`, `filemoon.to/...`, `vidcloud.co/...`)
- **StreamSB / SBVideo** (`streamsb.net/e/...`, `sbembed.com/e/...`, `watchsb.com/e/...`, `playersb.com/e/...`)
- **Google Drive & Dropbox** (`drive.google.com/file/d/...`, `dropbox.com/s/...`)
- **MediaFire & Mega** (`mediafire.com/file/...`, `mega.nz/file/...`, `mega.co.nz/...`)

### 📡 Global Streaming, Live & Enterprise
- **Kick** (`kick.com/...`, `kick.com/video/...`, `kick.com/clips/...`)
- **NicoNico Douga** (`nicovideo.jp/watch/sm...`, `sp.nicovideo.jp/...`)
- **AbemaTV** (`abema.tv/channels/...`, `abema.tv/video/title/...`, `abema.tv/video/episode/...`)
- **Douyin / Kuaishou / XiaoHongShu** (`douyin.com/video/...`, `iesdouyin.com/share/video/...`, `kuaishou.com/...`, `xiaohongshu.com/...`)
- **Odysee & LBRY** (`odysee.com/@...`, `lbry.tv/...`)
- **BitChute** (`bitchute.com/video/...`, `bitchute.com/channel/...`)
- **DTube** (`d.tube/#!/v/...`)
- **VK & VK Video** (`vk.com/video...`, `vkvideo.ru/...`, `vk.com/wall...`)
- **Loom** (`loom.com/share/...`)
- **Wistia** (`fast.wistia.net/embed/iframe/...`, `wistia.com/...`)
- **Brightcove** (`players.brightcove.net/...`, `brightcove.com/...`)
- **JWPlayer** (`content.jwplatform.com/videos/...`, `cdn.jwplayer.com/players/...`)
- **Vidyard & Brighteon** (`share.vidyard.com/watch/...`, `brighteon.com/...`)
- **TED Talks** (`ted.com/talks/...`)
- **Nebula & Floatplane** (`nebula.tv/videos/...`, `floatplane.com/post/...`)

### 🎵 Music & Audio Platforms
- **Spotify** (`open.spotify.com/track/...`, `/album/...`, `/playlist/...`)
- **SoundCloud** (`soundcloud.com/artist/track`, `/sets/...`)
- **Deezer** (`deezer.com/track/...`, `deezer.com/album/...`, `deezer.page.link/...`)
- **Apple Podcasts & Apple Music** (`podcasts.apple.com/...`, `music.apple.com/...`)
- **Tidal** (`tidal.com/browse/track/...`, `listen.tidal.com/...`)
- **Mixcloud** (`mixcloud.com/artist/show-name/`)
- **Audiomack** (`audiomack.com/artist/song/...`, `audiomack.com/artist/album/...`)
- **Bandcamp** (`artist.bandcamp.com/track/...`, `/album/...`)
- **Freesound, Hearthis.at & Jamendo** (`freesound.org/people/...`, `hearthis.at/...`, `jamendo.com/...`)
- **Podcast / RSS** (`feeds.podcast.com/rss`, `*.rss`, `*.xml`)

### 🔞 Adult Platforms & Live Cam Networks
- **Pornhub** (`pornhub.com/view_video.php?viewkey=...`, `pornhubpremium.com/...`)
- **XVideos & XNXX** (`xvideos.com/video...`, `xnxx.com/video...`)
- **XHamster** (`xhamster.com/videos/...`, `xhamster.desi/movies/...`, `xhamster.one/...`)
- **YouJizz** (`youjizz.com/videos/...`)
- **SpankBang** (`spankbang.com/.../video/...`)
- **RedTube & YouPorn** (`redtube.com/...`, `youporn.com/watch/...`)
- **EPorner** (`eporner.com/video/...`)
- **Motherless** (`motherless.com/...`)
- **Beeg** (`beeg.com/...`)
- **Tube8** (`tube8.com/...`)
- **TnaFlix & EmpFlix** (`tnaflix.com/video...`, `empflix.com/...`)
- **PornTrex** (`porntrex.com/videos/...`)
- **Thumbzilla** (`thumbzilla.com/video/...`)
- **ManyVids** (`manyvids.com/Video/...`)
- **Fapello** (`fapello.com/user/id/`)
- **Cumlouder & Daftsex** (`cumlouder.com/video/...`, `daftsex.com/watch/...`)
- **Chaturbate & Stripchat** (`chaturbate.com/room/...`, `stripchat.com/...`)
- **CamSoda, Cam4 & LiveJasmin** (`camsoda.com/...`, `cam4.com/...`, `livejasmin.com/...`)
- **Rule34Video** (`rule34video.party/videos/...`)
- **HQPorner & BongaCams** (`hqporner.com/hdporn/...`, `bongacams.com/...`)

### 🌐 Universal Fallback
- **Generic** (Any web page via HTML5 video/audio, OpenGraph meta, HLS `.m3u8`, DASH `.mpd`, schema.org)

### 🌐 Universal Fallback
- **Generic** (Any web page via HTML5 video/audio, OpenGraph meta, HLS `.m3u8`, DASH `.mpd`, schema.org)

---

## 🚀 Quick Start (CLI)

```bash
# Basic download
pydlp "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Turbo multi-connection acceleration (dynamic speed auto-tuning)
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

# List all supported extractors
pydlp --list-extractors

# Launch the Web Studio Dashboard & REST API
pydlp --serve --port 8000
```

---

## 📦 Standalone Executable & Distribution

Py-dlp includes a self-contained ZipApp packaging tool that bundles the entire library and CLI into an executable single-file binary with zero dependencies:

```bash
# Generate standalone executable 'dist/pydlp'
python3 bundle.py

# Run standalone binary directly anywhere with Python 3:
./dist/pydlp "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Build all distribution artifacts (sdist, wheel, standalone binary):
python3 devscripts/build_dist.py
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

### ⚡ Asynchronous Python SDK

```python
import asyncio
from pydlp import AsyncPyDLP

async def main():
    async_dlp = AsyncPyDLP({"turbo": True})
    info = await async_dlp.extract_info("https://soundcloud.com/artist/track", download=True)
    print("Downloaded async:", info.title)

asyncio.run(main())
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
# Run all 64 comprehensive unit & integration tests
python3 -m unittest discover -s tests -v
```

---

## 📄 License
MIT License. Free for personal, commercial, and open-source use.
