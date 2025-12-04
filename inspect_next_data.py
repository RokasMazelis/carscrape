import json
from oxylabs_client import OxylabsClient
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)

def inspect_url(url):
    client = OxylabsClient()
    print(f"Fetching {url}...")
    html = client.scrape(url)
    
    if not html:
        print("Failed to fetch.")
        return

    soup = BeautifulSoup(html, 'html.parser')
    script_data = soup.find('script', id='__NEXT_DATA__')
    
    if script_data:
        data = json.loads(script_data.string)
        ad_info = data.get('props', {}).get('pageProps', {}).get('ad', {})
        
        print("--- Ad Info Data ---")
        print(f"Top level phone: {ad_info.get('phone')}")
        if 'contact' in ad_info:
            print(f"Contact phone: {ad_info['contact'].get('phone')}")
        if 'seller' in ad_info:
            print(f"Seller phone: {ad_info['seller'].get('phone')}")
            
        print(f"Full seller object keys: {ad_info.get('seller', {}).keys()}")
    else:
        print("No __NEXT_DATA__ found.")

if __name__ == "__main__":
    # inspect_url("https://www.donedeal.ie/cars-for-sale/opel-corsa-elegnce-1-2-75hp-s-s-4dr/39140601")
    inspect_url("https://www.donedeal.ie/cars-for-sale/opel-mokka-2024-elegance-1-2-100bhp/38614994")
