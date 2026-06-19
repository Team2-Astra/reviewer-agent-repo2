# UU PDP Compliance Violations Analysis Report
**Target System:** Insecure Over-The-Air (OTA) Update System
**Applicable Regulation:** Indonesian Law No. 27 of 2022 on Personal Data Protection (*Undang-Undang Pelindungan Data Pribadi* / UU PDP)

This report provides a systematic breakdown of the personal data protection violations deliberately implemented in this OTA proof-of-concept project. It is structured to serve as an engineering reference and signature checklist for the development of compliance scanners, privacy audit tools, and static/dynamic codebase analyzers.

---

## Executive Summary of Violations

This OTA implementation demonstrates three core vectors of non-compliance under the Indonesian UU PDP:
1. **Lack of Legal Basis (No Consent)**: Harvesting and processing sensitive user/device data without explicit or active consent (*Persetujuan*).
2. **Failure to Secure Personal Data (Insecure Transport & Execution)**: Sending private data over unencrypted channels (HTTP) and executing remote, unsigned code silently, creating severe risks of data leakage and terminal hijack.
3. **No Retention or Deletion Framework**: Storing collected personal data indefinitely in plain text without encryption, scheduling, or mechanisms for data erasure (*Penghapusan/Pemusnahan*).

---

## Detailed Violation Mapping

### 1. Processing Personal Data Without Explicit Consent (Pasal 20 & 22)

*   **Relevant Regulation (UU PDP):**
    *   **Pasal 20:** *Pengendali Data Pribadi wajib memiliki dasar hukum pemrosesan Data Pribadi... salah satunya berupa persetujuan yang sah secara eksplisit dari Subjek Data Pribadi.* (Data Controller must have a lawful basis for processing, primarily explicit consent from the data subject).
    *   **Pasal 22:** Consent must be clearly given and recordable.
