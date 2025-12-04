import os
import requests
import logging
import cloudscraper
from dotenv import load_dotenv
import base64

# Reload env vars
load_dotenv(override=True)

class SmartProxyClient:
    def __init__(self):
        self.host = os.getenv("DECODO_PROXY_HOST")
        self.port = os.getenv("DECODO_PROXY_PORT")
        self.username = os.getenv("DECODO_PROXY_USERNAME")
        self.password = os.getenv("DECODO_PROXY_PASSWORD")
        
        if not self.host or not self.username:
            raise ValueError("DECODO_PROXY_HOST and DECODO_PROXY_USERNAME must be set in .env")

        # Strip whitespace
        self.username = self.username.strip() if self.username else ""
        self.password = self.password.strip() if self.password else ""
        self.host = self.host.strip() if self.host else ""
        self.port = self.port.strip() if self.port else ""
        
        self.proxies = {
            "http": f"http://{self.username}:{self.password}@{self.host}:{self.port}",
            "https": f"http://{self.username}:{self.password}@{self.host}:{self.port}",
        }
        
        # Setup CloudScraper
        self.scraper_session = cloudscraper.create_scraper(
            browser={
                'custom': 'ScraperBot/1.0',
            }
        )
        # Chrome headers
        self.scraper_session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.donedeal.ie/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        })

    def scrape(self, url, method="GET", cookies=None, payload=None, render=None):
        """Scrape via SmartProxy"""
        logging.info(f"Scraping {url} via SmartProxy (CloudScraper)...")
        
        # Convert cookies
        cookie_dict = cookies
        if isinstance(cookies, list):
            try:
                cookie_dict = {c['name']: c['value'] for c in cookies}
            except (TypeError, KeyError):
                logging.warning("Failed to convert cookies list to dict, passing raw.")
                pass

        try:
            
            if method == "POST":
                response = self.scraper_session.post(
                    url,
                    proxies=self.proxies,
                    cookies=cookie_dict,
                    json=payload,
                    timeout=60
                )
            else:
                response = self.scraper_session.get(
                    url,
                    proxies=self.proxies,
                    cookies=cookie_dict,
                    timeout=60
                )
            
            response.raise_for_status()
            return response.text
                
        except Exception as e:
            logging.error(f"SmartProxy request failed: {e}")
            return None
