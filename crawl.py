import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def normalize_url(url):
    # Parse the URL into components
    parsed = urlparse(url)
    
    # Extract components
    netloc = parsed.netloc.lower()  # Domain (case-insensitive)
    path = parsed.path  # Path
    
    # Remove default ports
    if ':80' in netloc and parsed.scheme == 'http':
        netloc = netloc.replace(':80', '')
    if ':443' in netloc and parsed.scheme == 'https':
        netloc = netloc.replace(':443', '')
    
    # Remove trailing slash from path
    if path.endswith('/'):
        path = path.rstrip('/')
    
    # Build normalized URL (no scheme, no fragment)
    if path:
        normalized = f"{netloc}{path}"
    else:
        normalized = netloc
    
    return normalized

def get_h1_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    h1_tag = soup.find('h1')

    if h1_tag is None:
        return ""

    return h1_tag.get_text(strip=True)

def get_first_paragraph_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try to find <main> tag first
    main_tag = soup.find('main')
    
    # If <main> exists, search for <p> within it
    if main_tag:
        p_tag = main_tag.find('p')
        if p_tag:
            return p_tag.get_text(strip=True)
    
    # Fallback: search entire document for first <p>
    p_tag = soup.find('p')
    
    if p_tag is None:
        return ""
    
    return p_tag.get_text(strip=True)

def get_urls_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    urls = []
    
    # Find all anchor tags
    anchor_tags = soup.find_all('a')
    
    for tag in anchor_tags:
        # Safely get href attribute
        href = tag.get('href')
        
        # Skip if no href attribute
        if href is None:
            continue
        
        # Convert to absolute URL
        absolute_url = urljoin(base_url, href)
        urls.append(absolute_url)
    
    return urls

def get_images_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    image_urls = []
    
    # Find all img tags
    img_tags = soup.find_all('img')
    
    for tag in img_tags:
        # Safely get src attribute
        src = tag.get('src')
        
        # Skip if no src attribute
        if src is None:
            continue
        
        # Convert to absolute URL
        absolute_url = urljoin(base_url, src)
        image_urls.append(absolute_url)
    
    return image_urls

def extract_page_data(html, page_url):
    """
    Extract all relevant data from an HTML page.

    Returns a dictionary with:
    - url: the page URL
    - h1: the h1 text (or empty string)
    - first_paragraph: first paragraph text (or empty string)
    - outgoing_links: list of absolute URLs from anchor tags
    - image_urls: list of absolute image URLs
    """
    return {
        "url": page_url,
        "h1": get_h1_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url)
    }

def get_html(url):
    """
    Fetch HTML content from a URL.
    
    Args:
        url: The URL to fetch
        
    Returns:
        The HTML content as a string
        
    Raises:
        Exception: If the request fails, status code is 400+, 
                   or content-type is not text/html
    """
    try:
        # Make request with custom User-Agent and TIMEOUT
        response = requests.get(
            url, 
            headers={"User-Agent": "BootCrawler/1.0"},
            timeout=10  # 10 seconds timeout
        )
        
        # Check for HTTP error status codes (400+)
        if response.status_code >= 400:
            raise Exception(f"HTTP error: {response.status_code}")
        
        # Get content-type header
        content_type = response.headers.get('Content-Type', '')
        
        # Check if content-type is text/html
        if 'text/html' not in content_type:
            raise Exception(f"Invalid content type: {content_type}. Expected text/html")
        
        # Return the HTML content
        return response.text
        
    except requests.exceptions.RequestException as e:
        # Catch all requests-related errors (network, timeout, etc.)
        raise Exception(f"Request failed: {e}")

def is_same_domain(base_url, current_url):
    """
    Check if current_url is on the same domain as base_url.
    """
    base_domain = urlparse(base_url).netloc
    current_domain = urlparse(current_url).netloc
    return base_domain == current_domain

def crawl_page(base_url, current_url=None, page_data=None):
    """
    Recursively crawl pages starting from base_url.
    """
    # Initialize on first call
    if current_url is None:
        current_url = base_url
    
    if page_data is None:
        page_data = {}
    
    # Check if current_url is on the same domain
    if not is_same_domain(base_url, current_url):
        return page_data
    
    # Normalize the URL
    normalized_url = normalize_url(current_url)
    
    # Check if we've already crawled this page
    if normalized_url in page_data:
        return page_data
    
    # Print progress
    print(f"Crawling: {current_url}")
    
    # Fetch the HTML
    try:
        html = get_html(current_url)
    except Exception as e:
        print(f"Error fetching {current_url}: {e}")
        # CRITICAL FIX: Mark as visited even if it failed
        page_data[normalized_url] = None
        return page_data
    
    # Extract page data
    data = extract_page_data(html, current_url)
    page_data[normalized_url] = data
    
    # Get all URLs from the page
    urls = get_urls_from_html(html, current_url)
    
    # Recursively crawl each URL
    for url in urls:
        page_data = crawl_page(base_url, url, page_data)
    
    return page_data

