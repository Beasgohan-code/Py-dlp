"""Continuous Playlist & Channel Watcher Daemon for Py-dlp.

Monitors playlists, channels, or RSS feeds continuously, downloading only new media items.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from pydlp.pydlp import PyDLP

logger = logging.getLogger("pydlp.watcher")


class WatcherDaemon:
    """Watches media feeds and downloads new releases automatically."""

    def __init__(self, pydlp_instance: PyDLP, urls: List[str], interval: int = 60, max_cycles: Optional[int] = None):
        self.pydlp = pydlp_instance
        self.urls = urls
        self.interval = max(5, interval)
        self.max_cycles = max_cycles
        self._running = True

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        """Main daemon loop."""
        cycle = 0
        self.pydlp.logger.info(f"[watcher] Starting Py-dlp Watcher Daemon (Interval: {self.interval}s)")
        self.pydlp.logger.info(f"[watcher] Monitoring {len(self.urls)} URL(s)... Press Ctrl+C to stop.")

        try:
            while self._running:
                cycle += 1
                self.pydlp.logger.info(f"[watcher] Checking cycle #{cycle} at {time.strftime('%Y-%m-%d %H:%M:%S')}...")

                for url in self.urls:
                    try:
                        self.pydlp.logger.info(f"[watcher] Checking target: {url}")
                        self.pydlp.download([url])
                    except Exception as e:
                        self.pydlp.logger.error(f"[watcher] Error checking {url}: {e}")

                if self.max_cycles and cycle >= self.max_cycles:
                    self.pydlp.logger.info(f"[watcher] Completed maximum cycles ({self.max_cycles}). Exiting.")
                    break

                self.pydlp.logger.info(f"[watcher] Cycle #{cycle} completed. Sleeping for {self.interval} seconds...")
                time.sleep(self.interval)

        except KeyboardInterrupt:
            self.pydlp.logger.info("\n[watcher] Watcher Daemon stopped by user.")
