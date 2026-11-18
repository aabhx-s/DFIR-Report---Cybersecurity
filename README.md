# Digital Forensics – Project Titan: Corporate Espionage & Firmware Exfiltration Case Study

## Project Overview

This repository contains an end-to-end digital forensics and incident response (DFIR) case study investigating an insider threat and proprietary technology theft incident at a fictional autonomous robotics defense firm (*AeroDyn Robotics*).

The objective was to examine a forensic disk image associated with lead firmware engineer **David Vance**, recover deleted and staged artifacts, trace communication channels and browsing activity, verify evidence integrity using cryptographic hashes, reconstruct a chronological timeline, and compile a comprehensive forensic investigation report.

---

## Case Information

| Field | Details |
| :--- | :--- |
| **Case ID** | `DF-2026-TITAN` |
| **Case Type** | Insider Threat / Corporate Espionage (Simulated) |
| **Subject / Suspect** | David Vance (Lead Firmware Engineer) |
| **Evidence ID** | `E002` |
| **Evidence Media** | 16 MB FAT16 Raw Disk Image (`E002-vance-usb.dd`) |
| **Data Source (Working Copy)** | `E002-vance-working.dd` |
| **Lead Examiner** | Aabhas (`aabhx-s`) |
| **Examination Date** | November 18, 2026 |

---

## Case Study Background

On November 15, 2026, internal Data Loss Prevention (DLP) telemetry at AeroDyn Robotics detected unauthorized mass file staging on workstation `ENG-WS-09`, assigned to lead firmware engineer David Vance. Vance had recently tendered his resignation to join competitor *Skyline Dynamics*. 

Corporate security detained Vance at the main exit turnstiles at 21:00 CST. A personal 16MB SanDisk USB thumb drive was seized from his possession under corporate security protocol. Vance claimed:
> *"I only used the USB drive to take home my personal study notes and resume."*

A full digital forensics investigation was initiated to verify or refute this claim.

---

## Tools Used

- **Autopsy 4.23.1** – Filesystem analysis, FAT16 directory table parsing, deleted file recovery, PhotoRec file carving, EXIF metadata extraction, timeline analysis, and reporting.
- **FTK Imager** – Forensic workstation preparation, image mounting, and partition structure verification.
- **DB Browser for SQLite** – Manual inspection and querying of the Chromium browser history database (`HISTORY.DB`).
- **Windows PowerShell 5.1** – SHA-256 cryptographic hash verification, carved-vs-deleted file comparison, and WebKit/Chromium 64-bit microsecond timestamp conversion.

---

## Investigation Process

### 1. Evidence Preservation and Verification
In accordance with **ISO/IEC 27037** standards, the primary evidence image (`E002-vance-usb.dd`) was write-blocked, and an exact forensic clone (`E002-vance-working.dd`) was created. 

Independent SHA-256 hashes were calculated via PowerShell:
- **Source Evidence SHA-256:** `933E7EA05A87ECFD66313EC7AFE670A4B360932F7FE2BF1C0AD2C79CAC8A17BC`
- **Working Copy SHA-256:** `933E7EA05A87ECFD66313EC7AFE670A4B360932F7FE2BF1C0AD2C79CAC8A17BC`
- **Integrity Status:** **MATCH (`True`)**

All analysis was performed strictly on the working copy to preserve the primary evidence in pristine condition.

### 2. Filesystem Examination
The working copy was ingested into Autopsy 4.23.1. Examination of the filesystem identified several key artifacts:
- **`NOTES.TXT`**: Routine engineering sprint tasks (sprint 42, Kalman filter calibration).
- **`SIGNAL.TXT`**: Exported chat log showing Vance agreeing to supply proprietary Titan obstacle-avoidance firmware to a competitor recruiter in exchange for a **\$25,000 upfront sign-on bonus**.
- **`RECEIPT.TXT`**: A confirmed e-ticket on Swiss flight LX-0019 departing Chicago O'Hare for Zurich at 22:30 CST on Nov 15 (one-way, seat 14A).
- **`SERVER.JPG`**: Photograph of restricted blade server chassis in R&D Lab 04.

