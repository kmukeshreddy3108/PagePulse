import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import audit

app = FastAPI(
    title="Page Pulse API",
    description="Backend API for webpage health audit tool",
    version="1.0.0"
)

# Configurable CORS origins
raw_origins = os.getenv("ALLOWED_ORIGINS", "").strip()
if raw_origins and raw_origins != "*":
    origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(audit.router, prefix="/api")


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Page Pulse API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}