from scraper import DoneDealScraper
import logging

# Configure logging to see output in console
logging.basicConfig(level=logging.INFO)

def main():
    # URL to scrape (Dealer page)
    start_url = "https://www.donedeal.ie/dealer/sd-autos"
    
    print(f"Starting scraper for: {start_url}")
    
    scraper = DoneDealScraper()
    
    # Pass the single URL as a string to trigger search/list mode
    ads = scraper.scrape_search_results(start_url, max_pages=1)
    
    print(f"\n✅ Scrape finished. Found {len(ads)} ads.")
    
    # Summary of results
    print("\n--- Results Summary ---")
    for ad in ads:
        print(f"ID: {ad.get('id')} | Phone: {ad.get('phone')} | Title: {ad.get('title')}")

if __name__ == "__main__":
    main()
