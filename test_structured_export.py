from scraper import DoneDealScraper
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # Test with a couple of ads to show the new structure
    test_urls = [
        "https://www.donedeal.ie/cars-for-sale/2020-bmw-730d-m-sport/40434017"
    ]
    
    print("=" * 70)
    print("Testing STRUCTURED CSV Export")
    print("=" * 70)
    print("\nThis will create a clean CSV with:")
    print("  ✓ Proper header row")
    print("  ✓ Consistent column names (id, url, phone, title, price, etc.)")
    print("  ✓ Normalized field names (make, model, year, mileage, etc.)")
    print("  ✓ Important fields first for easy use with your next agent\n")
    
    # Remove old CSV to start fresh
    csv_file = "donedeal_cars_structured.csv"
    if os.path.exists(csv_file):
        os.remove(csv_file)
        print(f"✓ Removed old {csv_file}\n")
    
    scraper = DoneDealScraper(headless=True)
    
    # Scrape
    ads = scraper.scrape_search_results(test_urls)
    
    if ads:
        # Save with new structure
        scraper.save_to_csv(ads, csv_file, append=False)
        
        print(f"\n✅ Structured CSV created: {csv_file}")
        print("\n--- CSV Column Order ---")
        
        # Show the column structure
        import csv
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            print(f"Total columns: {len(headers)}\n")
            
            print("Core columns:")
            for i, header in enumerate(headers[:10], 1):
                print(f"  {i}. {header}")
            
            if len(headers) > 10:
                print(f"\n  ... and {len(headers) - 10} more columns")
        
        print("\n--- Sample Data ---")
        for ad in ads:
            print(f"ID: {ad.get('id')}")
            print(f"Phone: {ad.get('phone')}")
            print(f"Make: {ad.get('Make', 'N/A')}")
            print(f"Model: {ad.get('Model', 'N/A')}")
            print(f"Year: {ad.get('Year', 'N/A')}")
            print(f"Price: {ad.get('price')}")
    else:
        print("❌ No ads scraped")

if __name__ == "__main__":
    main()
