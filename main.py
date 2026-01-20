import sys
import asyncio
from async_crawl import crawl_site_async


async def main():
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: uv run main.py URL [max_concurrency] [max_pages]")
        print("Example: uv run main.py https://example.com 5 100")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    # Get optional concurrency and max_pages arguments
    max_concurrency = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    
    print(f"starting crawl of: {base_url}")
    print(f"max_concurrency: {max_concurrency}")
    print(f"max_pages: {max_pages}")
    print()
    
    # Crawl the site asynchronously
    try:
        page_data = await crawl_site_async(base_url, max_concurrency, max_pages)
        
        # Filter successful pages
        successful_pages = {url: data for url, data in page_data.items() if data is not None}
        failed_pages = {url: data for url, data in page_data.items() if data is None}
        
        # Print summary
        print(f"\n=== Crawl Complete ===")
        print(f"Total pages found: {len(page_data)}")
        print(f"Successful: {len(successful_pages)}")
        print(f"Failed: {len(failed_pages)}")
        
        if failed_pages:
            print(f"\nFailed URLs:")
            for url in failed_pages.keys():
                print(f"  - {url}")
        
        print(f"\nSuccessful Page Details:")
        for data in successful_pages.values():
            print(f"\n{data['url']}")
            print(f"  H1: {data['h1']}")
            print(f"  First paragraph: {data['first_paragraph'][:50]}..." if data['first_paragraph'] else "  First paragraph: (none)")
            print(f"  Outgoing links: {len(data['outgoing_links'])}")
            print(f"  Images: {len(data['image_urls'])}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

