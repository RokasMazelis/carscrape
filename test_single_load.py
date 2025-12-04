from scraper import DoneDealScraper
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # Test with a valid car ad
    test_urls = [
        "https://www.donedeal.ie/cars-for-sale/2020-bmw-730d-m-sport/40434017"
    ]
    
    print("=" * 60)
    print("Testing SINGLE-LOAD phone reveal (browser opens only once)")
    print("=" * 60)
    print("\nYou should see:")
    print("  1. Browser opens once")
    print("  2. Loads the ad page")
    print("  3. Clicks phone button (on same page)")
    print("  4. Extracts phone number")
    print("  5. Browser closes")
    print("\nNo ERR_TUNNEL_CONNECTION_FAILED errors!\n")
    
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
        print(f"Phone: {ad.get('phone')}")  # Should show actual number
        print(f"Year: {ad.get('Year', 'N/A')}")
        print("-" * 50)

if __name__ == "__main__":
    main()
