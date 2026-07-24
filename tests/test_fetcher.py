"""Unit tests for app.services.fetcher.fetch_url.

requests.get is mocked throughout so these tests never touch the network.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from app.services.fetcher import fetch_url
from app.utils.exceptions import FetchTimeoutError, NonHTMLContentError, UpstreamFetchError


def _mock_response(status_code=200, content_type="text/html; charset=utf-8", text="<html></html>"):
    mock_resp = Mock()
    mock_resp.status_code = status_code
    mock_resp.headers = {"Content-Type": content_type}
    mock_resp.text = text
    return mock_resp


@patch("app.services.fetcher.requests.get")
def test_fetch_url_happy_path(mock_get):
    mock_get.return_value = _mock_response(status_code=200, text="<html><body>Hi</body></html>")

    result = fetch_url("https://example.com")

    assert result.status_code == 200
    assert result.html == "<html><body>Hi</body></html>"
    assert isinstance(result.response_time, float)
    assert result.response_time >= 0
    mock_get.assert_called_once()


@patch("app.services.fetcher.requests.get")
def test_fetch_url_passes_through_non_2xx_status(mock_get):
    """A 404/500 from the target site is data, not a Page Pulse error."""
    mock_get.return_value = _mock_response(status_code=404)

    result = fetch_url("https://example.com/missing")

    assert result.status_code == 404


@patch("app.services.fetcher.requests.get")
def test_fetch_url_raises_timeout_error_on_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout("timed out")

    with pytest.raises(FetchTimeoutError):
        fetch_url("https://example.com")


@patch("app.services.fetcher.requests.get")
def test_fetch_url_raises_upstream_error_on_connection_failure(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("dns failure")

    with pytest.raises(UpstreamFetchError):
        fetch_url("https://unreachable.example")


@patch("app.services.fetcher.requests.get")
def test_fetch_url_raises_non_html_error_for_json_response(mock_get):
    mock_get.return_value = _mock_response(content_type="application/json", text='{"a": 1}')

    with pytest.raises(NonHTMLContentError):
        fetch_url("https://api.example.com/data")


@patch("app.services.fetcher.requests.get")
def test_fetch_url_raises_non_html_error_when_content_type_missing(mock_get):
    mock_resp = _mock_response()
    mock_resp.headers = {}  # no Content-Type header at all
    mock_get.return_value = mock_resp

    with pytest.raises(NonHTMLContentError):
        fetch_url("https://example.com/file")
