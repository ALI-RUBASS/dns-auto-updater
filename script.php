
<?php
// Cloudflare DNS Auto-Updater
// Updates A record of themavennest.shop to current server IP

$zone_id = "YOUR_ZONE_ID"; // Replace with your Cloudflare Zone ID
$record_name = "themavennest.shop";
$new_ip = "91.99.219.182"; // or dynamically fetch if needed
$api_token = getenv('CF_TOKEN'); // From GitHub Secret

// Get all DNS records
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

// Update the DNS record
$update_url = "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records/$record_id";
$payload = json_encode([
    "type" => "A",
    "name" => $record_name,
    "content" => $new_ip,
    "ttl" => 300,
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

echo "Response: " . $update_response . PHP_EOL;
