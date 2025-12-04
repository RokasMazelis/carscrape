# DoneDeal Car Scraper

Simple scraper for DoneDeal.ie that grabs car listings with phone numbers revealed.

## What works best

Use `test_dealer_page.py` - it has the best success rate for phone number extraction.

```bash
python test_dealer_page.py
```

## Setup

1. Install dependencies:
```bash
pip install playwright beautifulsoup4 python-dotenv
playwright install chromium
```

2. Copy `.env.example` to `.env` and add your proxy credentials:
```bash
cp .env.example .env
```

Edit `.env` with your Decodo/SmartProxy details:
```
DECODO_PROXY_HOST=your-proxy-host
DECODO_PROXY_PORT=8000
DECODO_PROXY_USERNAME=your-username
DECODO_PROXY_PASSWORD=your-password
```

## How it works

- Uses Playwright for browser automation
- Runs through Decodo proxy (Irish IP)
- Clicks phone reveal buttons and extracts numbers
- Saves to CSV with all car details

## Files

- `browser_client.py` - Playwright browser automation
- `scraper.py` - Main scraper logic
- `test_dealer_page.py` - **Best working script** (use this one)
- `run_scraper.py` - Alternative runner
- `oxylabs_client.py` - Oxylabs proxy support
- `smart_proxy_client.py` - SmartProxy/CloudScraper support

## Output

Results saved to `donedeal_cars.csv` with columns:
- id, url, phone, title, price
- make, model, year, mileage
- fuel_type, transmission, engine_size
- and more...

## Notes

- Headless mode sometimes fails (detection), so test_dealer_page runs with visible browser
- Wait times are important - the script waits 10s after page load before clicking phone buttons
- Cookies included for testing but you can capture your own

## Troubleshooting

**Phone numbers showing as "Hidden"?**
- Try running with `headless=False` 
- Check proxy is working
- Make sure you have valid cookies (or let browser create session)

**Proxy errors?**
- Verify credentials in `.env`
- Test with one of the `test_*.py` scripts first
