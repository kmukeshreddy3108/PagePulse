"""Pydantic models for the /audit endpoint."""

from pydantic import BaseModel, Field


class AuditRequest(BaseModel):
    url: str = Field(
        ...,
        description="The webpage URL to audit.",
        examples=["https://example.com"],
    )


class AuditResponse(BaseModel):
    status: int = Field(..., description="HTTP status code returned by the target URL.")
    response_time: float = Field(..., description="Response time in seconds, rounded to 3 decimals.")
    page_title: str | None = Field(None, description="Contents of the <title> tag, if present.")
    meta_description: str | None = Field(None, description="Contents of the meta description tag, if present.")
    h1_count: int = Field(..., description="Number of <h1> elements on the page.")
    images_missing_alt: int = Field(..., description="Number of <img> tags missing an alt attribute.")
    word_count: int = Field(..., description="Approximate word count of visible page text.")


class ErrorResponse(BaseModel):
    detail: str