### 3. Browser History Analysis
Inspection of `HISTORY.DB` using Autopsy's SQLite Application viewer identified four URL records. Stored Chromium timestamps (microseconds since January 1, 1601 UTC) were converted to local time via PowerShell:
- **19:05 CST** — Search for competitor headquarters: *Skyline Dynamics - Autonomous Systems HQ (Zurich)*
- **19:10 CST** — Web access: *Proton Drive - Secure Encrypted Storage*
- **20:05 CST** — Web search: *SanDisk USB Clean Eraser & Slack Wiper*
- **20:15 CST** — Flight status check: *Flight LX-0019 Departure Status - Chicago O'Hare*

### 4. Deleted File Recovery & Unallocated File Carving
Autopsy detected a deleted file in the root directory table: **`_FIL_KEY.TXT`** (original name: `EXFIL_KEY.TXT`, modified at 20:18 CST).
The recovered text revealed:
> *"TITAN_V4_FIRMWARE_ARCHIVE: Encrypted container key: Kx9#Titan99!Alpha. Destination: Vortex drop portal. Handover: If upload fails, physical thumb drive left in Locker 42B at Terminal 2."*

To satisfy rigorous digital evidence verification standards, Autopsy's PhotoRec carver independently recovered the same file from unallocated space as **`$CarvedFiles/1/f0000000.txt`**.

Both files were exported and hashed in Windows PowerShell:
- **Deleted File (`_FIL_KEY.TXT`):** 185 bytes — `SHA-256: D0B037817D141F7F47768BD9A20B4EB74D6B0D87B910502AC4F13A5A364E5E43`
- **Carved File (`f0000000.txt`):** 185 bytes — `SHA-256: D0B037817D141F7F47768BD9A20B4EB74D6B0D87B910502AC4F13A5A364E5E43`
- **Comparison Result:** **MATCH (`True`)**

### 5. Photograph & EXIF Metadata Examination
`SERVER.JPG` depicts internal blade server chassis in R&D Lab 04. Autopsy's Picture Analyzer reported:
- **Device Make:** `Forensic Camera`
- **Device Model:** `Training Model`
- **Original Timestamp:** `2026:11:15 19:42:00`
This proves Vance was physically present inside the restricted server room where firmware repositories are maintained.

---

## Reconstructed Chronological Timeline

| Timestamp (CST) | Source Artifact | Recorded Event Description |
| :--- | :--- | :--- |
| **Nov 14, 20:15:00** | `NOTES.TXT` | Vance writes sprint tasks; mentions clean handover before leave. |
| **Nov 15, 18:22:10** | `SIGNAL.TXT` | Recruiter confirms \$25k sign-on bonus for Titan firmware repo. |
| **Nov 15, 18:25:34** | `SIGNAL.TXT` | Vance agrees to stage obstacle-avoidance firmware tonight. |
| **Nov 15, 18:28:12** | `SIGNAL.TXT` | Recruiter orders drive wiping and Terminal 2 airport dead-drop. |
| **Nov 15, 18:30:00** | `SIGNAL.TXT` | Vance confirms repository copy; cites 22:30 flight to Zurich. |
| **Nov 15, 19:05:00** | `HISTORY.DB` | Web search for competitor Skyline Dynamics headquarters in Zurich. |
| **Nov 15, 19:10:00** | `HISTORY.DB` | Web access to Proton Drive secure encrypted upload portal. |
| **Nov 15, 19:42:00** | `SERVER.JPG` | Photo taken inside restricted R&D Lab 04 server room (EXIF). |
| **Nov 15, 20:05:00** | `HISTORY.DB` | Web search for USB slack space wiping utility. |
| **Nov 15, 20:15:00** | `HISTORY.DB` | Web search for Flight LX-0019 departure status at O'Hare. |
| **Nov 15, 20:18:00** | `_FIL_KEY.TXT` | **Deleted draft created & deleted** (Container key: `Kx9#Titan99!Alpha`). |
| **Nov 15, 20:45:00** | `RECEIPT.TXT` | One-way e-ticket issued for Swiss Flight LX-0019 to Zurich. |
| **Nov 15, 21:00:00** | Security Log | Suspect detained at facility turnstiles; USB drive seized. |
| **Nov 15, 22:30:00** | Flight Log | Scheduled flight departure (unattended; suspect in custody). |

