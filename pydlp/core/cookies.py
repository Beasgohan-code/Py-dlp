"""Cookie management and parsing utilities for Py-dlp."""

from __future__ import annotations

import http.cookiejar
import os
import re
from typing import Dict, List, Optional


class NetscapeCookieJar(http.cookiejar.MozillaCookieJar):
    """Custom MozillaCookieJar that handles non-standard and comment variations gracefully."""

    def load_from_file(self, filename: str, ignore_discard: bool = True, ignore_expires: bool = True) -> None:
        """Loads cookies from a Netscape/Mozilla formatted cookies text file."""
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Cookie file not found: {filename}")
        self.filename = filename
        self.load(filename, ignore_discard=ignore_discard, ignore_expires=ignore_expires)

    def load_from_string(self, content: str) -> None:
        """Parses cookies directly from a Netscape cookies format string."""
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("# ") or (line.startswith("#") and not line.startswith("#HttpOnly_")):
                continue

            http_only = False
            if line.startswith("#HttpOnly_"):
                http_only = True
                line = line[len("#HttpOnly_"):]

            fields = line.split("\t")
            if len(fields) < 7:
                continue

            domain, domain_specified, path, secure, expires, name, value = fields[:7]
            try:
                exp_int = int(expires) if expires else None
            except ValueError:
                exp_int = None

            cookie = http.cookiejar.Cookie(
                version=0,
                name=name,
                value=value,
                port=None,
                port_specified=False,
                domain=domain,
                domain_specified=domain_specified.upper() == "TRUE",
                domain_initial_dot=domain.startswith("."),
                path=path,
                path_specified=bool(path),
                secure=secure.upper() == "TRUE",
                expires=exp_int,
                discard=False,
                comment=None,
                comment_url=None,
                rest={"HttpOnly": ""} if http_only else {},
            )
            self.set_cookie(cookie)


def parse_cookie_header(header_value: str) -> Dict[str, str]:
    """Parses a Cookie: header string into key-value pairs."""
    cookies = {}
    for item in header_value.split(";"):
        if "=" in item:
            k, v = item.strip().split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies


def build_cookie_header(cookies: Dict[str, str]) -> str:
    """Builds a Cookie: header string from key-value pairs."""
    return "; ".join(f"{k}={v}" for k, v in cookies.items())
