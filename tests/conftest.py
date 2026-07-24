"""Shared fixtures for the Page Pulse backend test suite."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """A TestClient wired to the real FastAPI app (no network calls made
    unless a test explicitly patches the fetch layer)."""
    return TestClient(app)


@pytest.fixture
def sample_html():
    """A small but representative HTML document covering every metric
    the parser extracts: title, meta description, multiple h1s, an
    image missing alt, and body text for the word count."""
    return """
    <html>
      <head>
        <title>  Sample Page  </title>
        <meta name="description" content="A page used for testing Page Pulse.">
      </head>
      <body>
        <h1>Welcome</h1>
        <h1>Second heading</h1>
        <img src="/logo.png" alt="Company logo">
        <img src="/banner.png">
        <img src="/icon.png" alt="">
        <p>This is some sample body copy used to check the word counter.</p>
        <script>console.log("ignored");</script>
      </body>
    </html>
    """
