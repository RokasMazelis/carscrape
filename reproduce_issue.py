from phone_revealer import PhoneRevealer
import logging

logging.basicConfig(level=logging.INFO)

def test_url(url):
    print(f"Testing URL: {url}")
    revealer = PhoneRevealer(headless=True)
    number = revealer.get_number(url)
    print(f"Extracted Number: {number}")

if __name__ == "__main__":
    # URL from CSV line 2 (User's example)
    # CSV: 39140601 ... 840658940
    # Expected: 00353578638125
    test_url("https://www.donedeal.ie/cars-for-sale/opel-corsa-elegnce-1-2-75hp-s-s-4dr/39140601")
    
    # URL from CSV line 1
    # CSV: 38614994 ... 831552126
    test_url("https://www.donedeal.ie/cars-for-sale/opel-mokka-2024-elegance-1-2-100bhp/38614994")
