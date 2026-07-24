"""Extracts audit metrics from an HTML document using BeautifulSoup."""

from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass
class PageMetrics:
    page_title: str | None
    meta_description: str | None
    h1_count: int
    images_missing_alt: int
    word_count: int


def analyze_html(html: str) -> PageMetrics:
    soup = BeautifulSoup(html, "html.parser")

    page_title = _extract_title(soup)
    meta_description = _extract_meta_description(soup)
    h1_count = len(soup.find_all("h1"))
    images_missing_alt = _count_images_missing_alt(soup)
    word_count = _count_words(soup)

    return PageMetrics(
        page_title=page_title,
        meta_description=meta_description,
        h1_count=h1_count,
        images_missing_alt=images_missing_alt,
        word_count=word_count,
    )


def _extract_title(soup: BeautifulSoup) -> str | None:
    if soup.title and soup.title.string:
        text = soup.title.string.strip()
        return text or None
    return None


def _extract_meta_description(soup: BeautifulSoup) -> str | None:
    tag = soup.find("meta", attrs={"name": "description"})
    if tag is None:
        # Some pages use the Open Graph description instead.
        tag = soup.find("meta", attrs={"property": "og:description"})
    if tag and tag.get("content"):
        content = tag["content"].strip()
        return content or None
    return None


def _count_images_missing_alt(soup: BeautifulSoup) -> int:
    images = soup.find_all("img")
    missing = 0
    for img in images:
        alt = img.get("alt")
        if alt is None or alt.strip() == "":
            missing += 1
    return missing


def _count_words(soup: BeautifulSoup) -> int:
    # Strip non-visible/script content before counting words.
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    if not text:
        return 0
    return len(text.split())
