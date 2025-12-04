from scraper import DoneDealScraper
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # Test with private seller search (with mileage filter)
    search_url = "https://www.donedeal.ie/dealer/sd-autos"
    
    print("=" * 70)
    print(f"Testing search: Private sellers with mileage > 1000")
    print("=" * 70)
    print(f"URL: {search_url}")
    print("\nThis will:")
    print("  1. Scrape the first page of search results")
    print("  2. Extract details for each ad (LIMITED TO 4 ADS)")
    print("  3. Reveal phone numbers (browser visible)")
    print("  4. Save to donedeal_cars.csv\n")
    print("Note: Limited to 4 ads for quick testing. Set headless=True to hide browser.\n")
    
    scraper = DoneDealScraper(headless=False)  # Changed to False so you can watch
    
    # Scrape first page only (max_pages=1)
    # Note: This saves to donedeal_cars.csv (now with proper structure)
    ads = scraper.scrape_search_results(search_url, max_pages=1, max_ads=4)
    
    print(f"\n✅ Scrape finished. Found {len(ads)} ads.")
    
    # Count successful phone reveals
    phones_found = sum(1 for ad in ads if ad.get('phone') not in ['Hidden', 'Error', None])
    print(f"📞 Phone numbers revealed: {phones_found}/{len(ads)}")
    
    # Summary
    print("\n--- Results Summary ---")
    for i, ad in enumerate(ads, 1):
        phone_status = "✓" if ad.get('phone') not in ['Hidden', 'Error', None] else "✗"
        print(f"\n[{i}] {phone_status} ID: {ad.get('id')}")
        print(f"    Title: {ad.get('title')}")
        print(f"    Price: {ad.get('price')}")
        print(f"    Phone: {ad.get('phone')}")
        print(f"    Make/Model: {ad.get('Make', 'N/A')} {ad.get('Model', 'N/A')}")
        print(f"    Year: {ad.get('Year', 'N/A')}")
        print(f"    Mileage: {ad.get('Mileage', 'N/A')}")
    
    print(f"\n📊 Total ads scraped: {len(ads)}")
    print(f"📁 Results saved to: donedeal_cars.csv (with structured headers)")
    print(f"\n💡 CSV columns: id, url, phone, title, price, year, make, model, mileage, fuel_type, etc.")

if __name__ == "__main__":
    main()
