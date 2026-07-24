"""URL validation helpers."""

from urllib.parse import urlparse

from app.utils.exceptions import InvalidURLError

_ALLOWED_SCHEMES = {"http", "https"}


def validate_url(raw_url: str) -> str:
    """
    Validate that `raw_url` is a well-formed, absolute http(s) URL.

    Returns the (stripped) URL on success, raises InvalidURLError otherwise.
    """
    if not raw_url or not raw_url.strip():
        raise InvalidURLError("URL must not be empty.")

    candidate = raw_url.strip()
    parsed = urlparse(candidate)

    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise InvalidURLError(
            "URL must start with http:// or https://."
        )

    if not parsed.netloc:
        raise InvalidURLError("URL is missing a valid domain/host.")

    # Reject hosts with no dot and no localhost-style usage, e.g. "http://abc"
    host = parsed.hostname or ""
    if "." not in host and host != "localhost":
        raise InvalidURLError("URL does not contain a valid domain.")

    return candidate
