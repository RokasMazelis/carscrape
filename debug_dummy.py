import asyncio
import logging
from phone_revealer import PhoneRevealer

logging.basicConfig(level=logging.INFO)

async def test_single():
    revealer = PhoneRevealer(headless=True)
    url = "https://www.donedeal.ie/cars-for-sale/2020-bmw-730d-m-sport/40434017"
    print(f"Testing {url}")
    
    # We need to access the page object to dump HTML, but get_number encapsulates it.
    # So we'll just rely on get_number's return.
    # Wait, I modified PhoneRevealer to save screenshot. I should modify it to save HTML too?
    # Or just trust my previous analysis that said "NO_BUTTON" in debug logs.
    
    # If I modify PhoneRevealer to save HTML on hidden, that's best.
    pass

if __name__ == "__main__":
    # I will just run the existing test_links.py but limits it? 
    # No, I'll modify PhoneRevealer first.
    pass
