"""Webhook & Push Notification System for Py-dlp.

Supports Discord Webhooks (rich embeds), Telegram Bots, and generic HTTP POST endpoints.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional
import urllib.request

from pydlp.core.types import MediaInfo
from pydlp.core.utils import format_bytes, format_seconds

logger = logging.getLogger("pydlp.notifications")


class NotificationManager:
    """Manages notifications dispatched to Discord, Telegram, or custom Webhooks."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.webhook_url = self.options.get("notify_webhook")
        self.discord_url = self.options.get("notify_discord")
        self.telegram_target = self.options.get("notify_telegram")  # Format: "BOT_TOKEN:CHAT_ID"

    @property
    def is_enabled(self) -> bool:
        return bool(self.webhook_url or self.discord_url or self.telegram_target)

    def notify_download_start(self, info: MediaInfo) -> None:
        if not self.is_enabled:
            return

        title = info.title or "Unknown Title"
        uploader = info.uploader or "Unknown Uploader"
        duration = format_seconds(info.duration) if info.duration else "Unknown"

        # Discord
        if self.discord_url:
            embed = {
                "title": f"📥 Download Started: {title}",
                "description": f"**Uploader:** {uploader}\n**Duration:** {duration}\n**Extractor:** {info.extractor}",
                "color": 3447003,  # Blue
            }
            if info.thumbnail:
                embed["thumbnail"] = {"url": info.thumbnail}
            if info.webpage_url:
                embed["url"] = info.webpage_url
            self._send_discord(self.discord_url, {"embeds": [embed]})

        # Telegram
        if self.telegram_target:
            msg = f"📥 <b>Download Started</b>\n<b>Title:</b> {title}\n<b>Uploader:</b> {uploader}\n<b>Duration:</b> {duration}"
            self._send_telegram(self.telegram_target, msg)

        # Generic Webhook
        if self.webhook_url:
            payload = {
                "event": "download_start",
                "title": title,
                "uploader": uploader,
                "duration": info.duration,
                "url": info.webpage_url,
                "extractor": info.extractor,
            }
            self._send_generic_webhook(self.webhook_url, payload)

    def notify_download_complete(
        self, info: MediaInfo, output_path: str, elapsed_seconds: float, total_bytes: Optional[int] = None
    ) -> None:
        if not self.is_enabled:
            return

        title = info.title or "Unknown Title"
        uploader = info.uploader or "Unknown Uploader"
        duration = format_seconds(info.duration) if info.duration else "Unknown"
        size_str = format_bytes(total_bytes) if total_bytes else "Unknown"
        time_str = f"{elapsed_seconds:.1f}s"

        # Discord Embed
        if self.discord_url:
            embed = {
                "title": f"✅ Download Complete: {title}",
                "description": (
                    f"**File:** `{output_path}`\n"
                    f"**Uploader:** {uploader}\n"
                    f"**Size:** {size_str} | **Elapsed:** {time_str}\n"
                    f"**Duration:** {duration} | **Extractor:** {info.extractor}"
                ),
                "color": 5763719,  # Green
            }
            if info.thumbnail:
                embed["thumbnail"] = {"url": info.thumbnail}
            if info.webpage_url:
                embed["url"] = info.webpage_url
            self._send_discord(self.discord_url, {"embeds": [embed]})

        # Telegram
        if self.telegram_target:
            msg = (
                f"✅ <b>Download Complete!</b>\n"
                f"<b>Title:</b> {title}\n"
                f"<b>Uploader:</b> {uploader}\n"
                f"<b>Size:</b> {size_str}\n"
                f"<b>Elapsed:</b> {time_str}"
            )
            self._send_telegram(self.telegram_target, msg)

        # Generic Webhook
        if self.webhook_url:
            payload = {
                "event": "download_complete",
                "title": title,
                "output_path": output_path,
                "size_bytes": total_bytes,
                "elapsed_seconds": elapsed_seconds,
                "url": info.webpage_url,
                "extractor": info.extractor,
            }
            self._send_generic_webhook(self.webhook_url, payload)

    def notify_download_error(self, url: str, error_msg: str, title: Optional[str] = None) -> None:
        if not self.is_enabled:
            return

        title_display = title or url

        if self.discord_url:
            embed = {
                "title": f"❌ Download Failed: {title_display[:60]}",
                "description": f"**URL:** {url}\n**Error:** ```{error_msg[:1000]}```",
                "color": 15548997,  # Red
            }
            self._send_discord(self.discord_url, {"embeds": [embed]})

        if self.telegram_target:
            msg = f"❌ <b>Download Failed!</b>\n<b>Target:</b> {url}\n<b>Error:</b> {error_msg}"
            self._send_telegram(self.telegram_target, msg)

        if self.webhook_url:
            payload = {
                "event": "download_error",
                "url": url,
                "title": title,
                "error": error_msg,
            }
            self._send_generic_webhook(self.webhook_url, payload)

    def _send_discord(self, webhook_url: str, payload: dict) -> None:
        self._post_json(webhook_url, payload)

    def _send_telegram(self, target: str, text: str) -> None:
        # target formatted as "TOKEN:CHAT_ID"
        parts = target.split(":", 1)
        if len(parts) != 2:
            logger.warning("Invalid telegram target format. Expected TOKEN:CHAT_ID")
            return
        token, chat_id = parts
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }
        self._post_json(url, payload)

    def _send_generic_webhook(self, webhook_url: str, payload: dict) -> None:
        self._post_json(webhook_url, payload)

    def _post_json(self, url: str, payload: dict) -> None:
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "Py-dlp/Notifier"},
            )
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                pass
        except Exception as e:
            logger.debug(f"Notification send failed: {e}")
