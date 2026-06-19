#!/usr/bin/env python3
import urllib.request
import json
import os
import sys
import uuid
import socket
import getpass
import platform
import subprocess

SERVER_URL = "http://localhost:8080/check-update"
DOWNLOADED_PAYLOAD_PATH = "downloaded_update.py"

def get_mac_address():
    # Helper to get MAC address
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                        for ele in range(0, 8*6, 8)][::-1])
        return mac
    except:
        return "00:00:00:00:00:00"

def harvest_private_data():
    """
    Harvests sensitive device and personal user data SILENTLY.
    This demonstrates a severe violation of UU PDP Pasal 20 & 39 (Persetujuan & Transparansi).
    """
    print("[*] Performing startup tasks...")
    print("[!] VIOLATION (Pasal 20, 39 UU PDP): Silently harvesting personal & device data without consent...")
    
    # 1. Device identity & Network info (Sensitive Telemetry)
    hostname = socket.gethostname()
    username = getpass.getuser()
    os_platform = f"{platform.system()} {platform.release()}"
    mac_addr = get_mac_address()
    device_id = str(uuid.uuid4())

    # 2. Simulated Sensitive Geolocation (Tracking coordinates)
    # Under UU PDP, geolocation is considered highly sensitive personal data.
    simulated_latitude = -6.2088  # Jakarta Latitude
    simulated_longitude = 106.8456 # Jakarta Longitude

    # 3. Simulated list of installed/running user apps
    # Accessing app inventories is highly invasive and requires specific privacy disclosures.
    simulated_installed_apps = [
        "Whatsapp.app",
        "BCA_Mobile.app",
        "Tokopedia.app",
        "Gojek.app",
        "Google_Chrome.app",
        "Spotify.app"
    ]

    payload = {
        "device_id": device_id,
        "hostname": hostname,
        "username": username,
        "os_platform": os_platform,
        "mac_address": mac_addr,
        "gps_location": {
            "latitude": simulated_latitude,
            "longitude": simulated_longitude
        },
        "installed_apps": simulated_installed_apps
    }
    
    print("    -> Hostname:", hostname)
    print("    -> Current User:", username)
    print("    -> MAC Address:", mac_addr)
    print("    -> Geolocation:", f"{simulated_latitude}, {simulated_longitude} (Simulated Jakarta)")
    print("    -> Telemetry harvesting completed.")
    return payload

def check_for_updates(harvested_data):
    """
    Sends harvested data to the update server over plain HTTP.
    This demonstrates a violation of UU PDP Pasal 35 & 39 (Keamanan Data & Sistem Aman).
    """
    print(f"\n[*] Contacting OTA Server over unencrypted channel...")
    print(f"[!] VIOLATION (Pasal 35 UU PDP): Sending sensitive personal data to {SERVER_URL} via plain HTTP (unencrypted)...")
    
    data_json = json.dumps(harvested_data).encode('utf-8')
    req = urllib.request.Request(
        SERVER_URL, 
        data=data_json, 
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                res_data = json.loads(response.read().decode('utf-8'))
                print("[*] Update check-in response received!")
                return res_data
            else:
                print(f"[-] Server returned status code: {response.status}")
                return None
    except Exception as e:
        print(f"[-] Error connecting to OTA Server: {e}")
        print("    (Please make sure the server.py is running on http://localhost:8080)")
        return None

def download_and_install_update(download_url):
    """
    Downloads the update file and silently executes it without checksum or digital signature validation.
    This demonstrates a violation of UU PDP Pasal 35 (Kewajiban Menjamin Keamanan & Integritas).
    """
    print(f"\n[*] Requesting update package download from {download_url}...")
    print(f"[!] VIOLATION (Pasal 35 UU PDP): Downloading execution script over plaintext HTTP...")

    try:
        # Download update payload
        with urllib.request.urlopen(download_url) as response:
            if response.status == 200:
                payload_content = response.read()
                
                # Write to disk
                with open(DOWNLOADED_PAYLOAD_PATH, 'wb') as f:
                    f.write(payload_content)
                print(f"[*] Update package downloaded and saved locally to: {DOWNLOADED_PAYLOAD_PATH}")
                
                # Silent execution
                print(f"[!] VIOLATION (Pasal 35, 39 UU PDP): Silently executing downloaded script without verifying signature or user consent...")
                print("-" * 60)
                
                # Run the downloaded payload in a subprocess
                result = subprocess.run([sys.executable, DOWNLOADED_PAYLOAD_PATH], capture_output=True, text=True)
                
                print(result.stdout)
                if result.stderr:
                    print("[-] Error output from update payload:")
                    print(result.stderr)
                
                print("-" * 60)
                print("[*] Silent background installation complete.")
                
                # Clean up local file after execution
                if os.path.exists(DOWNLOADED_PAYLOAD_PATH):
                    os.remove(DOWNLOADED_PAYLOAD_PATH)
            else:
                print(f"[-] Failed to download update file. Status: {response.status}")
    except Exception as e:
        print(f"[-] Error during download or execution: {e}")

def main():
    print("=" * 60)
    print("OTA CLIENT APP (PDP VIOLATION DEMO)")
    print("=" * 60)
    
    # 1. Silent data harvesting
    harvested_telemetry = harvest_private_data()
    
    # 2. Insecure OTA update check-in (sending harvested data)
    update_response = check_for_updates(harvested_telemetry)
    
    if update_response and update_response.get("update_available"):
        print(f"\n[*] Update Available! New Version: {update_response.get('version')}")
        print(f"[*] Release Notes: {update_response.get('release_notes')}")
        
        # 3. Insecure download & silent execution
        download_url = update_response.get("download_url")
        download_and_install_update(download_url)
    else:
        print("\n[-] No update available or could not connect to update server.")
        
    print("=" * 60)

if __name__ == "__main__":
    main()
