# DNSSync

This is a simple Python project that uses the Cloudflare API to keep your DNS records up to date. 

If you are hosting a project and DONT have a static IP address from your ISP, then eventually things will break. There are DynamicDNS services that alleviate this issue, but usually they cost money. 

This is a poor man's DynamicDNS setup. To use this, you must be using Cloudflare for your DNS, the free plan will work fine. 

So head over the the **Account API Tokens** page, create a token, and fill in the values in the .env.example file, rename that to .env and thats it!

```bash

CF_API_TOKEN="your_token_here"
CF_ZONE_ID="your_zone_id_here"
# IF you use -single.py use this
DOMAIN_NAME="example.com"

# IF you are using the regular one, use the comma separated list
DOMAIN_NAMES="example.com,subdomain.example.com"
RECORD_TYPE="A"

```

Then you are going to want to use CRON or something to constantly have this script run, so whenever your IP is updated from the ISP, your cloudflare account will update along with it. 

```bash
*/5 * * * * cd /absolute/path/DNSSync && ./venv/bin/python ipv4Sync.py >> ddns.log 2>&1
```

### Single vs List

There are two versions of the script, one is for changing a SINGLE DNS entry, thats the `-single.py` file, if you have multiple domains that all need updating, you would use the regular file and the comma separated list in the `.env` file. 