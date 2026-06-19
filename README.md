# Insecure OTA Update & Indonesian UU PDP Violations Demo

This project is a mock **Over-The-Air (OTA) Update System** intentionally implemented with critical privacy and security flaws. It is designed to act as a **vulnerability and compliance testbed** to demonstrate violations against Indonesia's Personal Data Protection Law (**UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi / UU PDP**). 

You can use this project to test, demonstrate, and calibrate a **compliance scanner** or **privacy audit tool** that flags code-level and network-level privacy violations.

---

## 🌟 Visualizing the Architecture & Data Flow

This diagram illustrates how the client and server interact, and highlights where the critical UU PDP violations occur in the lifecycle of an OTA update check-in.

```mermaid
sequence_graph
%% Diagram representation of insecure OTA flow
sequenceDiagram
    autonumber
    actor User as Device / User
    participant Client as OTA Client (App)
    participant Server as OTA Insecure Server

    Note over Client: Startup Event
    Client->>Client: Silently harvests Username, MAC,<br/>Simulated GPS & App Lists
    Note over Client: VIOLATION: Pasal 20 & 39<br/>(No User Consent / Dialog)

    Client->>Server: HTTP POST /check-update<br/>[Plaintext JSON Telemetry]
    Note over Client, Server: VIOLATION: Pasal 35 & 39<br/>(Insecure HTTP Transit)

    Note over Server: Receive Telemetry
    Server->>Server: Appends raw data to<br/>harvested_user_data.csv
    Note over Server: VIOLATION: Pasal 43 & 44<br/>(Indefinite Plaintext PII Log)

    Server-->>Client: HTTP 200 OK<br/>[Update Info & http:// download_url]
    Note over Server, Client: No cryptographic signatures<br/>or package hashes provided

    Client->>Server: HTTP GET /download-update
    Server-->>Client: HTTP 200 OK [Unsigned update_payload.py]

    Note over Client: Download Complete
    Client->>Client: Silently executes update_payload.py<br/>in a subprocess via sys.executable
    Note over Client: VIOLATION: Pasal 35 & 39<br/>(Silent execution, no verification)<br/>Vulnerable to Remote Code Execution!
```

---

## 📁 Project Directory Structure

```text
indonesia-ota-pdp-violation/
├── client/
│   └── client.py                 # Mock Client (silent harvesting, plain HTTP, insecure run)
├── server/
│   ├── server.py                 # Mock HTTP Server (collects data, plain log, serves payload)
│   └── updates/
│       └── update_payload.py     # Unsigned mock update script (executable payload)
├── violations_report.md          # Comprehensive regulatory analysis and scan indicators
└── README.md                     # This documentation file
```

---

## 🚀 Quick Start Guide

This project runs entirely on **Python 3** using built-in libraries (no `pip install` required), ensuring a seamless startup experience.

### Step 1: Start the OTA Server
Open a terminal window and launch the insecure server script:
```bash
python3 server/server.py
```
*The server will start up on `http://localhost:8080` and wait for check-ins. Harvested user information will be saved directly in `harvested_user_data.csv`.*

### Step 2: Run the OTA Client
In a separate terminal window, execute the client application:
```bash
python3 client/client.py
```
*The client will automatically gather device and personal metadata, send it to the server over insecure HTTP, download the update package, and execute it silently in the background.*

---

## 🔍 Observing the Compliance Violations

As you execute the scripts, pay attention to the output in both terminals and the generated files:

1.  **Consent Absence (Pasal 20 & 22):** 
    Look at the Client terminal. The script immediately prints `Silently harvesting personal & device data without consent...` and gathers usernames, MAC addresses, and geolocation without requesting user input or showing an opt-in screen.
2.  **Plaintext Transmission (Pasal 35 & 39):**
    The client logs show it connecting via unencrypted HTTP (`http://localhost:8080/check-update`) instead of HTTPS, sending raw telemetry data across the network in cleartext JSON.
3.  **Indefinite Storage & Lack of Erasure (Pasal 43 & 44):**
    After running the client, inspect the newly created file `harvested_user_data.csv` in the server's working directory. You will find all harvested personal details logged in plaintext, with no retention schedule, access controls, or user deletion mechanism.
4.  **No Integrity Check / Remote Code Execution (Pasal 35):**
    The client downloads `update_payload.py` and runs it instantly via `subprocess.run()`. Because the update lacks a developer signature, SHA-256 hash check, or security verification, any network interceptor could rewrite this update payload to run malicious shell commands.

---

## 🛠️ Testing Your Compliance Scanner

This project serves as a concrete target for several scanning styles:

### A. Static Code Analysis (SAST)
Point your source code scanner at `client/client.py`. It should flag:
*   Use of insecure connection strings starting with `http://` (**Vulnerability**).
*   Sinks like `subprocess.run([sys.executable, ...])` processing files fetched directly from network resources without hash checking (`hashlib`) or digital signatures (**Insecure RCE**).
*   System variables being accessed (`getpass.getuser()`, `uuid.getnode()`) without conditional access gates (**Invasive Telemetry**).

### B. Dynamic Analysis & Network Inspection (DAST / DAST Proxy)
Intercept local loopback traffic on port `8080` when executing the client. Your security proxy should flag:
*   Plaintext transmission of JSON payloads containing `gps_location` (`latitude`/`longitude`), `mac_address`, and user details.
*   Serving execution binaries/scripts (`.py` files) over unencrypted content types.

### C. Data Discovery Scan (PII Scan)
Scan the server's workspace folder after running. Your PII discovery rules should easily find:
*   `harvested_user_data.csv` containing unencrypted email/username strings, IP addresses, MAC IDs, and GPS coordinate pairs.

---

## 📄 Compliance References

For a detailed walkthrough of how these violations map to specific clauses within Indonesian Law No. 27 of 2022 (UU PDP), as well as precise indicator charts for scanner development, refer to:
👉 **[violations_report.md](file:///Users/agrottoh6655/.gemini/antigravity/scratch/indonesia-ota-pdp-violation/violations_report.md)**
