import os

def fix_env():
    try:
        with open(".env", "r") as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                new_lines.append(line)
                continue
                
            # Remove lines that look like shell commands
            if stripped.startswith("curl "):
                print(f"Removing bad line: {stripped[:10]}...")
                continue
                
            # Fix typo
            if stripped.startswith("OXULA"):
                print(f"Fixing typo: {stripped[:10]}...")
                line = line.replace("OXULA", "OXYLABS")
            
            new_lines.append(line)
            
        with open(".env", "w") as f:
            f.writelines(new_lines)
        print("Fixed .env file.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_env()
