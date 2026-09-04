"""Remote Cloud and Storage Auto-Uploader for Py-dlp.

Supports uploading finished downloads to:
- S3 / Cloudflare R2 / MinIO / Backblaze B2 (via HTTP REST API / PUT)
- WebDAV servers (Nextcloud, ownCloud)
- FTP / SFTP servers
"""

from __future__ import annotations

import ftplib
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
import urllib.parse
import urllib.request

from pydlp.core.types import MediaInfo
from pydlp.postprocessor.base import BasePostProcessor

logger = logging.getLogger("pydlp.cloud_uploader")


class CloudUploaderPostProcessor(BasePostProcessor):
    """Auto-uploads downloaded files to remote cloud destinations."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.s3_endpoint = self.options.get("upload_s3")
        self.webdav_url = self.options.get("upload_webdav")
        self.ftp_url = self.options.get("upload_ftp")

    @property
    def is_needed(self) -> bool:
        return bool(self.s3_endpoint or self.webdav_url or self.ftp_url)

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        if not self.is_needed or not info.filepath or not os.path.isfile(info.filepath):
            return [], info

        if self.s3_endpoint:
            self.upload_s3(info.filepath, self.s3_endpoint)
        if self.webdav_url:
            self.upload_webdav(info.filepath, self.webdav_url)
        if self.ftp_url:
            self.upload_ftp(info.filepath, self.ftp_url)

        return [], info

    def upload_s3(self, filepath: str, endpoint: str) -> bool:
        """Upload to S3/R2 presigned or direct REST endpoint."""
        filename = os.path.basename(filepath)
        target_url = endpoint if endpoint.endswith(filename) else f"{endpoint.rstrip('/')}/{filename}"
        logger.info(f"[cloud] Uploading {filename} to S3 endpoint {target_url}...")
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            req = urllib.request.Request(target_url, data=data, method="PUT")
            req.add_header("Content-Type", "application/octet-stream")
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                logger.info(f"[cloud] S3 upload succeeded (Status {resp.status})")
                return True
        except Exception as e:
            logger.warning(f"[cloud] S3 upload error: {e}")
            return False

    def upload_webdav(self, filepath: str, webdav_url: str) -> bool:
        """Upload to WebDAV server (Nextcloud, ownCloud)."""
        filename = os.path.basename(filepath)
        target_url = webdav_url if webdav_url.endswith(filename) else f"{webdav_url.rstrip('/')}/{filename}"
        logger.info(f"[cloud] Uploading {filename} to WebDAV {target_url}...")
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            req = urllib.request.Request(target_url, data=data, method="PUT")
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                logger.info(f"[cloud] WebDAV upload succeeded (Status {resp.status})")
                return True
        except Exception as e:
            logger.warning(f"[cloud] WebDAV upload error: {e}")
            return False

    def upload_ftp(self, filepath: str, ftp_url: str) -> bool:
        """Upload to FTP server."""
        filename = os.path.basename(filepath)
        logger.info(f"[cloud] Uploading {filename} to FTP...")
        try:
            parsed = urllib.parse.urlparse(ftp_url)
            ftp = ftplib.FTP(parsed.hostname or "localhost")
            if parsed.username:
                ftp.login(parsed.username, parsed.password or "")
            else:
                ftp.login()

            with open(filepath, "rb") as f:
                ftp.storbinary(f"STOR {filename}", f)
            ftp.quit()
            logger.info(f"[cloud] FTP upload succeeded: {filename}")
            return True
        except Exception as e:
            logger.warning(f"[cloud] FTP upload error: {e}")
            return False
