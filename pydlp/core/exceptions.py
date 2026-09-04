"""Exception hierarchy for Py-dlp."""

from typing import Optional


class PyDLPError(Exception):
    """Base exception for all PyDLP errors."""

    def __init__(self, msg: str, orig_error: Optional[Exception] = None):
        super().__init__(msg)
        self.msg = msg
        self.orig_error = orig_error

    def __str__(self) -> str:
        if self.orig_error:
            return f"{self.msg} (caused by: {self.orig_error})"
        return self.msg


class ExtractorError(PyDLPError):
    """Raised when an extractor fails to parse media metadata."""

    def __init__(
        self,
        msg: str,
        expected: bool = False,
        video_id: Optional[str] = None,
        ie: Optional[str] = None,
        orig_error: Optional[Exception] = None,
    ):
        super().__init__(msg, orig_error=orig_error)
        self.expected = expected
        self.video_id = video_id
        self.ie = ie


class UnsupportedURLError(ExtractorError):
    """Raised when no extractor is found for the given URL."""

    def __init__(self, url: str):
        super().__init__(f"Unsupported URL: {url}", expected=True)
        self.url = url


class DownloadError(PyDLPError):
    """Raised when downloading a media stream fails."""
    pass


class FormatNotAvailableError(ExtractorError):
    """Raised when the requested format cannot be found."""
    pass


class PostProcessingError(PyDLPError):
    """Raised when a post-processing step fails."""
    pass


class NetworkError(PyDLPError):
    """Raised on network connection, timeout, or DNS issues."""
    pass


class AuthenticationError(ExtractorError):
    """Raised when authentication/credentials are missing or invalid."""
    pass


class GeoRestrictedError(ExtractorError):
    """Raised when content is blocked in the requester's geographical region."""
    pass


class UnavailableVideoError(ExtractorError):
    """Raised when media has been removed, deleted, or set to private."""
    pass


class LiveStreamError(ExtractorError):
    """Raised when trying to process an ongoing live stream improperly."""
    pass


class CancelRequested(PyDLPError):
    """Raised when a download task cancellation is signaled by user/controller."""
    pass
