import csv


def write_csv_report(page_data, filename="report.csv"):
    """
    Write crawl data to a CSV file.
    
    Args:
        page_data: Dictionary of page data keyed by normalized URL
        filename: Output CSV filename (default: report.csv)
    """
    # Filter out failed pages (those with None as value)
    successful_pages = {url: data for url, data in page_data.items() if data is not None}
    
    # Define CSV column headers
    fieldnames = ["page_url", "h1", "first_paragraph", "outgoing_link_urls", "image_urls"]
    
    # Open file for writing
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header row
        writer.writeheader()
        
        # Write each page's data
        for page in successful_pages.values():
            # Join lists with semicolons
            outgoing_links = ";".join(page["outgoing_links"])
            image_urls = ";".join(page["image_urls"])
            
            # Write row
            writer.writerow({
                "page_url": page["url"],
                "h1": page["h1"],
                "first_paragraph": page["first_paragraph"],
                "outgoing_link_urls": outgoing_links,
                "image_urls": image_urls
            })
    
    print(f"\nCSV report written to: {filename}")
    print(f"Total pages exported: {len(successful_pages)}")

