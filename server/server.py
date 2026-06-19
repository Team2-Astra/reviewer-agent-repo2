#!/usr/bin/env python3
import http.server
import json
import os
import csv
from datetime import datetime

PORT = 8080
HARVESTED_DATA_FILE = "harvested_user_data.csv"
UPDATE_VERSION = "2.0.0"
UPDATE_FILE_PATH = "updates/update_payload.py"

class OTAServerHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override to log cleanly to console
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Server Log: {format%args}")

    def do_GET(self):
        if self.path == "/download-update":
            self.serve_update_file()
        else:
            self.send_error(404, "Endpoint not found")

    def do_POST(self):
        if self.path == "/check-update":
            self.handle_check_update()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_check_update(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            client_data = json.loads(post_data.decode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON format"}).encode())
            return

        # VULNERABILITY / PDP VIOLATION: Logging highly sensitive personal/device data 
        # in plaintext (CSV) without consent or security controls (Pasal 35, 39, 43 UU PDP).
        print(f"\n[!] VIOLATION (Pasal 20, 35 UU PDP): Received harvested telemetry from client IP {self.client_address[0]}:")
        print(json.dumps(client_data, indent=2))
        
        self.save_harvested_data(self.client_address[0], client_data)

        # Respond with update info.
        # VULNERABILITY / PDP VIOLATION: Providing update package URL over insecure HTTP,
        # with no checksum/hash/signature for the client to verify integrity (Pasal 35 UU PDP).
        update_info = {
            "update_available": True,
            "version": UPDATE_VERSION,
            "download_url": f"http://localhost:{PORT}/download-update",
            "release_notes": "Silent telemetry integration and core module performance optimizations.",
            "md5_checksum": "" # Intentionally left blank or omitted to demonstrate lack of integrity checks
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(update_info).encode())

    def serve_update_file(self):
        if not os.path.exists(UPDATE_FILE_PATH):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Update package file not found on server.")
            return

        print(f"\n[!] VIOLATION (Pasal 35 UU PDP): Serving unsigned update binary over unencrypted HTTP to {self.client_address[0]}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/octet-stream')
        self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(UPDATE_FILE_PATH)}"')
        self.end_headers()
        
        with open(UPDATE_FILE_PATH, 'rb') as f:
            self.wfile.write(f.read())

    def save_harvested_data(self, ip_address, data):
        # Create CSV header if file doesn't exist
        file_exists = os.path.exists(HARVESTED_DATA_FILE)
        
        fieldnames = [
            "timestamp", "client_ip", "device_id", "hostname", 
            "username", "os_platform", "mac_address", 
            "simulated_gps_latitude", "simulated_gps_longitude", 
            "installed_apps_count"
        ]

        # Extract values
        row = {
            "timestamp": datetime.now().isoformat(),
            "client_ip": ip_address,
            "device_id": data.get("device_id", "UNKNOWN"),
            "hostname": data.get("hostname", "UNKNOWN"),
            "username": data.get("username", "UNKNOWN"),
            "os_platform": data.get("os_platform", "UNKNOWN"),
            "mac_address": data.get("mac_address", "UNKNOWN"),
            "simulated_gps_latitude": data.get("gps_location", {}).get("latitude", "N/A"),
            "simulated_gps_longitude": data.get("gps_location", {}).get("longitude", "N/A"),
            "installed_apps_count": len(data.get("installed_apps", []))
        }

        with open(HARVESTED_DATA_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        
        print(f"[*] Plaintext data appended to: {os.path.abspath(HARVESTED_DATA_FILE)}")

def run_server():
    # Ensure updates folder exists
    os.makedirs(os.path.dirname(UPDATE_FILE_PATH), exist_ok=True)
    
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, OTAServerHandler)
    print("=" * 60)
    print(f"OTA INSECURE SERVER (PDP VIOLATION DEMO) STARTING ON PORT {PORT}...")
    print(f"Harvested data will be saved to: {os.path.abspath(HARVESTED_DATA_FILE)}")
    print(f"Update payload will be served from: {os.path.abspath(UPDATE_FILE_PATH)}")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping OTA Server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
