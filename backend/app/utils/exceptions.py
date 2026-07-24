"""
Custom exceptions for Page Pulse.

Each exception carries the HTTP status code it should be reported as,
per API_SPEC.md:
    400 Invalid URL
    408 Timeout
    415 Non HTML
    500 Internal Server Error
"""


class PagePulseError(Exception):
    """Base class for all handled Page Pulse errors."""

    status_code: int = 500
    message: str = "Internal Server Error"

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


class InvalidURLError(PagePulseError):
    status_code = 400
    message = "The provided URL is invalid."


class FetchTimeoutError(PagePulseError):
    status_code = 408
    message = "The request to the target URL timed out."


class NonHTMLContentError(PagePulseError):
    status_code = 415
    message = "The target URL did not return an HTML document."


class UpstreamFetchError(PagePulseError):
    """
    Raised for connection failures, DNS errors, too many redirects, etc.
    that occur while contacting the target URL.
    """

    status_code = 500
    message = "Failed to fetch the target URL."
