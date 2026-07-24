"""Integration tests for the POST /audit endpoint.

The network-facing fetch_url() is patched at its import site inside
app.services.audit_service so these tests exercise the full request/response
cycle (validation -> service -> parser -> schema -> HTTP response) without
ever making a real network call.
"""

from unittest.mock import patch

from app.services.fetcher import FetchResult
from app.utils.exceptions import FetchTimeoutError, NonHTMLContentError, UpstreamFetchError

PATCH_TARGET = "app.services.audit_service.fetch_url"


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_audit_happy_path_returns_full_metrics(client, sample_html):
    fake_result = FetchResult(status_code=200, response_time=0.245, html=sample_html)

    with patch(PATCH_TARGET, return_value=fake_result) as mock_fetch:
        response = client.post("/audit", json={"url": "https://example.com"})

    mock_fetch.assert_called_once_with("https://example.com")
    assert response.status_code == 200

    body = response.json()
    assert body == {
        "status": 200,
        "response_time": 0.245,
        "page_title": "Sample Page",
        "meta_description": "A page used for testing Page Pulse.",
        "h1_count": 2,
        "images_missing_alt": 2,
        "word_count": 17,
    }


def test_audit_happy_path_passes_through_target_error_status(client):
    """A target page returning 404 is still a successful audit (200 from
    our API) -- the 404 is reported as data in the `status` field."""
    fake_result = FetchResult(status_code=404, response_time=0.1, html="<html><body>Not found</body></html>")

    with patch(PATCH_TARGET, return_value=fake_result):
        response = client.post("/audit", json={"url": "https://example.com/missing"})

    assert response.status_code == 200
    assert response.json()["status"] == 404


# ---------------------------------------------------------------------------
# Invalid URL (400) -- caught before fetch_url is ever called
# ---------------------------------------------------------------------------


def test_audit_invalid_url_returns_400(client):
    with patch(PATCH_TARGET) as mock_fetch:
        response = client.post("/audit", json={"url": "not-a-url"})

    mock_fetch.assert_not_called()
    assert response.status_code == 400
    assert "detail" in response.json()


def test_audit_missing_url_field_returns_400(client):
    response = client.post("/audit", json={})
    assert response.status_code == 400
    assert "detail" in response.json()


def test_audit_empty_url_returns_400(client):
    response = client.post("/audit", json={"url": "   "})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Timeout (408)
# ---------------------------------------------------------------------------


def test_audit_timeout_returns_408(client):
    with patch(PATCH_TARGET, side_effect=FetchTimeoutError("Request to https://slow.example timed out after 10s.")):
        response = client.post("/audit", json={"url": "https://slow.example"})

    assert response.status_code == 408
    assert "timed out" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Non-HTML content (415)
# ---------------------------------------------------------------------------


def test_audit_non_html_returns_415(client):
    with patch(PATCH_TARGET, side_effect=NonHTMLContentError("Expected an HTML document but received 'application/json'.")):
        response = client.post("/audit", json={"url": "https://api.example.com/data.json"})

    assert response.status_code == 415
    assert "html" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Upstream / unexpected failures (500)
# ---------------------------------------------------------------------------


def test_audit_upstream_failure_returns_500(client):
    with patch(PATCH_TARGET, side_effect=UpstreamFetchError("Could not reach https://unreachable.example.")):
        response = client.post("/audit", json={"url": "https://unreachable.example"})

    assert response.status_code == 500
    assert "detail" in response.json()


def test_audit_unhandled_exception_returns_500():
    """Any exception that isn't a PagePulseError still yields the
    documented 500 shape, thanks to the catch-all handler in main.py.

    A dedicated client with raise_server_exceptions=False is used here so
    the test observes the real HTTP response the handler produces, instead
    of TestClient re-raising the exception for debugging purposes.
    """
    from fastapi.testclient import TestClient

    from app.main import app

    lenient_client = TestClient(app, raise_server_exceptions=False)

    with patch(PATCH_TARGET, side_effect=RuntimeError("boom")):
        response = lenient_client.post("/audit", json={"url": "https://example.com"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
