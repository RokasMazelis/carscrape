import logging
import re
from phone_revealer import PhoneRevealer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_links(filepath="links to test.md"):
    with open(filepath, "r") as f:
        lines = f.readlines()
    
    links = []
    for line in lines:
        line = line.strip()
        if line and line.startswith("http"):
            links.append(line)
    return links

def main():
    links = load_links()
    if not links:
        print("No links found in 'links to test.md'")
        return

    print(f"Found {len(links)} links to test.")
    
    revealer = PhoneRevealer(headless=True)
    
    results = []
    
    for i, link in enumerate(links):
        print(f"\n[{i+1}/{len(links)}] Testing: {link}")
        try:
            number = revealer.get_number(link)
            print(f"Result: {number}")
            results.append({"url": link, "number": number})
        except Exception as e:
            print(f"Error: {e}")
            results.append({"url": link, "number": "Error"})

    print("\n--- Summary ---")
    for res in results:
        print(f"{res['number']} | {res['url']}")

if __name__ == "__main__":
    main()
