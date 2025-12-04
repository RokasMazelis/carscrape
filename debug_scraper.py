from scraper import DoneDealScraper
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    url = "https://www.donedeal.ie/cars/Opel?mileage_from=1000&fuelType=Petrol"
    print(f"Starting DEBUG scraper for: {url}")
    
    scraper = DoneDealScraper()
    
    # 1. Fetch content manually using the client
    print("Fetching page via Oxylabs...")
    content = scraper.client.scrape(url, cookies=scraper.cookies)
    
    if content:
        filename = "debug_search_results.html"
        print(f"✅ Content fetched ({len(content)} chars). Saving to {filename}...")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
            
        # 2. Analyze content briefly
        if "Opel" in content:
            print("✅ Found 'Opel' in content.")
        else:
            print("⚠️ 'Opel' NOT found in content. Possible captcha or block.")
            
        if "card-list" in content or "CardList" in content:
            print("✅ Found 'card-list' related class.")
        else:
            print("⚠️ 'card-list' NOT found.")
            
        if "__NEXT_DATA__" in content:
             print("✅ Found '__NEXT_DATA__'.")
        else:
             print("⚠️ '__NEXT_DATA__' NOT found.")
             
        if "challenge-form" in content or "Cloudflare" in content:
            print("⚠️ Detected potential Cloudflare challenge.")
            
    else:
        print("❌ Failed to fetch content.")

if __name__ == "__main__":
    main()