---

## Key Findings

1. **Active Collusion:** Vance agreed to deliver proprietary autonomous firmware algorithms to an external competitor recruiter for a \$25,000 payout.
2. **Physical Access:** EXIF metadata confirms Vance entered the restricted R&D Lab 04 server room at 19:42 CST.
3. **Flight Plan:** Browser history and recovered receipts confirm booking of an international one-way flight to Zurich departing at 22:30 CST.
4. **Smoking Gun Recovered:** Dual-method recovery (directory parsing and unallocated file carving) extracted the exfiltration note containing the master decryption passphrase (`Kx9#Titan99!Alpha`) and the airport locker contingency plan.
5. **Bit-Level Equivalence:** The carved copy and deleted directory entry produced matching 185-byte file sizes and identical SHA-256 digests (`D0B03781...`).

---

## Repository Structure

```
├── reports/
│   └── DF-2026-TITAN-Final-Forensic-Report.md    # Complete 4-page formal DFIR report
├── screenshots/                                  # 9 verified examination screenshots
│   ├── 01-signal-metadata.png                    # Signal chat metadata
│   ├── 02-receipt-metadata.png                   # Flight ticket metadata
│   ├── 03-server-photo-metadata.png              # Server room EXIF metadata
│   ├── 04-browser-history-sqlite.jpg             # SQLite browser queries
│   ├── 05-deleted-draft-metadata.png             # Deleted _FIL_KEY.TXT view
│   ├── 06-carved-file-metadata.png               # Carved f0000000.txt view
│   ├── 07-recovered-hash-comparison.jpg          # PowerShell hash match (True)
│   ├── 08-autopsy-timeline-list.png              # Autopsy chronological timeline
│   └── 09-primary-evidence-verification.png     # Pre-analysis SHA-256 match
├── documentation/
│   ├── E002-investigation-notes.txt              # Detailed forensic findings
│   ├── E002-verification.txt                     # SHA-256 integrity record
│   └── investigation-log.txt                     # Chronological examiner log
├── evidence/
│   ├── E002-vance-usb.dd                         # Primary evidence raw image
│   ├── E002-vance-working.dd                     # Working copy for Autopsy
│   └── exported/                                 # Carved & deleted file exports
├── scripts/
│   ├── build_titan_evidence.py                   # Disk generator script
│   ├── verify_hashes.ps1                         # PowerShell hash verifier
│   ├── verify_carved_match.ps1                   # PowerShell carved match verifier
│   └── convert_timestamps.ps1                    # Chromium microsecond converter
└── DF-2026-TITAN/                                # Autopsy 4.23.1 case database
```

---

## Skills Demonstrated

- Digital evidence preservation and ISO/IEC 27037 compliance
- SHA-256 bit-stream integrity verification
- FAT16 directory table parsing (`0xE5` deletion markers)
- Unallocated space file carving using PhotoRec
- SQLite database examination and schema analysis
- Chromium 64-bit microsecond timestamp conversion
- Image EXIF metadata parsing
- Chronological forensic timeline reconstruction
- Forensic report writing and case study documentation

---

## Disclaimer
This project is a simulated digital forensics training exercise. All individuals, organizations, and events depicted are synthetic and designed for educational and cybersecurity research purposes.
