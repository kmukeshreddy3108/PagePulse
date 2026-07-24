"""POST /audit endpoint."""

from fastapi import APIRouter

from app.models.schemas import AuditRequest, AuditResponse
from app.services.audit_service import run_audit

router = APIRouter()


@router.post(
    "/audit",
    response_model=AuditResponse,
    summary="Audit a webpage URL",
)
def audit_page(request: AuditRequest) -> AuditResponse:
    """
    Fetch and analyze the given URL, returning basic SEO/health metrics.

    Errors (invalid URL, timeout, non-HTML content, upstream failures) are
    raised as PagePulseError subclasses and handled globally in main.py.
    """
    return run_audit(request.url)
