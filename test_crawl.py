import unittest
from crawl import normalize_url, get_h1_from_html, get_first_paragraph_from_html, get_urls_from_html, get_images_from_html, extract_page_data

class TestCrawl(unittest.TestCase):
    def test_normalize_url_https(self):
        input_url = "https://blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)
    
    def test_normalize_url_http(self):
        input_url = "http://blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)
    
    def test_normalize_url_trailing_slash(self):
        input_url = "https://blog.boot.dev/path/"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)
    
    def test_normalize_url_fragment(self):
        input_url = "https://blog.boot.dev/path#section"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)
    
    def test_normalize_url_uppercase(self):
        input_url = "https://BLOG.BOOT.DEV/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)
    
    def test_normalize_url_no_path(self):
        input_url = "https://blog.boot.dev"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev"
        self.assertEqual(actual, expected)
    
    def test_normalize_url_port_http(self):
        input_url = "http://blog.boot.dev:80/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)
    
    def test_normalize_url_port_https(self):
        input_url = "https://blog.boot.dev:443/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)
    
    def test_normalize_url_custom_port(self):
        input_url = "https://blog.boot.dev:8080/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev:8080/path"
        self.assertEqual(actual, expected)
    
    # --- Tests for get_h1_from_html ---
    def test_get_h1_from_html_basic(self):
        input_body = '<html><body><h1>Test Title</h1></body></html>'
        actual = get_h1_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_h1_from_html_no_h1(self):
        input_body = '<html><body><h2>Not an H1</h2></body></html>'
        actual = get_h1_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_h1_from_html_nested(self):
        input_body = '<html><body><div><h1>Nested Title</h1></div></body></html>'
        actual = get_h1_from_html(input_body)
        expected = "Nested Title"
        self.assertEqual(actual, expected)

    def test_get_h1_from_html_with_whitespace(self):
        input_body = '<html><body><h1>  Title with spaces  </h1></body></html>'
        actual = get_h1_from_html(input_body)
        expected = "Title with spaces"
        self.assertEqual(actual, expected)

    # --- Tests for get_first_paragraph_from_html ---
    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = '''<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_no_main(self):
        input_body = '<html><body><p>First paragraph.</p><p>Second.</p></body></html>'
        actual = get_first_paragraph_from_html(input_body)
        expected = "First paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_no_paragraph(self):
        input_body = '<html><body><div>No paragraphs here.</div></body></html>'
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_empty_main(self):
        input_body = '''<html><body>
            <p>Outside paragraph.</p>
            <main></main>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = "Outside paragraph."
        self.assertEqual(actual, expected)
    
    # --- Tests for get_urls_from_html ---
    def test_get_urls_from_html_absolute(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><a href="https://blog.boot.dev"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><a href="/path/to/page">Link</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/path/to/page"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_multiple(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <a href="/page1">First</a>
            <a href="https://external.com">Second</a>
            <a href="/page2">Third</a>
        </body></html>'''
        actual = get_urls_from_html(input_body, input_url)
        expected = [
            "https://blog.boot.dev/page1",
            "https://external.com",
            "https://blog.boot.dev/page2"
        ]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_no_href(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><a>No href attribute</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    # --- Tests for get_images_from_html ---
    def test_get_images_from_html_relative(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="https://cdn.example.com/image.jpg"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://cdn.example.com/image.jpg"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_multiple(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <img src="/img1.png" alt="First">
            <img src="https://external.com/img2.jpg" alt="Second">
            <img src="img3.gif">
        </body></html>'''
        actual = get_images_from_html(input_body, input_url)
        expected = [
            "https://blog.boot.dev/img1.png",
            "https://external.com/img2.jpg",
            "https://blog.boot.dev/img3.gif"
        ]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_no_src(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img alt="No src attribute"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)
    
    def test_extract_page_data_basic(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://blog.boot.dev",
            "h1": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://blog.boot.dev/link1"],
            "image_urls": ["https://blog.boot.dev/image1.jpg"]
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_with_main(self):
        input_url = "https://example.com/page"
        input_body = '''<html><body>
            <h1>Main Title</h1>
            <p>Outside paragraph</p>
            <main>
                <p>Main content paragraph</p>
                <a href="https://external.com">External</a>
                <img src="image.png">
            </main>
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://example.com/page",
            "h1": "Main Title",
            "first_paragraph": "Main content paragraph",
            "outgoing_links": ["https://external.com"],
            "image_urls": ["https://example.com/image.png"]
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_missing_elements(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <div>Just a div, no h1 or paragraphs</div>
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://blog.boot.dev",
            "h1": "",
            "first_paragraph": "",
            "outgoing_links": [],
            "image_urls": []
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_multiple_links_images(self):
        input_url = "https://site.com"
        input_body = '''<html><body>
            <h1>Gallery</h1>
            <p>Check out these links and images.</p>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
            <a href="https://external.com">External</a>
            <img src="/img1.jpg">
            <img src="/img2.png">
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://site.com",
            "h1": "Gallery",
            "first_paragraph": "Check out these links and images.",
            "outgoing_links": [
                "https://site.com/page1",
                "https://site.com/page2",
                "https://external.com"
            ],
            "image_urls": [
                "https://site.com/img1.jpg",
                "https://site.com/img2.png"
            ]
        }
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()

