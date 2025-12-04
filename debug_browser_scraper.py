import logging
import time
import random
import re
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("browser_debug.log"),
        logging.StreamHandler()
    ]
)

# User Provided Credentials
PROXY_HOST = "gate.decodo.com"
PROXY_PORT = "10001"
PROXY_USER = "user-spnn7jyi3f-asn-13280"
PROXY_PASS = "f3zHx753fZt~nEibMx"

# Proxy Configuration
PROXY_CONFIG = {
    "server": f"http://{PROXY_HOST}:{PROXY_PORT}",
    "username": PROXY_USER,
    "password": PROXY_PASS
}

# Target URL (from CSV)
TARGET_URL = "https://www.donedeal.ie/cars-for-sale/opel-grandland-gs-line-1-2l-130ps-automatic-from/39669123?campaign=3"

def run_browser_debug():
    logging.info("Starting Browser Debug with Decodo Proxy...")
    
    with sync_playwright() as p:
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--window-size=1920,1080",
        ]
        
        logging.info(f"Launching browser with proxy: {PROXY_HOST}:{PROXY_PORT}")
        
        # Launch Browser
        browser = p.chromium.launch(
            headless=True, # Must be True in this env, but user can run False locally
            proxy=PROXY_CONFIG,
            args=browser_args
        )
        
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="en-IE",
            timezone_id="Europe/Dublin"
        )
        
        page = context.new_page()
        
        try:
            # 1. Check IP
            logging.info("Checking IP Address...")
            try:
                page.goto("https://ip.decodo.com/json", timeout=30000)
                content = page.inner_text("body")
                logging.info(f"Current IP Info: {content}")
                page.screenshot(path="debug_artifacts/0_ip_check.png")
            except Exception as e:
                logging.error(f"Failed to check IP: {e}")

            # 2. Go to Target URL
            logging.info(f"Navigating to: {TARGET_URL}")
            page.goto(TARGET_URL, timeout=60000, wait_until="domcontentloaded")
            time.sleep(5) # Wait for initial load
            
            # Screenshot Initial State
            page.screenshot(path="debug_artifacts/1_page_loaded.png")
            
            # Handle Cookies (Didomi)
            logging.info("Checking for cookie banner...")
            try:
                # Wait a bit for it to appear
                cookie_btn = page.locator("#didomi-notice-agree-button")
                if cookie_btn.is_visible():
                    logging.info("Cookie banner visible. Clicking...")
                    cookie_btn.click()
                    time.sleep(2)
                else:
                    logging.info("Cookie banner not visible immediately.")
            except Exception as e:
                logging.warning(f"Cookie handling warning: {e}")

            # 3. Find Button
            # Use :visible pseudo-class to find the interactable one
            button_selector = 'button[data-testid="view-phone-number"]:visible'
            
            # Wait for it to be visible
            try:
                page.wait_for_selector(button_selector, state="visible", timeout=10000)
            except:
                logging.warning("Visible phone button not found in 10s.")

            buttons = page.locator(button_selector)
            count = buttons.count()
            logging.info(f"Found {count} VISIBLE 'Show Phone Number' buttons.")
            
            if count > 0:
                button = buttons.first
                
                # Scroll into view
                button.scroll_into_view_if_needed()
                time.sleep(1)
                
                page.screenshot(path="debug_artifacts/2_before_click.png")
                
                # 4. Click Button
                logging.info("Clicking button...")
                try:
                    button.click(timeout=5000)
                except Exception as click_e:
                    logging.warning(f"Standard click failed: {click_e}. Trying JS click.")
                    button.evaluate("e => e.click()")

                # Wait for reaction (text change or network)
                time.sleep(5)
                
                page.screenshot(path="debug_artifacts/3_after_click.png")
                
                # Check result (Text change or Link)
                # Re-query the element or check its parent/replacement
                
                # Check for tel link anywhere in that area
                tel_links = page.locator('a[href^="tel:"]')
                if tel_links.count() > 0:
                     href = tel_links.first.get_attribute("href")
                     logging.info(f"Found Revealed Number (tel link): {href}")
                else:
                     # Check button text again
                     btn_text = button.inner_text()
                     logging.info(f"Button text after click: {btn_text}")
            else:
                logging.error("No visible phone button found.")
                page.screenshot(path="debug_artifacts/2_no_button_visible.png")

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            page.screenshot(path="debug_artifacts/error_state.png")
            
        finally:
            browser.close()
            logging.info("Browser closed.")

if __name__ == "__main__":
    run_browser_debug()
