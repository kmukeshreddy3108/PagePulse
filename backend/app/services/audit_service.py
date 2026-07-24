"""Orchestrates URL validation, fetching, and HTML analysis for an audit."""

from app.models.schemas import AuditResponse
from app.parser.html_parser import analyze_html
from app.services.fetcher import fetch_url
from app.utils.validators import validate_url


def run_audit(raw_url: str) -> AuditResponse:
    """
    Run a full audit on `raw_url` and return the assembled AuditResponse.

    Any invalid input, network failure, timeout, or non-HTML response
    raises a PagePulseError subclass, which the route layer translates
    into the appropriate HTTP error response.
    """
    url = validate_url(raw_url)
    fetch_result = fetch_url(url)
    metrics = analyze_html(fetch_result.html)

    return AuditResponse(
        status=fetch_result.status_code,
        response_time=fetch_result.response_time,
        page_title=metrics.page_title,
        meta_description=metrics.meta_description,
        h1_count=metrics.h1_count,
        images_missing_alt=metrics.images_missing_alt,
        word_count=metrics.word_count,
    )
