"""URL validation helpers."""

import ipaddress
import socket
from urllib.parse import urlparse

from app.utils.exceptions import InvalidURLError

_ALLOWED_SCHEMES = {"http", "https"}


def _is_private_or_forbidden_host(hostname: str) -> bool:
    """Check if hostname is localhost, a private IP, or link-local address."""
    host_lower = hostname.lower().strip()

    if host_lower in {"localhost", "localhost.localdomain"} or host_lower.endswith(".localhost"):
        return True

    # Try parsing directly as an IP address
    try:
        ip = ipaddress.ip_address(host_lower)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_unspecified:
            return True
        return False
    except ValueError:
        pass

    # Try resolving domain to IP addresses to catch DNS rebinding or internal domain aliases
    try:
        addr_info = socket.getaddrinfo(host_lower, None)
        for _, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_unspecified:
                return True
    except (socket.gaierror, ValueError):
        pass

    return False


def validate_url(raw_url: str) -> str:
    """
    Validate that `raw_url` is a well-formed, absolute http(s) URL pointing to a public host.

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

    host = parsed.hostname or ""
    if not host:
        raise InvalidURLError("URL does not contain a valid host.")

    if _is_private_or_forbidden_host(host):
        raise InvalidURLError("Access to private/internal IP addresses or localhost is forbidden.")

    # Reject hosts with no dot and no localhost-style usage, e.g. "http://abc"
    if "." not in host and host != "localhost":
        raise InvalidURLError("URL does not contain a valid domain.")

    return candidate