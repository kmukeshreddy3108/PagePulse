import os
import time
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import httpx
from bs4 import BeautifulSoup

app = FastAPI(
    title="Page Pulse API",
    description="Backend API for auditing webpage health, structure, and performance metrics.",
    version="1.0.0"
)

# Configurable CORS origins (defaults to local dev and common production deployment domains)
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,https://*.vercel.app"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class AuditRequest(BaseModel):
    url: str

class AuditResponse(BaseModel):
    status: int
    response_time: float
    page_title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_count: int
    images_missing_alt: int
    word_count: int

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/audit", response_model=AuditResponse)
async def run_audit(payload: AuditRequest):
    raw_url = payload.url.strip() if payload.url else ""
    if not raw_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must not be empty."
        )

    if not (raw_url.startswith("http://") or raw_url.startswith("https://")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must start with http:// or https://."
        )

    start_time = time.perf_counter()
    timeout = httpx.Timeout(10.0, connect=5.0)
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PagePulseBot/1.0; +https://digitalheroesco.com)"
    }

    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
        try:
            response = await client.get(raw_url, headers=headers)
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail=f"Request to {raw_url} timed out after 10s."
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not reach {raw_url}: {str(exc)}"
            )

    elapsed_time = round(time.perf_counter() - start_time, 3)

    content_type = response.headers.get("content-type", "").lower()
    if "html" not in content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expected an HTML document but received Content-Type '{content_type || 'unknown'}'."
        )

    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    title_tag = soup.find("title")
    page_title = title_tag.get_text().strip() if title_tag and title_tag.get_text().strip() else None

    meta_tag = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "description"}) or \
               soup.find("meta", attrs={"property": lambda x: x and x.lower() == "og:description"})
    meta_description = meta_tag.get("content", "").strip() if meta_tag and meta_tag.get("content") else None

    h1_count = len(soup.find_all("h1"))

    images = soup.find_all("img")
    images_missing_alt = sum(
        1 for img in images if not img.get("alt") or not img.get("alt").strip()
    )

    for script_or_style in soup(["script", "style", "noscript", "svg", "iframe"]):
        script_or_style.decompose()

    body_text = soup.get_text()
    words = [w for w in body_text.split() if w]
    word_count = len(words)

    return AuditResponse(
        status=response.status_code,
        response_time=elapsed_time,
        page_title=page_title,
        meta_description=meta_description,
        h1_count=h1_count,
        images_missing_alt=images_missing_alt,
        word_count=word_count
    )