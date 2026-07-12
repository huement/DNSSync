import os
import requests
from dotenv import load_dotenv

# Load the variables from the .env file into the system environment
load_dotenv()

# --- CONFIGURATION ---
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
CF_ZONE_ID = os.getenv("CF_ZONE_ID")
DOMAIN_NAME = os.getenv("DOMAIN_NAME", "huement.com") 
RECORD_TYPE = os.getenv("RECORD_TYPE", "A")
# ---------------------

# Validation check to stop the script if the .env file is missing keys
if not CF_API_TOKEN or not CF_ZONE_ID:
    print("[-] Error: Missing Cloudflare credentials in the .env file.")
    exit(1)

# Add this right under the configuration block to see what Python reads:
# Add this right under the configuration block to see what Python reads:
print(f"[DEBUG] Domain Name: '{DOMAIN_NAME}'")
#print(f"[DEBUG] Zone ID: '{CF_ZONE_ID[:4]}...{CF_ZONE_ID[-4:] if CF_ZONE_ID else ""}' (Length: {len(CF_ZONE_ID) if CF_ZONE_ID else 0})")
#print(f"[DEBUG] API Token: '{CF_API_TOKEN[:4]}...{CF_API_TOKEN[-4:] if CF_API_TOKEN else ""}' (Length: {len(CF_API_TOKEN) if CF_API_TOKEN else 0})")

headers = {
    "Authorization": f"Bearer {CF_API_TOKEN}",
    "Content-Type": "application/json"
}

def get_current_public_ip():
    # Hits the IPv4-specific endpoint to get your public router IP
    url = "https://api4.ipify.org?format=json"
    response = requests.get(url, timeout=10).json()
    return response["ip"]

def get_cloudflare_record():
    url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records?name={DOMAIN_NAME}&type={RECORD_TYPE}"
    response = requests.get(url, headers=headers, timeout=10).json()
    
    # 1. Check if Cloudflare rejected the API request entirely
    if not response.get("success"):
        print("[-] Cloudflare API Authorization Error!")
        print("[-] Details:", response.get("errors"))
        return None
        
    # 2. Check if the connection worked, but the record name is wrong
    if not response.get("result"):
        print(f"[-] Connected to Cloudflare, but couldn't find an exact record matching '{DOMAIN_NAME}' with type '{RECORD_TYPE}'.")
        return None
        
    return response["result"][0]

def update_cloudflare_record(record_id, current_ip):
    url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records/{record_id}"
    data = {
        "type": RECORD_TYPE,
        "name": DOMAIN_NAME,
        "content": current_ip,
        "ttl": 1,         # Automatic TTL
        "proxied": True   # Keeps your home IP hidden behind Cloudflare
    }
    response = requests.patch(url, headers=headers, json=data, timeout=10).json()
    
    if response["success"]:
        print(f"[+] Successfully updated {DOMAIN_NAME} to {current_ip}")
    else:
        print("[-] Failed to update Cloudflare:", response["errors"])

def main():
    try:
        current_ip = get_current_public_ip()
        print(f"[i] Current public IPv4 address: {current_ip}")
        
        record = get_cloudflare_record()
        if not record:
            return
            
        cf_ip = record["content"]
        record_id = record["id"]
        
        if current_ip == cf_ip:
            print("[i] IP matches Cloudflare. No update needed.")
        else:
            print(f"[!] IP changed from {cf_ip} to {current_ip}. Syncing...")
            update_cloudflare_record(record_id, current_ip)
            
    except Exception as e:
        print(f"[-] An error occurred: {e}")

if __name__ == "__main__":
    main()
