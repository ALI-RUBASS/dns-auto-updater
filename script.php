<?php
// Cloudflare DNS Auto-Updater
// Updates A record of themavennest.shop to current server IP

$zone_id = "1ccb28f8be8421a2b3e467bd53f54258";
$record_name = "themavennest.shop";
$api_token = getenv('CF_TOKEN');

// Fetch current public IP
$new_ip = trim(file_get_contents('https://api.ipify.org'));
if (filter_var($new_ip, FILTER_VALIDATE_IP) === false) {
    echo "Failed to fetch a valid public IP.\n";
    exit(1);
}

// Get existing A record
$url = "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records?type=A&name=$record_name";

$headers = [
    "Authorization: Bearer $api_token",
    "Content-Type: application/json"
];

$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL => $url,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => $headers,
]);
$response = curl_exec($ch);
curl_close($ch);

$data = json_decode($response, true);

if (!$data["success"] || empty($data["result"])) {
    echo "Failed to fetch DNS record: " . $response . PHP_EOL;
    exit(1);
}

$record_id = $data["result"][0]["id"];
$current_ip = $data["result"][0]["content"];

// Only update if IP has changed
if ($current_ip === $new_ip) {
    echo "IP unchanged ($new_ip). No update needed.\n";
    exit(0);
}

// Update the DNS record
$update_url = "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records/$record_id";
$payload = json_encode([
    "type" => "A",
    "name" => $record_name,
    "content" => $new_ip,
    "ttl" => 1,
    "proxied" => true
]);

$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL => $update_url,
    CURLOPT_CUSTOMREQUEST => "PUT",
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => $headers,
    CURLOPT_POSTFIELDS => $payload,
]);
$update_response = curl_exec($ch);
curl_close($ch);

echo "Update response: " . $update_response . PHP_EOL;
