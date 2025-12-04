import logging
import os
import time
import re
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

load_dotenv()

class BrowserClient:
    """Playwright browser client"""
    
    def __init__(self, headless=True, user_data_dir="browser_data"):
        self.headless = headless
        self.user_data_dir = user_data_dir
        
        # Proxy config
        self.decodo_host = os.getenv("DECODO_PROXY_HOST")
        self.decodo_port = os.getenv("DECODO_PROXY_PORT")
        self.decodo_user = os.getenv("DECODO_PROXY_USERNAME")
        self.decodo_pass = os.getenv("DECODO_PROXY_PASSWORD")
        
        if not self.decodo_host or not self.decodo_user:
            raise ValueError("DECODO_PROXY_HOST and DECODO_PROXY_USERNAME must be set in .env")
        
        # Browser state
        self._playwright = None
        self._browser: Browser = None
        self._context: BrowserContext = None
        self._session_start_time = None
        
    async def _ensure_browser(self):
        """Init browser if needed"""
        if self._browser and self._context:
            return
            
        host_clean = self.decodo_host.replace("http://", "").replace("https://", "")
        proxy_config = {
            "server": f"http://{host_clean}:{self.decodo_port}",
            "username": self.decodo_user,
            "password": self.decodo_pass
        }
        
        logging.info(f"Launching browser with Decodo proxy (User: {self.decodo_user})")
        
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
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
        self._context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="en-IE",
            timezone_id="Europe/Dublin",
            permissions=["geolocation"],
            geolocation={"latitude": 53.3498, "longitude": -6.2603}
        )
        
        # Hide webdriver
        await self._context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self._session_start_time = time.time()
        logging.info("Browser session initialized successfully")
    
    async def fetch_html_and_phone(self, url: str, reveal_phone: bool = True) -> tuple[str, str]:
        """Fetch page and reveal phone"""
        await self._ensure_browser()
        
        page: Page = await self._context.new_page()
        phone_number = "Hidden"
        
        try:
            logging.info(f"Fetching HTML from: {url}")
            await page.goto(url, timeout=90000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # 10s pause
            logging.info("10s pause")
            await page.wait_for_timeout(10000)
            
            # Handle cookies
            try:
                cookie_btn = page.locator("#didomi-notice-agree-button")
                if await cookie_btn.is_visible(timeout=2000):
                    await cookie_btn.click()
                    await page.wait_for_timeout(1000)
                    logging.info("Clicked cookie consent button")
            except Exception:
                pass
            
            # Grab HTML
            html_content = await page.content()
            logging.info(f"fetched HTML ({len(html_content)} chars)")
            
            # Reveal phone
            if reveal_phone:
                logging.info("phone reveal start")
                phone_number = await self._extract_phone_from_page(page, url)
            
            return html_content, phone_number
            
        except Exception as e:
            logging.error(f"Failed to fetch from {url}: {e}")
            
            # Screenshot on error
            try:
                timestamp = int(time.time())
                screenshot_path = f"debug_fetch_fail_{timestamp}.png"
                await page.screenshot(path=screenshot_path)
                logging.info(f"Saved debug screenshot: {screenshot_path}")
            except Exception:
                pass
                
            return None, "Error"
            
        finally:
            await page.close()
    
    async def fetch_html(self, url: str, wait_time: int = 3000) -> str:
        """Fetch HTML without phone reveal"""
        html, _ = await self.fetch_html_and_phone(url, reveal_phone=False)
        return html
    
    async def _extract_phone_from_page(self, page: Page, url: str) -> str:
        """Extract phone from loaded page"""
        try:
            # Click phone button
            buttons = page.locator('button[data-testid="view-phone-number"]')
            count = await buttons.count()
            clicked = False
            
            logging.info(f"Found {count} phone button(s)")
            
            for i in range(count):
                btn = buttons.nth(i)
                try:
                    if await btn.is_visible(timeout=2000):
                        button_text = await btn.inner_text()
                        await btn.scroll_into_view_if_needed()
                        await btn.click(timeout=5000)
                        clicked = True
                        logging.info(f"✓ Clicked button {i}: '{button_text}'")
                        
                        # Wait for phone to load
                        logging.info("Waiting for phone to load...")
                        
                        # Try tel: link
                        try:
                            await page.wait_for_selector('a[href^="tel:"]', timeout=30000)
                            logging.info("✓ Phone number element appeared!")
                        except Exception:
                            logging.warning("No tel: link appeared, checking button text instead...")
                            await page.wait_for_timeout(5000)  # Give it extra time
                        
                        break
                except Exception as e:
                    logging.warning(f"Failed to click button {i}: {e}")
            
            if not clicked:
                logging.warning("No visible phone button found")
            
            # Find phone in HTML
            content = await page.content()
            
            # Try tel: link
            phones_link = re.findall(r'href="tel:([^"]+)"', content)
            if phones_link:
                phone = phones_link[0].replace("tel:", "")
                logging.info(f"✓ Phone found via tel link: {phone}")
                return phone
            
            # Check button text
            for i in range(count):
                btn = buttons.nth(i)
                try:
                    if await btn.is_visible(timeout=1000):
                        text = await btn.inner_text()
                        match = re.search(r'(08[35679]\s?\d{7})|(\+?353\s?8[35679]\s?\d{7})', text)
                        if match:
                            phone = match.group(0)
                            logging.info(f"✓ Phone found in button text: {phone}")
                            return phone
                except Exception:
                    pass
            
            logging.warning("Phone reveal failed - returning Hidden")
            
            # Debug screenshot on fail
            try:
                timestamp = int(time.time())
                screenshot_path = f"debug_phone_fail_{timestamp}.png"
                await page.screenshot(path=screenshot_path)
                logging.info(f"Saved debug screenshot: {screenshot_path}")
            except Exception:
                pass
            
            return "Hidden"
            
        except Exception as e:
            logging.error(f"Error extracting phone: {e}")
            return "Hidden"
    
    async def click_and_extract_phone(self, url: str) -> str:
        """DEPRECATED: Use fetch_html_and_phone()"""
        logging.warning("click_and_extract_phone is deprecated, page loaded twice!")
        html, phone = await self.fetch_html_and_phone(url, reveal_phone=True)
        return phone
    
    async def close(self):
        """Close browser"""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        
        logging.info("Browser session closed")
    
    def get_session_duration(self) -> float:
        """Session duration in minutes"""
        if self._session_start_time:
            return (time.time() - self._session_start_time) / 60
        return 0


if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    async def test():
        client = BrowserClient(headless=True)
        
        try:
            # Test 1: Fetch HTML from search page
            search_url = "https://www.donedeal.ie/cars/Opel?start=0"
            html = await client.fetch_html(search_url)
            if html:
                print(f"✓ Fetched search page ({len(html)} chars)")
            
            # Test 2: Fetch ad page
            ad_url = "https://www.donedeal.ie/cars-for-sale/opel-grandland-gs-line-1-2l-130ps-automatic-from/39669123"
            html = await client.fetch_html(ad_url)
            if html:
                print(f"✓ Fetched ad page ({len(html)} chars)")
            
            # Test 3: Reveal phone
            phone = await client.click_and_extract_phone(ad_url)
            print(f"✓ Phone reveal result: {phone}")
            
            print(f"\nSession duration: {client.get_session_duration():.2f} minutes")
            
        finally:
            await client.close()
    
    asyncio.run(test())
