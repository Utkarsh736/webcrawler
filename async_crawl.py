import asyncio
import aiohttp
from urllib.parse import urlparse
from crawl import (
    normalize_url,
    extract_page_data,
    get_urls_from_html,
    is_same_domain
)


class AsyncCrawler:
    def __init__(self, base_url, max_concurrency=5, max_pages=100):
        """
        Initialize the async crawler.
        
        Args:
            base_url: The starting URL to crawl
            max_concurrency: Maximum number of concurrent requests
            max_pages: Maximum number of pages to crawl
        """
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.page_data = {}
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.max_pages = max_pages
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session = None
        self.should_stop = False
        self.all_tasks = set() 

    async def __aenter__(self):
        """Context manager entry - create HTTP session."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close HTTP session."""
        await self.session.close()
    async def add_page_visit(self, normalized_url):
        """
        Thread-safe check if we've visited a page.
        Handles stopping when max_pages is reached.
        
        Args:
            normalized_url: The normalized URL to check
            
        Returns:
            True if first visit, False if already visited or should stop
        """
        async with self.lock:
            # Check if we should stop
            if self.should_stop:
                return False
            
            # Check if already visited
            if normalized_url in self.page_data:
                return False
            
            # Check if we've reached max_pages
            if len(self.page_data) >= self.max_pages:
                self.should_stop = True
                print(f"\nReached maximum number of pages to crawl: {self.max_pages}")
                
                # Cancel all running tasks
                for task in self.all_tasks:
                    task.cancel()
                
                return False
            
            # Mark as visiting (prevent duplicate visits)
            self.page_data[normalized_url] = None
            return True


    
    async def get_html(self, url):
        """
        Fetch HTML from a URL asynchronously.
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string
            
        Raises:
            Exception: If request fails or content is not HTML
        """
        try:
            async with self.session.get(
                url,
                headers={"User-Agent": "BootCrawler/1.0"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                # Check status code
                if response.status >= 400:
                    raise Exception(f"HTTP error: {response.status}")
                
                # Check content type
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type:
                    raise Exception(f"Invalid content type: {content_type}. Expected text/html")
                
                # Return HTML
                return await response.text()
                
        except asyncio.TimeoutError:
            raise Exception("Request timeout")
        except aiohttp.ClientError as e:
            raise Exception(f"Request failed: {e}")
   
    async def crawl_page(self, current_url):
        """
        Recursively crawl a page and its links.

        Args:
            current_url: The URL to crawl
        """
        # Check if should stop
        if self.should_stop:
            return

        # Check same domain
        if not is_same_domain(self.base_url, current_url):
            return

        # Normalize URL
        normalized_url = normalize_url(current_url)

        # Check if first visit
        is_new = await self.add_page_visit(normalized_url)
        if not is_new:
            return

        print(f"Crawling: {current_url}")

        # Limit concurrent requests with semaphore
        async with self.semaphore:
            try:
                # Fetch HTML
                html = await self.get_html(current_url)

                # Extract page data
                data = extract_page_data(html, current_url)

                # Store data (thread-safe)
                async with self.lock:
                    self.page_data[normalized_url] = data

                # Get URLs from page
                urls = get_urls_from_html(html, current_url)

            except Exception as e:
                print(f"Error fetching {current_url}: {e}")
                # Page data already set to None in add_page_visit
                return

        # Create tasks for all URLs (outside semaphore)
        tasks = []
        for url in urls:
            if self.should_stop:
                break

            task = asyncio.create_task(self.crawl_page(url))
            tasks.append(task)

            # Track task in all_tasks
            async with self.lock:
                self.all_tasks.add(task)

        # Wait for all tasks to complete
        if tasks:
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            finally:
                # Remove completed tasks from all_tasks
                async with self.lock:
                    for task in tasks:
                        self.all_tasks.discard(task)
    
    async def crawl(self):
        """
        Start crawling from base_url.
        
        Returns:
            Dictionary of page data keyed by normalized URL
        """
        await self.crawl_page(self.base_url)
        return self.page_data


async def crawl_site_async(base_url, max_concurrency=5, max_pages=100):
    """
    Crawl a website asynchronously.
    
    Args:
        base_url: The starting URL
        max_concurrency: Maximum concurrent requests
        max_pages: Maximum number of pages to crawl
        
    Returns:
        Dictionary of page data
    """
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        page_data = await crawler.crawl()
        return page_data

