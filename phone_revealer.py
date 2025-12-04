import logging
import os
import time
import json
import re
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

class PhoneRevealer:
    def __init__(self, cookies_path="latest_cookies.json", headless=True, user_data_dir="browser_data"):
        self.cookies_path = cookies_path
        self.headless = headless
        self.user_data_dir = user_data_dir
        
        # Proxy config
        self.decodo_host = os.getenv("DECODO_PROXY_HOST")
        self.decodo_port = os.getenv("DECODO_PROXY_PORT")
        self.decodo_user = os.getenv("DECODO_PROXY_USERNAME")
        self.decodo_pass = os.getenv("DECODO_PROXY_PASSWORD")
        
        if not self.decodo_host:
            logging.warning("DECODO_PROXY_HOST not set in .env. SmartProxy might fail.")

    def get_number(self, url):
        return asyncio.run(self._get_number_async(url))

    async def _get_number_async(self, url):
        logging.info(f"Revealing phone for: {url}")
        
        proxy_config = None
        if self.decodo_host and self.decodo_user:
            host_clean = self.decodo_host.replace("http://", "").replace("https://", "")
            proxy_config = {
                "server": f"http://{host_clean}:{self.decodo_port}",
                "username": self.decodo_user,
                "password": self.decodo_pass
            }
            logging.info(f"Using Decodo/SmartProxy (User: {self.decodo_user})")
        else:
             logging.error("SmartProxy credentials not found! Cannot reveal phone number.")
             return "Failed"

        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=self.headless,
                proxy=proxy_config,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars",
                    "--use-mock-keychain", 
                    "--password-store=basic"
                ]
            )
            
            # Stealth context
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                locale="en-IE",
                timezone_id="Europe/Dublin",
                permissions=["geolocation"],
                geolocation={"latitude": 53.3498, "longitude": -6.2603}
            )
            
            # Hide webdriver
            await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            page = await context.new_page()
            
            try:
                await page.goto(url, timeout=90000, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                
                # Handle cookies
                try:
                    cookie_btn = page.locator("#didomi-notice-agree-button")
                    if await cookie_btn.is_visible():
                        await cookie_btn.click()
                        await page.wait_for_timeout(1500)
                except Exception:
                    pass

                # Click phone button
                buttons = page.locator('button[data-testid="view-phone-number"]')
                count = await buttons.count()
                clicked = False
                
                for i in range(count):
                    btn = buttons.nth(i)
                    if await btn.is_visible():
                        try:
                            await btn.scroll_into_view_if_needed()
                            await btn.click(timeout=5000)
                            clicked = True
                            await page.wait_for_timeout(2000)
                            break
                        except Exception as e:
                            logging.warning(f"Failed to click button {i}: {e}")
                
                if not clicked:
                     logging.warning("No visible phone button found or clickable.")

                # Extract phone
                content = await page.content()
                phones_link = re.findall(r'href="tel:([^"]+)"', content)
                
                if phones_link:
                    logging.info(f"Phone found via HTML tel link: {phones_link[0]}")
                    return phones_link[0].replace("tel:", "")
                
                for i in range(count):
                    btn = buttons.nth(i)
                    if await btn.is_visible():
                        text = await btn.inner_text()
                        match = re.search(r'(08[35679]\s?\d{7})|(\+?353\s?8[35679]\s?\d{7})', text)
                        if match:
                            logging.info(f"Phone found in button text: {match.group(0)}")
                            return match.group(0)

                logging.warning("Reveal failed. Returning Hidden.")
                
                # Debug screenshot
                try:
                    timestamp = int(time.time())
                    screenshot_path = f"debug_fail_{timestamp}.png"
                    await page.screenshot(path=screenshot_path)
                    logging.info(f"Saved screenshot to {screenshot_path}")
                except Exception:
                    pass

                return "Hidden"

            except Exception as e:
                logging.error(f"Playwright error: {e}")
                return "Error"
            finally:
                await browser.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    revealer = PhoneRevealer(headless=True) 
    test_url = "https://www.donedeal.ie/cars-for-sale/opel-grandland-gs-line-1-2l-130ps-automatic-from/39669123?campaign=3"
    print(revealer.get_number(test_url))


