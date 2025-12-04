import json

def fix_cookies():
    try:
        with open("cookies_fresh.json", "r") as f:
            cookies = json.load(f)
        
        fixed_cookies = []
        for c in cookies:
            # Create a clean cookie object compliant with Playwright
            new_cookie = {
                "name": c["name"],
                "value": c["value"],
                "domain": c["domain"],
                "path": c.get("path", "/"),
                "secure": True,
                "sameSite": "Lax"
            }
            fixed_cookies.append(new_cookie)
            
        with open("cookies_fresh.json", "w") as f:
            json.dump(fixed_cookies, f, indent=2)
            
        print(f"Fixed {len(fixed_cookies)} cookies.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_cookies()
