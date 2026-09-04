"""External downloader integration (aria2c, curl, wget, axel, ffmpeg) with auto-fallback."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import DownloadError
from pydlp.core.http import HttpClient
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo
from pydlp.downloader.base import BaseDownloader


class ExternalDownloader(BaseDownloader):
    """Executes downloads via external CLI tools (aria2c, curl, wget, axel, ffmpeg) when requested."""

    SUPPORTED_EXECUTABLES = ["aria2c", "curl", "wget", "axel", "ffmpeg"]

    def __init__(self, http_client: HttpClient, options: Optional[Dict[str, Any]] = None):
        super().__init__(http_client, options)
        self.downloader_name = self.options.get("external_downloader", "aria2c").lower()

    @classmethod
    def is_available(cls, name: str) -> bool:
        return shutil.which(name) is not None

    def _build_command(self, url: str, filename: str, headers: Dict[str, str]) -> List[str]:
        name = self.downloader_name
        part_name = f"{filename}.part"

        if name == "aria2c":
            cmd = [
                "aria2c",
                "--continue=true",
                "--max-connection-per-server=16",
                "--split=16",
                "--min-split-size=1M",
                f"--out={os.path.basename(part_name)}",
                f"--dir={os.path.dirname(part_name) or '.'}",
            ]
            for k, v in headers.items():
                cmd.append(f"--header={k}: {v}")
            cmd.append(url)
            return cmd

        elif name == "curl":
            cmd = ["curl", "-L", "-C", "-", "-o", part_name]
            for k, v in headers.items():
                cmd.extend(["-H", f"{k}: {v}"])
            cmd.append(url)
            return cmd

        elif name == "wget":
            cmd = ["wget", "-c", "-O", part_name]
            for k, v in headers.items():
                cmd.append(f"--header={k}: {v}")
            cmd.append(url)
            return cmd

        elif name == "axel":
            cmd = ["axel", "-n", "16", "-o", part_name]
            for k, v in headers.items():
                cmd.extend(["-H", f"{k}: {v}"])
            cmd.append(url)
            return cmd

        elif name == "ffmpeg":
            cmd = ["ffmpeg", "-y", "-i", url, "-c", "copy", part_name]
            return cmd

        else:
            raise DownloadError(f"Unsupported external downloader: {name}")

    def download(self, filename: str, info_dict: MediaInfo, fmt: MediaFormat) -> bool:
        if not fmt.url:
            raise DownloadError("Format has no URL to download")

        final_path, part_path = self._get_target_paths(filename)
        headers = dict(self.http.headers)
        if fmt.http_headers:
            headers.update(fmt.http_headers)

        if not self.is_available(self.downloader_name):
            # Fallback to internal HTTP downloader
            from pydlp.downloader.http import HttpDownloader
            fallback = HttpDownloader(self.http, self.options)
            for h in self.progress_dispatcher._hooks:
                fallback.add_progress_hook(h)
            return fallback.download(filename, info_dict, fmt)

        cmd = self._build_command(fmt.url, filename, headers)

        self.progress_dispatcher.dispatch(
            DownloadProgress(
                status="downloading",
                filename=final_path,
                downloaded_bytes=0,
                speed=0.0,
                eta=0,
                percentage=0.0,
            )
        )

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            stdout, stderr = proc.communicate()
            if proc.returncode != 0:
                # If external tool failed, try internal HTTP fallback
                from pydlp.downloader.http import HttpDownloader
                fallback = HttpDownloader(self.http, self.options)
                for h in self.progress_dispatcher._hooks:
                    fallback.add_progress_hook(h)
                return fallback.download(filename, info_dict, fmt)

            if os.path.exists(part_path) and part_path != final_path:
                os.replace(part_path, final_path)

            file_size = os.path.getsize(final_path) if os.path.exists(final_path) else 0
            self.progress_dispatcher.dispatch(
                DownloadProgress(
                    status="finished",
                    filename=final_path,
                    downloaded_bytes=file_size,
                    total_bytes=file_size,
                    speed=0.0,
                    eta=0,
                    percentage=100.0,
                )
            )
            return True

        except Exception as e:
            # Fallback to internal HTTP downloader
            from pydlp.downloader.http import HttpDownloader
            fallback = HttpDownloader(self.http, self.options)
            for h in self.progress_dispatcher._hooks:
                fallback.add_progress_hook(h)
            return fallback.download(filename, info_dict, fmt)
