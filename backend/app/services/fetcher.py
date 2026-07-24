"""Fetches a target URL and captures raw response data + timing."""

import time
from dataclasses import dataclass

import requests

from app.utils.exceptions import FetchTimeoutError, NonHTMLContentError, UpstreamFetchError

# Seconds to wait for a connection + response before giving up.
REQUEST_TIMEOUT = 10

# Maximum response size allowed (5 MB)
MAX_RESPONSE_BYTES = 5 * 1024 * 1024

# A generic UA avoids some sites blocking requests with no User-Agent header.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; PagePulseBot/1.0; "
        "+https://digitalheroesco.com)"
    )
}


@dataclass
class FetchResult:
    status_code: int
    response_time: float
    html: str


def fetch_url(url: str) -> FetchResult:
    """
    Fetch `url` and return its status code, elapsed time, and HTML body.

    Raises:
        FetchTimeoutError: if the request exceeds REQUEST_TIMEOUT.
        NonHTMLContentError: if the response is not an HTML document.
        UpstreamFetchError: for connection errors, DNS failures, size limits, etc.
    """
    start = time.perf_counter()
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
            stream=True,
        )
    except requests.exceptions.Timeout as exc:
        raise FetchTimeoutError(f"Request to {url} timed out after {REQUEST_TIMEOUT}s.") from exc
    except requests.exceptions.RequestException as exc:
        raise UpstreamFetchError(f"Could not reach {url}: {exc}") from exc

    elapsed = round(time.perf_counter() - start, 3)

    content_type = response.headers.get("Content-Type", "")
    if "html" not in content_type.lower():
        response.close()
        raise NonHTMLContentError(
            f"Expected an HTML document but received Content-Type '{content_type or 'unknown'}'."
        )

    # Stream response chunks up to MAX_RESPONSE_BYTES limit
    content_chunks = []
    downloaded_size = 0
    try:
        for chunk in response.iter_content(chunk_size=65536):
            downloaded_size += len(chunk)
            if downloaded_size > MAX_RESPONSE_BYTES:
                response.close()
                raise UpstreamFetchError(
                    f"Target response size exceeds maximum allowed limit ({MAX_RESPONSE_BYTES // (1024 * 1024)}MB)."
                )
            content_chunks.append(chunk)
    finally:
        response.close()

    raw_bytes = b"".join(content_chunks)

    # Robust encoding resolution
    encoding = response.encoding or response.apparent_encoding or "utf-8"
    try:
        html_text = raw_bytes.decode(encoding, errors="replace")
    except Exception:
        html_text = raw_bytes.decode("utf-8", errors="replace")

    return FetchResult(
        status_code=response.status_code,
        response_time=elapsed,
        html=html_text,
    )