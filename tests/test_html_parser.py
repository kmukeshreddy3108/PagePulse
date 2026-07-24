"""Unit tests for app.parser.html_parser.analyze_html."""

from app.parser.html_parser import analyze_html


def test_analyze_html_extracts_all_metrics(sample_html):
    metrics = analyze_html(sample_html)

    assert metrics.page_title == "Sample Page"
    assert metrics.meta_description == "A page used for testing Page Pulse."
    assert metrics.h1_count == 2
    # banner.png (no alt attr) + icon.png (alt="") are both missing alt text
    assert metrics.images_missing_alt == 2
    assert metrics.word_count == 17


def test_analyze_html_handles_missing_title_and_description():
    html = "<html><head></head><body><p>No metadata here.</p></body></html>"
    metrics = analyze_html(html)

    assert metrics.page_title is None
    assert metrics.meta_description is None
    assert metrics.h1_count == 0
    assert metrics.images_missing_alt == 0
    assert metrics.word_count == 3


def test_analyze_html_falls_back_to_og_description():
    html = """
    <html>
      <head>
        <meta property="og:description" content="Open Graph description.">
      </head>
      <body></body>
    </html>
    """
    metrics = analyze_html(html)
    assert metrics.meta_description == "Open Graph description."


def test_analyze_html_ignores_script_and_style_text():
    html = """
    <html>
      <body>
        <script>var shouldNotCount = "lots of hidden words here";</script>
        <style>.a { color: red; }</style>
        <p>Only these five words count.</p>
      </body>
    </html>
    """
    metrics = analyze_html(html)
    assert metrics.word_count == 5


def test_analyze_html_all_images_have_alt():
    html = '<html><body><img src="a.png" alt="A"><img src="b.png" alt="B"></body></html>'
    metrics = analyze_html(html)
    assert metrics.images_missing_alt == 0
