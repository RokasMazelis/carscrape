import json
import time
import logging
import re
import asyncio
from bs4 import BeautifulSoup
from browser_client import BrowserClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

class DoneDealScraper:
    def __init__(self, cookies_path="latest_cookies.json", headless=True):
        self.browser = None
        self.headless = headless
        self.cookies_path = cookies_path
        self.cookies = self._load_cookies(cookies_path)
        self.base_url = "https://www.donedeal.ie"
        self._loop = None

    def _load_cookies(self, path):
        try:
            with open(path, 'r') as f:
                content = f.read().strip()
                if not content:
                    logging.warning(f"{path} is empty. Phone numbers might not be accessible.")
                    return None
                return json.loads(content)
        except FileNotFoundError:
            logging.warning(f"{path} not found. Phone numbers might not be accessible.")
            return None
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in {path}.")
            return None

    async def _ensure_browser(self):
        """Init browser"""
        if self.browser is None:
            self.browser = BrowserClient(headless=self.headless)
            await self.browser._ensure_browser()
    
    async def _close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
    
    def get_ad_id_from_url(self, url):
        # Extract ID from URL
        match = re.search(r'/(\d+)$', url)
        if match:
            return match.group(1)
        match = re.search(r'(\d+)', url.split('/')[-1])
        return match.group(1) if match else None

    def scrape_search_results(self, start_url, max_pages=1, max_ads=None):
        """Sync wrapper"""
        return asyncio.run(self._scrape_search_results_async(start_url, max_pages, max_ads))
    
    async def _scrape_search_results_async(self, start_url, max_pages=1, max_ads=None):
        all_ads = []
        
        try:
            await self._ensure_browser()
            
            # Direct URLs mode
            if isinstance(start_url, list):
                 urls_to_process = start_url[:max_ads] if max_ads else start_url
                 logging.info(f"Processing {len(urls_to_process)} direct URLs...")
                 for i, ad_url in enumerate(urls_to_process):
                     logging.info(f"[{i+1}/{len(urls_to_process)}] Processing: {ad_url}")
                     ad_data = await self._scrape_ad_async(ad_url)
                     if ad_data:
                        all_ads.append(ad_data)
                        self.save_to_csv([ad_data], "donedeal_cars.csv", append=True)
                 return all_ads

            current_url = start_url
            
            for page in range(1, max_pages + 1):
                logging.info(f"Scraping search page {page}: {current_url}")
                html_content = await self.browser.fetch_html(current_url)
                
                if not html_content:
                    logging.error("Failed to retrieve search page content.")
                    break

                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find ad links
                ad_links = []
                
                # Look for card-list
                card_list = soup.find('ul', attrs={"data-testid": "card-list"})
                
                if card_list:
                    logging.info("Found card-list structure.")
                    list_items = card_list.find_all('li', attrs={"data-testid": re.compile(r'listing-card-index-\d+')})
                    
                    for li in list_items:
                        link_tag = li.find('a', href=True)
                        if link_tag:
                            href = link_tag['href']
                            # Filter non-ads
                            if ('/cars-for-sale/' in href or '/ad/' in href or '/view/' in href):
                                full_url = href if href.startswith('http') else self.base_url + href
                                if full_url not in ad_links:
                                    ad_links.append(full_url)
                
                # Fallback: generic parsing
                if not ad_links:
                    logging.info("Fallback: generic parsing")
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if ('/cars/' in href or '/ad/' in href) and re.search(r'\d{7,}', href):
                            full_url = href if href.startswith('http') else self.base_url + href
                            if full_url not in ad_links:
                                ad_links.append(full_url)
                
                logging.info(f"Found {len(ad_links)} ads on page {page}.")
                
                # Apply max ads limit
                if max_ads:
                    remaining = max_ads - len(all_ads)
                    if remaining <= 0:
                        logging.info(f"Reached max_ads limit ({max_ads}). Stopping.")
                        break
                    if len(ad_links) > remaining:
                        logging.info(f"Limiting to {remaining} ads to reach max_ads={max_ads}.")
                        ad_links = ad_links[:remaining]
                else:
                    # Default limit for testing
                    if len(ad_links) > 20:
                        logging.info("Limiting to first 20 ads (default testing limit).")
                        ad_links = ad_links[:20]

                for ad_url in ad_links:
                    ad_data = await self._scrape_ad_async(ad_url)
                    if ad_data:
                        all_ads.append(ad_data)
                        # Save incrementally
                        self.save_to_csv([ad_data], "donedeal_cars.csv", append=True)
                    
                    if max_ads and len(all_ads) >= max_ads:
                        logging.info(f"Reached max_ads limit ({max_ads}). Stopping.")
                        return all_ads
                    
                    # Delay between ads
                    await asyncio.sleep(1) 

                # Next page
                next_button = soup.find('a', attrs={"data-testid": "next-button"}) 
                if not next_button:
                    next_button = soup.find('a', string=re.compile(r'Next', re.I))
                
                if next_button and 'href' in next_button.attrs:
                    next_href = next_button['href']
                    if not next_href.startswith('http'):
                        current_url = self.base_url + next_href
                    else:
                        current_url = next_href
                else:
                    # Manual pagination
                    if "start=" in current_url:
                        try:
                            match = re.search(r'start=(\d+)', current_url)
                            if match:
                                current_start = int(match.group(1))
                                new_start = current_start + 28
                                current_url = re.sub(r'start=\d+', f'start={new_start}', current_url)
                            else:
                                break
                        except:
                            break
                    else:
                        if "?" in current_url:
                            current_url += "&start=28"
                        else:
                            current_url += "?start=28"
                    
                        if not ad_links:
                             logging.info("No ads found on this page and no explicit next button. Stopping.")
                             break
            
            return all_ads
            
        finally:
            await self._close_browser()

    def scrape_ad(self, url):
        """Sync wrapper"""
        return asyncio.run(self._scrape_ad_async(url))
    
    async def _scrape_ad_async(self, url):
        logging.info(f"Scraping ad: {url}")
        
        await self._ensure_browser()
        
        # Fetch HTML and phone in one go
        max_retries = 2
        html_content = None
        phone_number = "Hidden"
        
        for attempt in range(max_retries + 1):
            html_content, phone_number = await self.browser.fetch_html_and_phone(url, reveal_phone=True)
            if html_content:
                break
            logging.warning(f"Attempt {attempt+1} failed to scrape ad {url}. Retrying...")
            await asyncio.sleep(2)
            
        if not html_content:
            logging.error(f"Failed to scrape ad after {max_retries+1} attempts: {url}")
            return None

        soup = BeautifulSoup(html_content, 'html.parser')
        ad_id = self.get_ad_id_from_url(url)
        
        # Title
        title_elem = soup.find('h1')
        title = title_elem.get_text(strip=True) if title_elem else "N/A"
        
        # Price
        price = "N/A"
        price_elem = soup.find(lambda tag: tag.name == "div" and "Price" in tag.get("class", []) and "€" in tag.get_text())
        if not price_elem:
             price_match = soup.find(string=re.compile(r'€[\d,]+'))
             if price_match:
                 price = price_match.strip()
        else:
            price = price_elem.get_text(strip=True)

        # Extract details
        ad_details = {}
        
        list_items = soup.find_all(attrs={"data-testid": "list-item"})
        for item in list_items:
            name_elem = item.find("p", class_=lambda c: c and "ListItemName" in c)
            value_elem = item.find("p", class_=lambda c: c and "ListItemValue" in c)
            
            if name_elem and value_elem:
                key = name_elem.get_text(strip=True)
                val = value_elem.get_text(strip=True)
                ad_details[key] = val

        key_info_items = soup.find_all(class_=lambda c: c and "KeyInfoListItem" in c)
        for item in key_info_items:
            divs = item.find_all("div", recursive=False)
            if len(divs) >= 2:
                key = divs[0].get_text(strip=True)
                val = divs[1].get_text(strip=True)
                ad_details[key] = val

        # Check __NEXT_DATA__ for phone
        phone_from_next = None
        script_data = soup.find('script', id='__NEXT_DATA__')
        if script_data:
             try:
                 data = json.loads(script_data.string)
                 ad_info = data.get('props', {}).get('pageProps', {}).get('ad', {})
                 
                 if 'phone' in ad_info:
                     phone_from_next = ad_info['phone']
                 elif 'contact' in ad_info and 'phone' in ad_info['contact']:
                     phone_from_next = ad_info['contact']['phone']
                 elif 'seller' in ad_info and 'phone' in ad_info['seller']:
                     phone_from_next = ad_info['seller']['phone']
                 
                 if phone_from_next and "Hidden" not in phone_from_next and "***" not in phone_from_next:
                     logging.info(f"Found phone in __NEXT_DATA__: {phone_from_next}")
                 else:
                     phone_from_next = None
             except Exception as e:
                 logging.error(f"Failed to parse __NEXT_DATA__: {e}")

        if phone_from_next:
            phone_number = phone_from_next
            logging.info(f"Using phone from __NEXT_DATA__: {phone_number}")

        result = {
            "id": ad_id,
            "url": url,
            "title": title,
            "price": price,
            "phone": phone_number,
        }
        result.update(ad_details)
        
        return result

    def get_phone_number(self, ad_id, soup=None):
        api_url = f"https://www.donedeal.ie/search/api/v4/view/ad/{ad_id}/contact"
        
        logging.info(f"Fetching phone for ID {ad_id}...")
        
        # Try raw request
        response_content = self.client.scrape(api_url, cookies=self.cookies, render=None)
        
        is_blocked = False
        if response_content and isinstance(response_content, str):
            if "<!DOCTYPE" in response_content or "<html" in response_content:
                is_blocked = True
                logging.warning(f"Phone API blocked. Retrying with render='html'...")

        # Try rendered request
        if is_blocked or not response_content:
             response_content = self.client.scrape(api_url, cookies=self.cookies, render="html")

        # Try POST fallback
        is_failed = False
        if not response_content:
            is_failed = True
        elif isinstance(response_content, str) and ("<!DOCTYPE" in response_content or "<html" in response_content):
            is_failed = True
            
        if is_failed:
            logging.warning(f"GET failed. Retrying with POST to /listing/contact/phone...")
            post_url = "https://www.donedeal.ie/listing/contact/phone"
            post_payload = {"adId": int(ad_id)}
            response_content = self.client.scrape(post_url, method="POST", payload=post_payload, cookies=self.cookies, render=None)

        if response_content:
            try:
                text = response_content
                # Clean HTML wrapper
                if isinstance(text, str):
                    if "<body>" in text:
                        s = BeautifulSoup(text, 'html.parser')
                        pre = s.find('pre')
                        if pre:
                            text = pre.get_text(strip=True)
                        else:
                            text = s.get_text(strip=True)
                
                if isinstance(text, str):
                    text = text.strip()
                    data = json.loads(text)
                else:
                    data = text 
                
                if isinstance(data, dict):
                    return data.get("phoneNumber", "Not Found")
                
            except Exception as e:
                logging.error(f"Failed to parse phone API response: {e}")
                if response_content and isinstance(response_content, str):
                     logging.error(f"Response preview: {response_content[:200]}")
                return "Error"
        return "Failed"


    def save_to_csv(self, ads, filename, append=False):
        import csv
        import os
        if not ads:
            return

        # Standard column order
        standard_fields = [
            "id",
            "url",
            "phone",
            "title",
            "price",
            "year",
            "make",
            "model",
            "mileage",
            "fuel_type",
            "transmission",
            "engine_size",
            "body_type",
            "colour",
            "nct_expiry",
            "county",
            "seller_type",
            "doors",
            "seats",
            "horsepower",
            "engine_description",
            "trim",
        ]
        
        # Field mapping
        field_mapping = {
            "Make": "make",
            "Model": "model",
            "Year": "year",
            "Mileage": "mileage",
            "Fuel Type": "fuel_type",
            "Transmission": "transmission",
            "Engine Size": "engine_size",
            "Body Type": "body_type",
            "Colour": "colour",
            "Doors": "doors",
            "Seats": "seats",
            "NCT Expiry": "nct_expiry",
            "County": "county",
            "Seller Type": "seller_type",
            "Power": "horsepower",
            "Trim Level": "trim",
        }
        
        normalized_ads = []
        for ad in ads:
            normalized = {
                "id": ad.get("id", ""),
                "url": ad.get("url", ""),
                "phone": ad.get("phone", "Hidden"),
                "title": ad.get("title", ""),
                "price": ad.get("price", ""),
            }
            
            for donedeal_key, standard_key in field_mapping.items():
                if donedeal_key in ad:
                    normalized[standard_key] = ad[donedeal_key]
            
            for key, value in ad.items():
                if key not in ["id", "url", "phone", "title", "price"] and key not in field_mapping:
                    clean_key = key.lower().replace(" ", "_").replace("/", "_")
                    normalized[clean_key] = value
            
            normalized_ads.append(normalized)
        
        all_keys = set()
        for ad in normalized_ads:
            all_keys.update(ad.keys())
        
        extra_fields = sorted([k for k in all_keys if k not in standard_fields])
        fieldnames = [f for f in standard_fields if f in all_keys] + extra_fields
        
        file_exists = os.path.exists(filename)
        mode = 'a' if append else 'w'
        write_header = not (append and file_exists)
        
        with open(filename, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            if write_header:
                writer.writeheader()
            for ad in normalized_ads:
                writer.writerow(ad)

if __name__ == "__main__":
    scraper = DoneDealScraper()
