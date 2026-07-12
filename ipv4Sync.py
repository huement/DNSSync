import os
import requests
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# --- CONFIGURATION ---
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CF_ZONE_ID = os.getenv("CF_ZONE_ID")
RECORD_TYPE = os.getenv("RECORD_TYPE", "A")  

# Read the comma-separated string and turn it into a clean Python list
raw_domains = os.getenv("DOMAIN_NAMES", "")
DOMAINS = [d.strip() for d in raw_domains.split(",") if d.strip()]
# ---------------------

if not CF_API_TOKEN or not CF_ZONE_ID or not DOMAINS:
    print("[-] Error: Missing Cloudflare credentials or DOMAIN_NAMES in the .env file.")
    exit(1)

headers = {
    "Authorization": f"Bearer {CF_API_TOKEN}",
    "Content-Type": "application/json"
}

def get_current_public_ip():
    url = "https://api4.ipify.org?format=json"
    response = requests.get(url, timeout=10).json()
    return response["ip"]

def get_cloudflare_record(domain):
    url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records?name={domain}&type={RECORD_TYPE}"
    response = requests.get(url, headers=headers, timeout=10).json()
    
    if not response.get("success"):
        print(f"[-] Cloudflare API Authorization Error checking {domain}!")
        print("[-] Details:", response.get("errors"))
        return None
        
    if not response.get("result"):
        print(f"[-] Connected to Cloudflare, but couldn't find an exact record matching '{domain}'.")
        return None
        
    return response["result"][0]

def update_cloudflare_record(record_id, domain, current_ip):
    url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records/{record_id}"
    data = {
        "type": RECORD_TYPE,
        "name": domain,
        "content": current_ip,
        "ttl": 1,
        "proxied": True
    }
    response = requests.patch(url, headers=headers, json=data, timeout=10).json()
    
    if response["success"]:
        print(f"[+] Successfully updated {domain} to {current_ip}")
    else:
        print(f"[-] Failed to update {domain}:", response["errors"])

def main():
    try:
        # Step 1: Get your current home public IP (only call this once!)
        current_ip = get_current_public_ip()
        print(f"[i] Current public IPv4 address: {current_ip}")
        print("-" * 50)
        
        # Step 2: Loop through every domain in your list
        for domain in DOMAINS:
            print(f"[>] Processing {domain}...")
            record = get_cloudflare_record(domain)
            if not record:
                continue
                
            cf_ip = record["content"]
            record_id = record["id"]
            
            if current_ip == cf_ip:
                print(f"[i] {domain} matches Cloudflare. No update needed.")
            else:
                print(f"[!] {domain} IP changed from {cf_ip} to {current_ip}. Syncing...")
                update_cloudflare_record(record_id, domain, current_ip)
            print("-" * 50)
            
    except Exception as e:
        print(f"[-] An error occurred: {e}")

if __name__ == "__main__":
    main()
