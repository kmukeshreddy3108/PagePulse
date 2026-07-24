"""Extracts audit metrics from an HTML document using BeautifulSoup."""

from dataclasses import dataclass
import re

from bs4 import BeautifulSoup


@dataclass
class AuditMetrics:
    page_title: str | None
    meta_description: str | None
    h1_count: int
    images_total: int
    images_missing_alt: int


def analyze_html(html_content: str) -> AuditMetrics:
    """
    Parse raw HTML content and extract standard SEO/a11y metrics.

    Metrics collected:
        - page_title: Content of <title>, trimmed. None if missing or empty.
        - meta_description: Content of <meta name="description"> or <meta property="og:description">.
        - h1_count: Number of <h1> elements.
        - images_total: Total number of <img> tags.
        - images_missing_alt: Number of <img> tags without an alt attribute (or empty string alt).
    """
    soup = BeautifulSoup(html_content, "html.parser")

    return AuditMetrics(
        page_title=_extract_page_title(soup),
        meta_description=_extract_meta_description(soup),
        h1_count=_count_h1s(soup),
        images_total=_count_total_images(soup),
        images_missing_alt=_count_missing_alt_images(soup),
    )


def _extract_page_title(soup: BeautifulSoup) -> str | None:
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        cleaned = title_tag.string.strip()
        return cleaned or None
    return None


def _extract_meta_description(soup: BeautifulSoup) -> str | None:
    # Case-insensitive lookup for name="description" or property="og:description"
    pattern = re.compile(r"^(description|og:description)$", re.I)
    tag = soup.find("meta", attrs={"name": pattern})
    if tag is None:
        tag = soup.find("meta", attrs={"property": pattern})
    if tag and tag.get("content"):
        content = tag["content"].strip()
        return content or None
    return None


def _count_h1s(soup: BeautifulSoup) -> int:
    return len(soup.find_all("h1"))


def _count_total_images(soup: BeautifulSoup) -> int:
    return len(soup.find_all("img"))


def _count_missing_alt_images(soup: BeautifulSoup) -> int:
    missing = 0
    for img in soup.find_all("img"):
        alt = img.get("alt")
        # Missing attribute OR attribute present but consists only of whitespace
        if alt is None or not alt.strip():
            missing += 1
    return missing