import asyncio
import os
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def main():
    url = "https://www.donedeal.ie/cars-for-sale/opel-grandland-gs-line-1-2l-130ps-automatic-from/39669123?campaign=3"
    
    print(f"Testing Crawl4AI on: {url}")

    # Browser config
    proxy_str = f"http://{os.getenv('DECODO_PROXY_USERNAME')}:{os.getenv('DECODO_PROXY_PASSWORD')}@{os.getenv('DECODO_PROXY_HOST')}:{os.getenv('DECODO_PROXY_PORT')}"
    
    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
        proxy=proxy_str,
        enable_stealth=True,
        extra_args=["--use-mock-keychain", "--password-store=basic"]
    )

    # JS code
    js_code = """
    (async () => {
        console.log("Starting JS execution...");
        
        // Helper to wait
        const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));
        
        // 1. Handle Cookies (Aggressive)
        try {
            const cookieBtn = document.querySelector("#didomi-notice-agree-button");
            if (cookieBtn) {
                console.log("Found cookie banner, clicking...");
                cookieBtn.click();
                await wait(1500);
            }
            // Remove overlay
            const host = document.querySelector('#didomi-host');
            if(host) host.remove();
        } catch (e) {
            console.log("Cookie handling error: " + e);
        }

        // Click phone button
        const btnSelector = 'button[data-testid="view-phone-number"]';
        let clicked = false;
        
        for(let i=0; i<5; i++) {
            try {
                const btn = document.querySelector(btnSelector);
                if (btn) {
                    console.log(`Attempt ${i+1}: Found phone button.`);
                    
                    // Check if revealed
                    if (btn.querySelector("a[href^='tel:']") || btn.innerText.match(/\d{6,}/)) {
                        console.log("Phone number already revealed!");
                        clicked = true;
                        break;
                    }

                    console.log("Scrolling...");
                    btn.scrollIntoView({behavior: "instant", block: "center"});
                    await wait(500);
                    
                    console.log("Clicking...");
                    btn.click();
                    
                    // React workaround
                    btn.dispatchEvent(new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    }));
                    
                    await wait(2000);
                    
                    const btnAfter = document.querySelector(btnSelector);
                    if (btnAfter) {
                         const btnText = btnAfter.innerText.trim();
                         console.log(`Button text after click: "${btnText}"`);
                         
                         if (btnAfter.querySelector("a[href^='tel:']") || btnText.match(/\d{6,}/)) {
                             console.log("Success! Number revealed.");
                             clicked = true;
                             break;
                         }
                    } else {
                        console.log("Button element disappeared/replaced. Searching for number in container...");
                    }
                } else {
                    console.log(`Attempt ${i+1}: Button not found.`);
                }
            } catch (e) {
                console.log("Button interaction error: " + e);
            }
            await wait(1000);
        }
        
        if(!clicked) console.log("Failed to reveal number after retries.");
        
    })();
    """

    run_config = CrawlerRunConfig(
        js_code=[js_code],
        cache_mode=CacheMode.BYPASS, 
        screenshot=True, 
        magic=True,
        log_console=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=url,
            config=run_config
        )
        
        if result.success:
            print("Crawl successful!")
            
            if result.screenshot:
                import base64
                with open("crawl4ai_screenshot.png", "wb") as f:
                    f.write(base64.b64decode(result.screenshot))
                print("Saved screenshot to crawl4ai_screenshot.png")

            import re
            phones_link = re.findall(r'href="tel:([^"]+)"', result.html)
            phones_text = re.findall(r'08\d\s?\d{7}', result.html)
            
            if phones_link:
                print("Found 'tel:' link in HTML:", phones_link)
            elif phones_text:
                print("Found phone-like text in HTML:", phones_text)
            else:
                print("No phone number found in final HTML.")
                with open("crawl4ai_debug.html", "w") as f:
                    f.write(result.html)
                print("Saved HTML to crawl4ai_debug.html")
        else:
            print("Crawl failed:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
