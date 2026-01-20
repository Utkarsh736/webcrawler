# Async Web Crawler

A high-performance, concurrent web crawler built in Python that recursively crawls websites and exports structured data to CSV reports.

## Features

- **Async/Concurrent Crawling**: Uses `asyncio` and `aiohttp` for fast, non-blocking HTTP requests
- **Configurable Limits**: Control max concurrent requests and total pages to crawl
- **Smart URL Handling**: Normalizes URLs to avoid duplicate crawls
- **Same-Domain Filtering**: Stays within the target website domain
- **HTML Parsing**: Extracts h1 tags, paragraphs, links, and images using BeautifulSoup
- **CSV Export**: Generates structured reports for easy analysis
- **Graceful Stopping**: Cancels in-flight tasks when limits are reached
- **Error Handling**: Handles timeouts, non-HTML content, and network failures

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

## Getting Started

### Cloning the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/Utkarsh736/webcrawler.git
cd webcrawler
```

### Installation

If using `uv` (recommended):

```bash
uv sync
```

If using pip:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Crawl a website with default settings (5 concurrent requests, 100 max pages):

```bash
uv run main.py https://example.com
```

### Advanced Usage

Specify custom concurrency and page limits:

```bash
uv run main.py URL [max_concurrency] [max_pages]
```

**Examples:**

```bash
# Crawl with 10 concurrent requests, max 50 pages
uv run main.py https://wagslane.dev 10 50

# Conservative crawl: 2 concurrent requests, max 20 pages
uv run main.py https://example.com 2 20

# Aggressive crawl: 15 concurrent requests, max 200 pages
uv run main.py https://example.com 15 200
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `URL` | Starting URL to crawl (required) | - |
| `max_concurrency` | Maximum concurrent HTTP requests | 5 |
| `max_pages` | Maximum number of pages to crawl | 100 |

## Output

The crawler generates a `report.csv` file with the following columns:

- **page_url**: The URL of the crawled page
- **h1**: The main heading (h1 tag) content
- **first_paragraph**: Text from the first paragraph (prioritizes `<main>` tag)
- **outgoing_link_urls**: All links found on the page (semicolon-separated)
- **image_urls**: All image URLs found on the page (semicolon-separated)

### Example Output

```csv
page_url,h1,first_paragraph,outgoing_link_urls,image_urls
https://example.com,Welcome,This is the homepage,...,https://example.com/logo.png
```

## Project Structure

```
webcrawler/
├── main.py              # Entry point and CLI handling
├── async_crawl.py       # AsyncCrawler class with concurrent crawling logic
├── crawl.py             # URL normalization and HTML parsing utilities
├── csv_report.py        # CSV report generation
├── test_crawl.py        # Unit tests for core functions
├── pyproject.toml       # Project dependencies and configuration
└── README.md            # This file
```

## How It Works

1. **URL Normalization**: Converts URLs to a standard format (removes protocols, trailing slashes, default ports)
2. **Concurrent Fetching**: Uses asyncio semaphore to limit simultaneous requests
3. **HTML Parsing**: Extracts structured data using BeautifulSoup4
4. **Link Discovery**: Finds all `<a>` and `<img>` tags, converts relative URLs to absolute
5. **Recursive Crawling**: Follows discovered links within the same domain
6. **Duplicate Prevention**: Tracks visited URLs with thread-safe async locks
7. **CSV Export**: Writes results to a structured CSV file

## Testing

Run the unit tests:

```bash
uv run -m unittest
```

Tests cover:
- URL normalization (protocols, trailing slashes, ports, case sensitivity)
- HTML parsing (h1, paragraphs, links, images)
- Edge cases (missing elements, nested tags, whitespace)

## Best Practices

- **Start Small**: Test with low `max_pages` (e.g., 10) before crawling large sites
- **Respect Servers**: Don't set `max_concurrency` too high (5-10 is reasonable)
- **Monitor Progress**: Watch console output to ensure crawler isn't stuck
- **Use Ctrl+C**: Kill the crawler if it's misbehaving

## Limitations

- Only crawls HTML pages (skips PDFs, images, RSS feeds, etc.)
- Stays within the starting domain (no external site crawling)
- No JavaScript rendering (only static HTML)
- No robots.txt compliance (add manually if needed)

## Dependencies

- `aiohttp`: Async HTTP client
- `beautifulsoup4`: HTML parsing
- `requests`: Synchronous HTTP (used in tests)

## Future Enhancements

- [ ] Respect robots.txt
- [ ] Add rate limiting with delays between requests
- [ ] Support for JavaScript-rendered pages (Playwright/Selenium)
- [ ] Export to JSON/SQLite
- [ ] Depth-limited crawling
- [ ] Retry failed requests with exponential backoff

## License

This project is open source and available under the MIT License.

## Author

[Utkarsh736](https://github.com/Utkarsh736)
