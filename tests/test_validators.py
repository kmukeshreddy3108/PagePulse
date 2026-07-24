"""Unit tests for app.utils.validators.validate_url."""

import pytest

from app.utils.exceptions import InvalidURLError
from app.utils.validators import validate_url


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "http://example.com",
        "https://example.com/path?query=1",
        "http://localhost:8000",
        "  https://example.com  ",  # surrounding whitespace should be trimmed
    ],
)
def test_validate_url_accepts_well_formed_urls(url):
    result = validate_url(url)
    assert result == url.strip()


@pytest.mark.parametrize(
    "url",
    [
        "",
        "   ",
        "not-a-url",
        "ftp://example.com",
        "example.com",  # missing scheme
        "http://",  # missing host
        "http://abc",  # no dot, not localhost
        None,
    ],
)
def test_validate_url_rejects_invalid_urls(url):
    with pytest.raises(InvalidURLError):
        validate_url(url)


def test_invalid_url_error_carries_400_status_code():
    try:
        validate_url("not-a-url")
    except InvalidURLError as exc:
        assert exc.status_code == 400
    else:
        pytest.fail("InvalidURLError was not raised")
