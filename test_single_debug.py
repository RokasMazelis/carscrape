import logging
from phone_revealer import PhoneRevealer

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    revealer = PhoneRevealer(headless=True)
    url = "https://www.donedeal.ie/cars-for-sale/2020-bmw-730d-m-sport/40434017"
    print(f"Testing {url}")
    print(revealer.get_number(url))
