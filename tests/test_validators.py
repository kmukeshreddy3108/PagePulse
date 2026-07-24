import pytest
from app.services.validator import validate_url, is_private_ip, ValidationError


def test_validate_url_valid_public_urls():
    """Test that standard public HTTP/HTTPS URLs pass validation."""
    valid_urls = [
        "https://example.com",
        "http://example.com/path?query=1",
        "https://subdomain.digitalheroesco.com/page",
        "http://google.com",
    ]
    for url in valid_urls:
        assert validate_url(url) is True


def test_validate_url_rejects_localhost_and_private_ips():
    """Test that localhost, loopback, and private IP ranges are rejected to prevent SSRF."""
    private_urls = [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        "http://10.0.0.1",
        "http://172.16.0.1",
        "http://192.168.1.1",
        "http://169.254.169.254",  # Cloud metadata
        "http://[::1]",
        "http://0.0.0.0",
    ]
    for url in private_urls:
        with pytest.raises((ValueError, ValidationError)):
            validate_url(url)


def test_validate_url_rejects_invalid_schemes_and_malformed():
    """Test that non-HTTP schemes and malformed URLs are rejected."""
    invalid_urls = [
        "ftp://example.com",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "not_a_url",
        "http://",
        "",
        "   ",
    ]
    for url in invalid_urls:
        with pytest.raises((ValueError, ValidationError)):
            validate_url(url)


def test_is_private_ip_helper():
    """Test the private IP detection helper directly."""
    assert is_private_ip("127.0.0.1") is True
    assert is_private_ip("10.0.0.5") is True
    assert is_private_ip("192.168.0.1") is True
    assert is_private_ip("8.8.8.8") is False
    assert is_private_ip("1.1.1.1") is False