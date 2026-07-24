"""Page Pulse backend entrypoint."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes.audit import router as audit_router
from app.utils.exceptions import PagePulseError

app = FastAPI(
    title="Page Pulse API",
    description="Audits a webpage URL for basic SEO/health metrics.",
    version="1.0.0",
)

# Frontend is deployed separately (Vercel) from the backend (Render),
# so CORS must be open to the deployed frontend origin(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(PagePulseError)
async def page_pulse_error_handler(request: Request, exc: PagePulseError) -> JSONResponse:
    """Translate known application errors into their documented status codes."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Malformed request bodies (e.g. missing 'url') are treated as 400s."""
    return JSONResponse(status_code=400, content={"detail": "Invalid request payload."})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all so unexpected failures still return the documented 500 shape."""
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(audit_router)
