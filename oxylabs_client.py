import os
import requests
import json
import logging
from dotenv import load_dotenv

load_dotenv()

class OxylabsClient:
    def __init__(self):
        self.username = os.getenv("OXYLABS_API_USERNAME")
        self.password = os.getenv("OXYLABS_API_PASSWORD")
        self.geo_location = os.getenv("OXYLABS_COUNTRY", "Ireland")
        self.api_url = "https://realtime.oxylabs.io/v1/queries"
        
        if not self.username or not self.password:
            raise ValueError("OXYLABS_API_USERNAME and OXYLABS_API_PASSWORD must be set in .env")

    def scrape(self, url, method="GET", cookies=None, payload=None, render="html"):
        """Scrape via Oxylabs API"""
        headers = {
            "Content-Type": "application/json",
        }
        
        # Build job payload
        job_payload = {
            "source": "universal",
            "url": url,
            "geo_location": self.geo_location,
        }
        
        if render:
            job_payload["render"] = render
            
        # POST support
        if method == "POST" and payload:
            job_payload["http_method"] = "post"
            job_payload["body"] = json.dumps(payload)

        # Setup headers
        custom_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        if cookies:
            # Format cookies
            if isinstance(cookies, list):
                cookie_parts = []
                for c in cookies:
                    cookie_parts.append(f"{c['name']}={c['value']}")
                    
                    # Inject XSRF token
                    if c['name'] == 'XSRF-TOKEN' or c['name'] == 'X-XSRF-TOKEN':
                        custom_headers['X-XSRF-TOKEN'] = c['value']
                        custom_headers['X-CSRF-TOKEN'] = c['value']
                
                cookie_str = "; ".join(cookie_parts)
            elif isinstance(cookies, dict):
                 cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            else:
                cookie_str = str(cookies)
            
            custom_headers["Cookie"] = cookie_str

        job_payload["headers"] = custom_headers
        
        if "api/v" in url:
             job_payload["source"] = "universal"
             job_payload["render"] = None
             
        
        logging.info(f"Scraping {url} via Oxylabs...")
        
        try:
            response = requests.post(
                self.api_url,
                auth=(self.username, self.password),
                json=job_payload,
                timeout=180
            )
            response.raise_for_status()
            data = response.json()
            
            if "results" in data and len(data["results"]) > 0:
                return data["results"][0]["content"]
            else:
                logging.error(f"No content returned from Oxylabs: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Oxylabs request failed: {e}")
            if hasattr(e, 'response') and e.response:
                 logging.error(f"Response: {e.response.text}")
            return None
