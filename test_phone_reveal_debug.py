from scraper import DoneDealScraper
import logging

# Configure logging with DEBUG level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # Test with just ONE ad to see phone reveal in action
    test_urls = [
        "https://www.donedeal.ie/cars-for-sale/2020-bmw-730d-m-sport/40434017"
    ]
    
    print("Testing phone reveal with visible browser...")
    print("You should see the browser window open and click the phone button\n")
    
    # Set headless=False to see the browser
    scraper = DoneDealScraper(headless=False)
    
    ads = scraper.scrape_search_results(test_urls)
    
    print(f"\n✅ Scrape finished.")
    
    # Summary
    print("\n--- Results ---")
    for ad in ads:
        print(f"ID: {ad.get('id')}")
        print(f"Title: {ad.get('title')}")
        print(f"Price: {ad.get('price')}")
        print(f"Phone: {ad.get('phone')}")  # Should show actual number or "Hidden"
        print("-" * 50)

if __name__ == "__main__":
    main()
