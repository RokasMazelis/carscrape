import json
import sys

def extract_har_info(har_path):
    try:
        with open(har_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entries = data['log']['entries']
        print(f"Total entries: {len(entries)}")
        
        reveal_entry = None
        for entry in entries:
            url = entry['request']['url']
            method = entry['request']['method']
            if "phonereveal" in url:
                print(f"Potential match: {method} {url}")
                if method == "GET":
                    reveal_entry = entry
                    break
        
        if reveal_entry:
            print(f"Found phonereveal request: {reveal_entry['request']['url']}")
            
            # Extract Cookies
            cookies_list = reveal_entry['request'].get('cookies', [])
            playwright_cookies = []
            
            if cookies_list:
                print(f"Found {len(cookies_list)} cookies in 'cookies' list.")
                for c in cookies_list:
                    cookie = {
                        "name": c['name'],
                        "value": c['value'],
                        "domain": ".donedeal.ie",
                        "path": "/"
                    }
                    playwright_cookies.append(cookie)
            else:
                print("No 'cookies' list found, trying headers...")
                # Try parsing Cookie header
                headers = {h['name'].lower(): h['value'] for h in reveal_entry['request']['headers']}
                print(f"Available headers: {list(headers.keys())}")
                if 'cookie' in headers:
                    print("Found 'cookie' header. Parsing...")
                    cookie_str = headers['cookie']
                    for item in cookie_str.split(';'):
                        if '=' in item:
                            name, value = item.strip().split('=', 1)
                            playwright_cookies.append({
                                "name": name,
                                "value": value,
                                "domain": ".donedeal.ie",
                                "path": "/"
                            })
                else:
                     print("No 'cookie' header found.")
            
            if playwright_cookies:
                with open('cookies_fresh.json', 'w') as f:
                    json.dump(playwright_cookies, f, indent=2)
                print(f"Saved {len(playwright_cookies)} cookies to cookies_fresh.json")
            else:
                print("No cookies extracted at all.")
            
            # Extract Headers
            headers = {h['name']: h['value'] for h in reveal_entry['request']['headers']}
            print("\nHeaders:")
            for k, v in headers.items():
                print(f"{k}: {v}")
                
            # Check specifically for Recaptcha
            if 'recaptcha-token' in headers:
                print(f"\nRecaptcha Token found: {headers['recaptcha-token'][:50]}...")
            else:
                print("\nWARNING: No recaptcha-token header found in HAR entry.")
                
        else:
            print("No phonereveal request found in HAR.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_har_info("www.donedeal.ie.har")
