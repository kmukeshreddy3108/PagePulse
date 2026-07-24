import pytest
from app.services.parser import parse_html


def test_parse_html_complete_page():
    """Test parsing complete HTML with title, meta description, h1 tags, images, and body text."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Sample Page Title</title>
        <meta name="description" content="This is a sample meta description for testing.">
    </head>
    <body>
        <h1>Primary Main Heading</h1>
        <p>This is the first paragraph of content on the page to test word count.</p>
        <img src="logo.png" alt="Company Logo" />
        <img src="banner.png" />
        <img src="icon.png" alt="" />
    </body>
    </html>
    """

    result = parse_html(html_content)

    assert result["page_title"] == "Sample Page Title"
    assert result["meta_description"] == "This is a sample meta description for testing."
    assert result["h1_count"] == 1
    assert result["images_missing_alt"] == 2  # missing alt or empty alt
    assert result["word_count"] > 0


def test_parse_html_missing_title_and_meta():
    """Test parsing HTML without title or meta description."""
    html_content = """
    <html>
    <body>
        <h1>Heading 1</h1>
        <h1>Heading 2</h1>
        <p>Short text body</p>
    </body>
    </html>
    """

    result = parse_html(html_content)

    assert result["page_title"] is None or result["page_title"] == ""
    assert result["meta_description"] is None or result["meta_description"] == ""
    assert result["h1_count"] == 2
    assert result["images_missing_alt"] == 0
    assert result["word_count"] >= 3


def test_parse_html_empty_body():
    """Test parsing minimal or empty HTML content."""
    html_content = "<html><head></head><body></body></html>"

    result = parse_html(html_content)

    assert result["h1_count"] == 0
    assert result["images_missing_alt"] == 0
    assert result["word_count"] == 0