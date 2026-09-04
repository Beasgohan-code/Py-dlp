"""Distributed Swarm Downloader for Py-dlp.

Enables distributed fragment downloading across multiple remote worker nodes.
"""

from __future__ import annotations

import concurrent.futures
import json
import logging
import urllib.request
from typing import Any, Dict, List, Optional

logger = logging.getLogger("pydlp.swarm")


class SwarmNode:
    """Represents a remote worker node capable of downloading byte ranges."""

    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url.rstrip("/")

    def ping(self) -> bool:
        """Check if node is responsive."""
        try:
            req = urllib.request.Request(f"{self.endpoint_url}/api/status")
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def fetch_chunk(self, url: str, start_byte: int, end_byte: int) -> Optional[bytes]:
        """Request worker node to download and return segment bytes."""
        payload = json.dumps({"url": url, "range": [start_byte, end_byte]}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.endpoint_url}/api/fetch_chunk",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                return resp.read()
        except Exception as e:
            logger.warning(f"[swarm] Failed chunk fetch from {self.endpoint_url}: {e}")
            return None


class SwarmClusterManager:
    """Coordinates parallel distributed downloads across registered worker nodes."""

    def __init__(self, node_urls: Optional[List[str] | str] = None):
        self.nodes: List[SwarmNode] = []
        if node_urls:
            if isinstance(node_urls, str):
                urls = [u.strip() for u in node_urls.split(",") if u.strip()]
            else:
                urls = list(node_urls)
            for u in urls:
                self.nodes.append(SwarmNode(u))

    @property
    def has_active_nodes(self) -> bool:
        return len(self.nodes) > 0

    def get_healthy_nodes(self) -> List[SwarmNode]:
        """Returns list of online responding nodes."""
        healthy = []
        for node in self.nodes:
            if node.ping():
                healthy.append(node)
        return healthy
