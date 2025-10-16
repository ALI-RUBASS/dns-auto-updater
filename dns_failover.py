import requests
import os

# Config
zone_id = "1ccb28f8be8421a2b3e467bd53f54258"
record_name = "themavennest.shop"
cf_token = os.environ.get("CF_TOKEN")  # GitHub Secret

primary_ip = "91.99.219.182"
failover_ip = "91.98.125.83"
check_url = f"http://{primary_ip}:9100"

headers = {
    "Authorization": f"Bearer {cf_token}",
    "Content-Type": "application/json"
}

# 1. Check if primary server is up
try:
    response = requests.get(check_url, timeout=5)
    server_up = response.status_code == 200
except requests.RequestException:
    server_up = False

# Decide which IP to set
new_ip = primary_ip if server_up else failover_ip
print(f"Server up: {server_up}. Setting DNS to {new_ip}")

# 2. Get existing A record
url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={record_name}"
res = requests.get(url, headers=headers).json()

if not res["success"] or len(res["result"]) == 0:
    print("Failed to fetch DNS record:", res)
    exit(1)

record = res["result"][0]
record_id = record["id"]
current_ip = record["content"]

if current_ip == new_ip:
    print("DNS IP is already correct. No update needed.")
    exit(0)

# 3. Update DNS record
update_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
payload = {
    "type": "A",
    "name": record_name,
    "content": new_ip,
    "ttl": 1,
    "proxied": record["proxied"]  # keep current proxied setting
}

update_res = requests.put(update_url, headers=headers, json=payload).json()
print("Update response:", update_res)
