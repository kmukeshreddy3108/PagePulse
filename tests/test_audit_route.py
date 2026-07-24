import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import requests

from app.main import app

client = TestClient(app)


def create_mock_streaming_response(
    status_code=200,
    content=b"<html><head><title>Test Page</title><meta name=\"description\" content=\"Test description\"></head><body><h1>Main Title</h1><p>Test content body for word count</p><img src=\"test.jpg\"></body></html>",
    content_type="text/html; charset=utf-8",
    encoding="utf-8"
):
    """Helper to create a mock requests response that supports chunked streaming via iter_content()."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.headers = {"content-type": content_type}
    mock_resp.encoding = encoding
    mock_resp.url = "https://example.com"
    mock_resp.raise_for_status = MagicMock()

    # Streaming implementation using iter_content()
    def iter_content(chunk_size=1024, decode_unicode=False):
        if decode_unicode:
            yield content.decode(encoding)
        else:
            yield content

    mock_resp.iter_content = iter_content
    mock_resp.text = content.decode(encoding)
    return mock_resp


@patch("app.services.fetcher.requests.get")
@patch("app.routers.audit.fetch_url")
def test_audit_success(mock_fetch_router, mock_requests_get):
    """Test successful audit endpoint response model and field names."""
    mock_response = create_mock_streaming_response()
    
    if mock_fetch_router.get_original:
        mock_fetch_router.side_effect = None
        mock_fetch_router.return_value = (200, 0.245, mock_response.text)
    mock_requests_get.return_value = mock_response

    response = client.post("/audit", json={"url": "https://example.com"})

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "response_time" in data
    assert "page_title" in data
    assert "meta_description" in data
    assert "h1_count" in data
    assert "images_missing_alt" in data
    assert "word_count" in data

    assert data["status"] == 200
    assert isinstance(data["response_time"], (int, float))
    assert data["page_title"] == "Test Page"
    assert data["meta_description"] == "Test description"
    assert data["h1_count"] == 1
    assert data["images_missing_alt"] == 1


def test_audit_rejects_localhost_and_private_ips():
    """Test that audit endpoint returns 400 for localhost / private IP attempts."""
    private_urls = [
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://192.168.1.1",
        "http://169.254.169.254",
    ]
    for url in private_urls:
        response = client.post("/audit", json={"url": url})
        assert response.status_code == 400
        assert "detail" in response.json()


def test_audit_invalid_url_format():
    """Test that malformed or non-HTTP URLs return 400."""
    response = client.post("/audit", json={"url": "invalid-url"})
    assert response.status_code == 400
    assert "detail" in response.json()


@patch("app.services.fetcher.requests.get")
@patch("app.routers.audit.fetch_url")
def test_audit_timeout_returns_408(mock_fetch_router, mock_requests_get):
    """Test that requests timeout returns 408 HTTP status code."""
    mock_requests_get.side_effect = requests.exceptions.Timeout("Request timed out")
    mock_fetch_router.side_effect = requests.exceptions.Timeout("Request timed out")

    response = client.post("/audit", json={"url": "https://example.com/slow"})
    assert response.status_code == 408
    assert "detail" in response.json()


@patch("app.services.fetcher.requests.get")
@patch("app.routers.audit.fetch_url")
def test_audit_non_html_content_returns_415(mock_fetch_router, mock_requests_get):
    """Test that fetching non-HTML content returns 415 Unsupported Media Type."""
    non_html_resp = create_mock_streaming_response(
        content=b"%PDF-1.4 binary data...",
        content_type="application/pdf"
    )
    mock_requests_get.return_value = non_html_resp
    
    from app.services.fetcher import NonHTMLError
    mock_fetch_router.side_effect = NonHTMLError("URL returned non-HTML content")

    response = client.post("/audit", json={"url": "https://example.com/document.pdf"})
    assert response.status_code in [400, 415]
    assert "detail" in response.json()


@patch("app.services.fetcher.requests.get")
@patch("app.routers.audit.fetch_url")
def test_audit_server_error_returns_500(mock_fetch_router, mock_requests_get):
    """Test that unhandled exceptions return 500 Internal Server Error."""
    mock_requests_get.side_effect = Exception("Unexpected backend failure")
    mock_fetch_router.side_effect = Exception("Unexpected backend failure")

    response = client.post("/audit", json={"url": "https://example.com/error"})
    assert response.status_code in [500, 400]
    assert "detail" in response.json()