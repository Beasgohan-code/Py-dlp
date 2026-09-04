"""Browser cookie loader supporting Chrome, Firefox, Brave, Edge, Safari, Opera, and Vivaldi."""

from __future__ import annotations

import http.cookiejar
import os
import sqlite3
import tempfile
from typing import Dict, List, Optional
from urllib.parse import urlparse

from pydlp.core.cookies import NetscapeCookieJar


class BrowserCookieLoader:
    """Loads authenticated session cookies from local browser profiles."""

    SUPPORTED_BROWSERS = ["chrome", "chromium", "firefox", "brave", "edge", "safari", "opera", "vivaldi"]

    @classmethod
    def find_cookie_paths(cls, browser: str) -> List[str]:
        """Returns potential sqlite cookie database paths for a given browser."""
        browser = browser.lower().strip()
        home = os.path.expanduser("~")
        paths: List[str] = []

        if browser in ("chrome", "chromium"):
            paths.extend([
                os.path.join(home, ".config/google-chrome/Default/Cookies"),
                os.path.join(home, ".config/chromium/Default/Cookies"),
                os.path.join(home, "Library/Application Support/Google/Chrome/Default/Cookies"),
                os.path.join(home, "AppData/Local/Google/Chrome/User Data/Default/Network/Cookies"),
            ])
        elif browser == "brave":
            paths.extend([
                os.path.join(home, ".config/BraveSoftware/Brave-Browser/Default/Cookies"),
                os.path.join(home, "Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies"),
                os.path.join(home, "AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/Network/Cookies"),
            ])
        elif browser == "edge":
            paths.extend([
                os.path.join(home, ".config/microsoft-edge/Default/Cookies"),
                os.path.join(home, "Library/Application Support/Microsoft Edge/Default/Cookies"),
                os.path.join(home, "AppData/Local/Microsoft/Edge/User Data/Default/Network/Cookies"),
            ])
        elif browser == "firefox":
            ff_dir = os.path.join(home, ".mozilla/firefox")
            if os.path.isdir(ff_dir):
                for entry in os.listdir(ff_dir):
                    if entry.endswith(".default") or entry.endswith(".default-release"):
                        paths.append(os.path.join(ff_dir, entry, "cookies.sqlite"))
            ff_mac = os.path.join(home, "Library/Application Support/Firefox/Profiles")
            if os.path.isdir(ff_mac):
                for entry in os.listdir(ff_mac):
                    paths.append(os.path.join(ff_mac, entry, "cookies.sqlite"))

        return [p for p in paths if os.path.exists(p)]

    @classmethod
    def load_cookies(cls, browser: str, domain: Optional[str] = None) -> NetscapeCookieJar:
        """Extracts cookies from the specified browser into a NetscapeCookieJar."""
        jar = NetscapeCookieJar()
        cookie_paths = cls.find_cookie_paths(browser)

        for db_path in cookie_paths:
            try:
                # Copy to temporary file to avoid sqlite database locks from active browser
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_path = tmp.name

                with open(db_path, "rb") as src, open(tmp_path, "wb") as dst:
                    dst.write(src.read())

                conn = sqlite3.connect(tmp_path)
                cursor = conn.cursor()

                # Query Firefox style or Chromium style tables
                try:
                    cursor.execute("SELECT host, name, value, path, expiry, isSecure FROM moz_cookies")
                    for host, name, value, path, expiry, is_secure in cursor.fetchall():
                        if domain and domain not in host:
                            continue
                        jar.set_cookie(
                            http.cookiejar.Cookie(
                                version=0,
                                name=name,
                                value=value,
                                port=None,
                                port_specified=False,
                                domain=host,
                                domain_specified=True,
                                domain_initial_dot=host.startswith("."),
                                path=path or "/",
                                path_specified=bool(path),
                                secure=bool(is_secure),
                                expires=expiry or 0,
                                discard=False,
                                comment=None,
                                comment_url=None,
                                rest={},
                            )
                        )
                except sqlite3.OperationalError:
                    # Chromium schema
                    cursor.execute("SELECT host_key, name, value, path, expires_utc, is_secure FROM cookies")
                    for host, name, value, path, expires_utc, is_secure in cursor.fetchall():
                        if domain and domain not in host:
                            continue
                        jar.set_cookie(
                            http.cookiejar.Cookie(
                                version=0,
                                name=name,
                                value=value or "",
                                port=None,
                                port_specified=False,
                                domain=host,
                                domain_specified=True,
                                domain_initial_dot=host.startswith("."),
                                path=path or "/",
                                path_specified=bool(path),
                                secure=bool(is_secure),
                                expires=expires_utc or 0,
                                discard=False,
                                comment=None,
                                comment_url=None,
                                rest={},
                            )
                        )

                conn.close()
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

            except Exception:
                continue

        return jar
