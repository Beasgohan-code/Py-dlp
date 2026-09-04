"""Production-grade HTTP client engine for Py-dlp."""

from __future__ import annotations

import gzip
import http.client
import io
import json
import random
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from typing import Any, Callable, Dict, Generator, Optional, Tuple, Union

from pydlp.core.cookies import NetscapeCookieJar
from pydlp.core.exceptions import NetworkError

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


class RateLimiter:
    """Token-bucket rate limiter for bandwidth throttling."""

    def __init__(self, rate_bytes_per_sec: Optional[float] = None):
        self.rate = rate_bytes_per_sec  # bytes per second
        self.capacity = rate_bytes_per_sec or 0.0
        self.tokens = self.capacity
        self.last_update = time.monotonic()

    def limit(self, chunk_size: int) -> None:
        if not self.rate or self.rate <= 0:
            return
        now = time.monotonic()
        elapsed = now - self.last_update
        self.last_update = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        if self.tokens < chunk_size:
            deficit = chunk_size - self.tokens
            sleep_time = deficit / self.rate
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.tokens = 0
            self.last_update = time.monotonic()
        else:
            self.tokens -= chunk_size


class HttpResponse:
    """Encapsulates an HTTP response."""

    def __init__(
        self,
        raw_response: urllib.response.addinfourl,
        status_code: int,
        headers: Dict[str, str],
        url: str,
    ):
        self._raw = raw_response
        self.status_code = status_code
        self.headers = headers
        self.url = url
        self._content: Optional[bytes] = None

    def read(self, amt: Optional[int] = None) -> bytes:
        return self._raw.read(amt)

    @property
    def content(self) -> bytes:
        if self._content is None:
            raw_bytes = self._raw.read()
            encoding = self.headers.get("content-encoding", "").lower()
            if "gzip" in encoding or (len(raw_bytes) > 2 and raw_bytes[:2] == b"\x1f\x8b"):
                try:
                    self._content = gzip.decompress(raw_bytes)
                except Exception:
                    self._content = raw_bytes
            elif "deflate" in encoding:
                try:
                    self._content = zlib.decompress(raw_bytes)
                except Exception:
                    self._content = raw_bytes
            else:
                self._content = raw_bytes
        return self._content

    def text(self, encoding: Optional[str] = None) -> str:
        data = self.content
        if encoding:
            return data.decode(encoding, errors="replace")
        content_type = self.headers.get("content-type", "")
        if "charset=" in content_type:
            enc = content_type.split("charset=")[-1].split(";")[0].strip()
            try:
                return data.decode(enc, errors="replace")
            except LookupError:
                pass
        return data.decode("utf-8", errors="replace")

    def json(self) -> Any:
        return json.loads(self.text())

    def close(self) -> None:
        if self._raw:
            self._raw.close()

    def __enter__(self) -> HttpResponse:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()


class HttpClient:
    """Advanced HTTP client supporting streaming, retries, rate-limits, and proxies."""

    def __init__(
        self,
        user_agent: Optional[str] = None,
        timeout: float = 10.0,
        max_retries: int = 3,
        proxy: Optional[str] = None,
        verify_ssl: bool = True,
        rate_limit_bytes_per_sec: Optional[float] = None,
        cookie_jar: Optional[NetscapeCookieJar] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self.rate_limiter = RateLimiter(rate_limit_bytes_per_sec)
        self.cookie_jar = cookie_jar or NetscapeCookieJar()

        self.default_headers = dict(DEFAULT_HEADERS)
        if user_agent:
            self.default_headers["User-Agent"] = user_agent
        if headers:
            self.default_headers.update(headers)

        self._opener = self._build_opener()

    def _build_opener(self) -> urllib.request.OpenerDirector:
        handlers: list[urllib.request.BaseHandler] = []

        # Cookie handler
        handlers.append(urllib.request.HTTPCookieProcessor(self.cookie_jar))

        # SSL context
        ssl_ctx = ssl.create_default_context()
        if not self.verify_ssl:
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
        handlers.append(urllib.request.HTTPSHandler(context=ssl_ctx))

        # Proxy handler
        if self.proxy:
            handlers.append(
                urllib.request.ProxyHandler(
                    {
                        "http": self.proxy,
                        "https": self.proxy,
                    }
                )
            )

        return urllib.request.build_opener(*handlers)

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[bytes, str, Dict[str, Any]]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        byte_range: Optional[Tuple[int, Optional[int]]] = None,
    ) -> HttpResponse:
        """Executes an HTTP request with automatic retry and backoff."""
        timeout_val = timeout or self.timeout

        # Query params
        if params:
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            for k, v in params.items():
                qs[k] = [str(v)]
            new_query = urllib.parse.urlencode(qs, doseq=True)
            url = urllib.parse.urlunparse(parsed._replace(query=new_query))

        # Prepare payload
        body_bytes: Optional[bytes] = None
        req_headers = dict(self.default_headers)
        if headers:
            req_headers.update(headers)

        if data is not None:
            if isinstance(data, dict):
                body_bytes = urllib.parse.urlencode(data).encode("utf-8")
                req_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
            elif isinstance(data, str):
                body_bytes = data.encode("utf-8")
            elif isinstance(data, bytes):
                body_bytes = data

        if byte_range:
            start, end = byte_range
            range_header = f"bytes={start}-" if end is None else f"bytes={start}-{end}"
            req_headers["Range"] = range_header

        req = urllib.request.Request(
            url=url,
            data=body_bytes,
            headers=req_headers,
            method=method.upper(),
        )

        last_err: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._opener.open(req, timeout=timeout_val)
                resp_headers = {k.lower(): v for k, v in resp.headers.items()}
                return HttpResponse(
                    raw_response=resp,
                    status_code=resp.getcode() or 200,
                    headers=resp_headers,
                    url=resp.geturl(),
                )
            except urllib.error.HTTPError as e:
                # 4xx or 5xx
                if e.code in (403, 404, 410):
                    resp_headers = {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
                    return HttpResponse(raw_response=e, status_code=e.code, headers=resp_headers, url=url)
                last_err = e
                if attempt < self.max_retries:
                    backoff = (2**attempt) + random.uniform(0.1, 0.5)
                    time.sleep(backoff)
            except (urllib.error.URLError, http.client.HTTPException, ConnectionError, TimeoutError, OSError) as e:
                last_err = e
                if attempt < self.max_retries:
                    backoff = (2**attempt) + random.uniform(0.1, 0.5)
                    time.sleep(backoff)

        raise NetworkError(f"HTTP request to {url} failed after {self.max_retries} attempts: {last_err}", orig_error=last_err)

    def get(self, url: str, **kwargs: Any) -> HttpResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> HttpResponse:
        return self.request("POST", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> HttpResponse:
        return self.request("HEAD", url, **kwargs)

    def stream(
        self,
        url: str,
        chunk_size: int = 64 * 1024,
        headers: Optional[Dict[str, str]] = None,
        byte_range: Optional[Tuple[int, Optional[int]]] = None,
    ) -> Generator[bytes, None, None]:
        """Streams response body in chunks while applying rate limiting."""
        resp = self.request("GET", url, headers=headers, byte_range=byte_range)
        try:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                self.rate_limiter.limit(len(chunk))
                yield chunk
        finally:
            resp.close()
