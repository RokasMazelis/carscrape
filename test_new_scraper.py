from scraper import DoneDealScraper
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # Test with a few specific ad URLs first
    test_urls = [
        "https://www.donedeal.ie/cars-for-sale/opel-grandland-gs-line-1-2l-130ps-automatic-from/39669123",
        "https://www.donedeal.ie/cars-for-sale/2022-opel-crossland-1-2-sport/38620768"
    ]
    
    print("Testing Playwright-based scraper with direct URLs...")
    
    scraper = DoneDealScraper(headless=True)
    
    # Test with direct URLs
    ads = scraper.scrape_search_results(test_urls)
    
    print(f"\n✅ Scrape finished. Processed {len(ads)} ads.")
    
    # Summary
    print("\n--- Results Summary ---")
    for ad in ads:
        print(f"ID: {ad.get('id')}")
        print(f"Title: {ad.get('title')}")
        print(f"Price: {ad.get('price')}")
        print(f"Phone: {ad.get('phone')}")
        print(f"Mileage: {ad.get('Mileage', 'N/A')}")
        print("-" * 50)

if __name__ == "__main__":
    main()
