import requests
import os
import sys

# ---------------- CONFIG ----------------
ZONE_ID = "1ccb28f8be8421a2b3e467bd53f54258"
RECORD_NAME = "themavennest.shop"
PRIMARY_IP = "91.99.219.182"
FAILOVER_IP = "91.98.125.83"
CHECK_PORT = 9100
TIMEOUT = 5  # seconds

# ---------------- TOKEN VALIDATION ----------------
CF_TOKEN = os.environ.get("CF_TOKEN", "").strip()
if not CF_TOKEN:
    print("Error: CF_TOKEN is missing or empty!")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {CF_TOKEN}",
    "Content-Type": "application/json"
}

# ---------------- CHECK PRIMARY SERVER ----------------
check_url = f"http://{PRIMARY_IP}:{CHECK_PORT}"
try:
    response = requests.get(check_url, timeout=TIMEOUT)
    server_up = response.status_code == 200
except requests.RequestException:
    server_up = False

# Decide which IP to set
new_ip = PRIMARY_IP if server_up else FAILOVER_IP
print(f"Primary server up: {server_up}. DNS will be set to {new_ip}")

# ---------------- FETCH EXISTING A RECORD ----------------
url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records?type=A&name={RECORD_NAME}"
try:
    res = requests.get(url, headers=HEADERS, timeout=TIMEOUT).json()
except requests.RequestException as e:
    print("Error fetching DNS record:", e)
    sys.exit(1)

if not res.get("success") or len(res.get("result", [])) == 0:
    print("Failed to fetch DNS record:", res)
    sys.exit(1)

record = res["result"][0]
record_id = record["id"]
current_ip = record["content"]
proxied_status = record.get("proxied", False)

if current_ip == new_ip:
    print(f"DNS IP is already {current_ip}. No update needed.")
    sys.exit(0)

# ---------------- UPDATE DNS RECORD ----------------
update_url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{record_id}"
payload = {
    "type": "A",
    "name": RECORD_NAME,
    "content": new_ip,
    "ttl": 1,  # Auto
    "proxied": proxied_status
}

try:
    update_res = requests.put(update_url, headers=HEADERS, json=payload, timeout=TIMEOUT).json()
except requests.RequestException as e:
    print("Error updating DNS record:", e)
    sys.exit(1)

if update_res.get("success"):
    print(f"DNS successfully updated from {current_ip} → {new_ip}")
else:
    print("Failed to update DNS:", update_res)
