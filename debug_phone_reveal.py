
whefrom phone_revealer import PhoneRevealer
import logging
import os

# Configure logging to show debug info
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # A URL that matches the HAR file context
    url = "https://www.donedeal.ie/cars-for-sale/181-audi-a5-2-0-tdi-only-11250/41038709?campaign=3"
    print(f"Starting DEBUG Phone Reveal for: {url}")
    
    # HEADLESS=True is safer for avoiding detection with proper headers
    revealer = PhoneRevealer(cookies_path="cookies_fresh.json", headless=True) 
    
    try:
        number = revealer.get_number(url)
        print(f"✅ Result: {number}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