*   **How the Code Violates This:**
    *   In [client/client.py](file:///Users/agrottoh6655/.gemini/antigravity/scratch/indonesia-ota-pdp-violation/client/client.py) inside `harvest_private_data()`, the client automatically retrieves the system username, hostname, MAC address, simulated GPS location, and a list of installed apps at startup.
    *   This data is compiled and transmitted immediately without displaying a consent prompt, terms of service dialog, or checking a local settings file indicating the user has opted-in.
*   **Scanner Detection Signatures & Heuristics:**
    *   **API Harvesting Static Checks:** Detect access to system APIs that extract user identifiers (`getpass.getuser()`, `os.getlogin()`), hardware IDs (`uuid.getnode()` for MAC, `socket.gethostname()`), or geolocation APIs without accompanying consent checks.
    *   **Data Minimization Flaw:** Tracking the compilation of nested dictionaries containing multiple mixed telemetry fields (e.g., geolocation + software inventory + hardware ID) that are not directly necessary for the functional task of "checking for software updates". A compliant update check-in should only require an anonymized device fingerprint and the current software version.

---

### 2. Lack of Technical Security and System Integrity (Pasal 35 & 39)

*   **Relevant Regulation (UU PDP):**
    *   **Pasal 35:** *Pengendali Data Pribadi wajib menyusun dan menerapkan langkah teknis operasional untuk mengamankan Data Pribadi... dengan memperhatikan sifat dan risiko.* (Obligation to implement technical operational measures to protect Personal Data based on risk).
    *   **Pasal 39:** *Pengendali Data Pribadi wajib mencegah Data Pribadi diakses secara tidak sah dengan menggunakan sistem keamanan yang andal, aman, dan bertanggung jawab.* (Obligation to prevent unauthorized access using a secure, reliable, and responsible system).
*   **How the Code Violates This (Double Vector):**
    *   **Data-in-Transit Leakage:** In [client/client.py](file:///Users/agrottoh6655/.gemini/antigravity/scratch/indonesia-ota-pdp-violation/client/client.py) inside `check_for_updates()`, the client makes an unencrypted HTTP POST request to `http://localhost:8080/check-update`. Any attacker on the local network (Wi-Fi, ISP, transit router) can intercept this packet (Man-in-the-Middle) and inspect the user's GPS coordinates, usernames, MAC addresses, and active applications in plain text.
    *   **Insecure Execution & Remote Code Execution (RCE) Vulnerability:** In `download_and_install_update()`, the client downloads Python script files over HTTP and immediately executes them in a subprocess via `subprocess.run([sys.executable, ...])` without:
        1. Validating a cryptographic checksum (e.g., SHA-256) of the package.
        2. Verifying a digital signature (RSA/ECDSA) signed by the developer's private key.
    *   This opens a catastrophic flaw where a MITM attacker can hijack the connection, substitute the server's response with a malicious Python script, and execute arbitrary code on the client's device with full user permissions.
*   **Scanner Detection Signatures & Heuristics:**
    *   **Transport Layer Scanner:** Search code for non-HTTPS URL schemes (`http://`) utilized in payload or update endpoints.
    *   **Dynamic Traffic Inspection:** Flag HTTP POST bodies or headers containing keywords like `gps_location`, `latitude`, `mac_address`, `username` or other PII sent in unencrypted JSON.
    *   **Unsafe Execution Sink:** Look for code execution APIs (`subprocess.run`, `subprocess.Popen`, `os.system`, `exec()`, `eval()`) operating on files retrieved via web-requests (`urllib.request.urlopen`, `requests.get`) where there are no matching validation steps utilizing verification methods (e.g. `hashlib.sha256()` checks or cryptographic signatures from `cryptography` libraries).

---

### 3. Infinite Retention and Plaintext Logging (Pasal 43, 44 & 45)

*   **Relevant Regulation (UU PDP):**
    *   **Pasal 43:** *Pengendali Data Pribadi wajib menghapus Data Pribadi dalam hal... Data Pribadi tidak lagi diperlukan untuk pencapaian tujuan pemrosesan.* (Obligation to erase Personal Data when it is no longer required for the purpose).
    *   **Pasal 44:** *Pengendali Data Pribadi wajib memusnahkan Data Pribadi setelah habis masa retensi.* (Obligation to destroy Personal Data after the retention period expires).
*   **How the Code Violates This:**
    *   In [server/server.py](file:///Users/agrottoh6655/.gemini/antigravity/scratch/indonesia-ota-pdp-violation/server/server.py) inside `save_harvested_data()`, the server appends every client's IP and harvested details to `harvested_user_data.csv` in raw plaintext.
    *   There is no scheduler to prune/delete these logs after a specific timeframe (e.g. 30 days).
    *   There is no mechanism, database flag, or endpoint to allow users to invoke their right to erasure (*Hak Penghapusan* under Pasal 43) or withdraw consent (*Penarikan Persetujuan* under Pasal 40).
*   **Scanner Detection Signatures & Heuristics:**
    *   **Log Storage Sinks:** Scan server-side scripts for data write operations (`open(..., 'a')`, SQL database INSERT statements) that persist PII fields to flat files or local SQL databases without checking for encryption operations or associated retention counters/clean-up routines.

---

## Scanner Target Reference Sheet

When building your compliance scanner demo, you can feed these target definitions into your detection rules:

| ID | Violation Title | UU PDP Reference / Type | Target Code Snippet / AST Pattern | Severity |
| :--- | :--- | :--- | :--- | :--- |
| **PDP-001** | Unauthorized Telemetry | Pasal 20, 22 | Harvesting device variables (`socket.gethostname()`, `getpass.getuser()`, `uuid.getnode()`) outside of an explicitly declared configuration or consent state. | **MEDIUM** |
| **PDP-002** | Insecure Transport (HTTP) | Pasal 35, 39 | Network requests targeting endpoints starting with `"http://"` containing string keys like `"gps"`, `"mac"`, `"user"`. | **HIGH** |
| **PDP-003** | Insecure Remote Execution | Pasal 35, 39 | `subprocess.run` or `exec()` targeting downloaded web assets without cryptographic signature verification. | **CRITICAL** |
| **PDP-004** | Plaintext PII Storage | Pasal 43, 44 | Server-side saving of raw system fields and location data to local disk (`.csv` / `.log`) without hashing/encryption or TTL mechanism. | **HIGH** |
| **SCA-001** | Deprecated / Vulnerable Packages | Dependency Vulnerability (SCA) | `package.json` dependencies targeting `"request"` (deprecated) or vulnerable versions like `"lodash": "4.17.15"`, `"minimist": "1.2.0"`, `"express": "4.16.0"`. | **HIGH** |

---

### Suggested Scanner Test Run Scenario

1.  **Phase 1 (Network Scanning):** Run your scanner as a local gateway or proxy. Launch `server.py` and `client.py`. Your scanner should intercept the port `8080` check-in request and raise **PDP-002** due to plain text telemetry transmission of GPS and MAC addresses.
2.  **Phase 2 (Static Code Analysis):** Point your static scanner at `client.py`. It should look for execution sinks (`subprocess.run([sys.executable, DOWNLOADED_PAYLOAD_PATH])`) and trace the source of that file to an insecure network request (`urllib.request.urlopen`), triggering **PDP-003** (RCE via unsigned update download).
3.  **Phase 3 (Data Inventory Scan):** Point your scanner at the server directory. It should find `harvested_user_data.csv` containing plaintext user names, locations, and IPs, triggering **PDP-004** (plaintext unencrypted PII store).
4.  **Phase 4 (Software Composition Analysis - SCA):** Point your dependency scanner at [package.json](file:///Users/agrottoh6655/.gemini/antigravity/scratch/indonesia-ota-pdp-violation/package.json). It should flag:
    *   **Deprecation Warning:** Package `request` is deprecated.
    *   **Vulnerability Detections (CVEs):** Critical vulnerabilities in `lodash` (Prototype Pollution - CVE-2020-8203), `minimist` (Prototype Pollution - CVE-2020-7598), and outdated `express` (SCA-001).

