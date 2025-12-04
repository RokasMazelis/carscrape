import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import logging

load_dotenv()

async def main():
    logging.basicConfig(level=logging.INFO)
    url = "https://www.donedeal.ie/cars-for-sale/opel-corsa-elegnce-1-2-75hp-s-s-4dr/39140601"
    
    decodo_host = os.getenv("DECODO_PROXY_HOST")
    decodo_port = os.getenv("DECODO_PROXY_PORT")
    decodo_user = os.getenv("DECODO_PROXY_USERNAME")
    decodo_pass = os.getenv("DECODO_PROXY_PASSWORD")
    
    proxy_config = None
    if decodo_host and decodo_user:
        host_clean = decodo_host.replace("http://", "").replace("https://", "")
        proxy_config = {
            "server": f"http://{host_clean}:{decodo_port}",
            "username": f"{decodo_user}-cc-IE", # Force Ireland
            "password": decodo_pass
        }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            proxy=proxy_config,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        logging.info(f"Navigating to {url}")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        
        # Dump initial content to check for loose numbers
        content_before = await page.content()
        with open("debug_before_click.html", "w") as f:
            f.write(content_before)
            
        # Try to click
        try:
            btn = await page.query_selector('button[data-testid="view-phone-number"]')
            if btn:
                logging.info("Found button, clicking...")
                await btn.click()
                await page.wait_for_timeout(3000)
            else:
                logging.warning("Button not found!")
        except Exception as e:
            logging.error(f"Click failed: {e}")
            
        # Dump content after click
        content_after = await page.content()
        with open("debug_after_click.html", "w") as f:
            f.write(content_after)
            
        # Try to find the correct number specifically
        specific_selector = await page.query_selector('a[data-testid="call-phone-number"]')
        if specific_selector:
            href = await specific_selector.get_attribute("href")
            text = await specific_selector.inner_text()
            logging.info(f"Specific Selector Found: href={href}, text={text}")
        else:
            logging.warning("Specific selector 'a[data-testid=\"call-phone-number\"]' NOT found.")
            
        # Check what the loose regex finds
        import re
        phones_link = re.findall(r'href="tel:([^"]+)"', content_after)
        phones_text = re.findall(r'08\d\s?\d{7}', content_after)
        logging.info(f"Regex Link matches: {phones_link}")
        logging.info(f"Regex Text matches: {phones_text}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
