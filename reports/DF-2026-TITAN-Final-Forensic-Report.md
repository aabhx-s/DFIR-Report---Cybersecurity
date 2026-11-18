DIGITAL FORENSICS / INCIDENT RESPONSE CASE
# Project Titan: Corporate Espionage & Firmware Exfiltration
## Final Forensic Report

| Case Metadata | Record Details |
| :--- | :--- |
| **Case number** | `DF-2026-TITAN` |
| **Subject / evidence** | David Vance / E002 |
| **Examiner** | Lead Digital Forensics & Incident Response Specialist |
| **Examination date** | November 18, 2026 |
| **Data source** | `E002-vance-working.dd` |
| **Case classification** | Insider Threat / Corporate Espionage; synthetic evidence |

---

## 1. Examination overview

I examined a forensic disk image associated with an insider threat and proprietary technology exfiltration investigation involving David Vance, a lead firmware engineer at AeroDyn Robotics. The objective of the examination was to establish whether proprietary autonomous drone navigation source code was staged or exfiltrated, recover potentially relevant deleted files, analyze web browser and communication artifacts, and construct a chronological timeline of events leading up to the suspect's interception at the facility perimeter on November 15, 2026.

The examination identified communications between Vance and an external recruiter negotiating a \$25,000 payment for the proprietary Titan v4 navigation repository, confirmed an international one-way flight booking to Zurich, and recovered a critical deleted draft containing the encryption passphrase for the stolen firmware container along with instructions for an airport dead-drop. These findings corroborate the incident hypothesis of unauthorized trade secret theft.

---

## 2. Evidence handling and tools

I worked strictly from the forensic working copy (`E002-vance-working.dd`) rather than the original evidence image. SHA-256 verification was documented during evidence preparation and confirmed identical (`933E7EA05A87ECFD66313EC7AFE670A4B360932F7FE2BF1C0AD2C79CAC8A17BC`). 

I used **Autopsy 4.23.1** for filesystem examination, deleted file recovery, file carving, metadata review, and timeline analysis; **FTK Imager** for evidence preservation and acquisition review; **DB Browser for SQLite** to inspect `HISTORY.DB`; and **Windows PowerShell** to compare cryptographic hashes and convert browser timestamps.

The case timezone was **America/Chicago (Central Standard Time, CST)**, unless otherwise specified.

---

## 3. Investigative findings

### Planning and communications
`NOTES.TXT` reflects routine sprint tasks, including Kalman filter calibration and a handover note ("Prepare clean code handover before personal leave"). In contrast, `SIGNAL.TXT` contains an exported chat log from November 15 between Vance and an entity identified as `Vortex_Recruiter`. In this exchange, the recruiter confirms approval of a "\$25k upfront sign-on bonus", and Vance replies at 18:25 that he will have the "core Titan obstacle-avoidance firmware repo ready tonight". At 18:28, the recruiter instructs Vance to purge logs, wipe the drive, and stage the upload or leave it in Terminal 2. Vance confirms at 18:30 that he is copying the repository and taking the 22:30 flight to Zurich. *(Documented in Screenshot: 01-signal-metadata.png)*

### Browser history and transportation
`HISTORY.DB` is a Chromium SQLite database containing browsing records from November 15, 2026. Examined directly via Autopsy's SQLite Application viewer, the database revealed four distinct URL records. Microsecond timestamps (microseconds since January 1, 1601 UTC) were converted to CST using PowerShell. At 19:05, a search for competitor headquarters ("Skyline Dynamics - Autonomous Systems HQ") was recorded. At 19:10, Vance accessed Proton Drive ("Secure Encrypted Storage"). At 20:05, Vance visited an anti-forensics tool page ("SanDisk USB Clean Eraser & Slack Wiper"). At 20:15, he checked the departure status of flight LX-0019. *(Documented in Screenshot: 04-browser-history-sqlite.jpg)*

`RECEIPT.TXT` corroborates this flight query: an airline confirmation for David Vance on Swiss International Air Lines flight LX-0019 (Chicago O'Hare to Zurich), one-way in seat 14A, departing at 22:30 CST on November 15. *(Documented in Screenshot: 02-receipt-metadata.png)*

### Deleted exfiltration handover draft
Autopsy identified a deleted text file named `_FIL_KEY.TXT` (original filename `EXFIL_KEY.TXT`). Its contents revealed:
> *"TITAN_V4_FIRMWARE_ARCHIVE: Encrypted container key: Kx9#Titan99!Alpha. Destination: Vortex drop portal. Handover: If upload fails, physical thumb drive left in Locker 42B at Terminal 2."*

This file represents the central technical finding: it links Vance directly to the exfiltration archive, provides the decryption passphrase, and discloses a physical contingency drop-point at the airport. Filesystem timestamps show creation and modification on November 15 at 20:18 CST, shortly before deletion. *(Documented in Screenshot: 05-deleted-draft-metadata.png)*

### File carving and verification
A second copy of the deleted handover note was recovered independently through unallocated space file carving under `$CarvedFiles/1/f0000000.txt` using Autopsy's PhotoRec carver. Both the directory-recovered file and the carved copy were exported and hashed using SHA-256 in PowerShell:

| Exported File | Size | SHA-256 Comparison |
| :--- | :--- | :---: |
| `_FIL_KEY.TXT` | 185 bytes | **Match** |
| `f0000000.txt` | 185 bytes | **Match** |

**Shared SHA-256 digest:**  
`D0B037817D141F7F47768BD9A20B4EB74D6B0D87B910502AC4F13A5A364E5E43`

The matching hash verifies that both recovered copies contain byte-for-byte identical contents. *(Documented in Screenshots: 06-carved-file-metadata.png and 07-recovered-hash-comparison.jpg)*

### Restricted server room photograph
`SERVER.JPG` depicts internal blade server racks with a banner reading "AERODYN BLADE CHASSIS - RACK 04 / CONFIDENTIAL - R&D LAB 04". Autopsy's Picture Analyzer reported the device make as `Forensic Camera` and model as `Training Model`. The EXIF `DateTimeOriginal` timestamp is recorded as `2026:11:15 19:42:00 CST`. This corroborates physical access badge records indicating Vance entered the restricted server room where firmware repositories are maintained. *(Documented in Screenshot: 03-server-photo-metadata.png)*

---

## 4. Reconstructed timeline

The timeline below integrates message contents, browser history records, airline receipt information, and filesystem timestamps:

| Date / time (CST) | Source | Recorded event |
| :--- | :--- | :--- |
| **Nov 14, 20:15** | `NOTES.TXT` | Engineering Sprint 42 notes written; notes clean handover. |
| **Nov 15, 18:22** | `SIGNAL.TXT` | Recruiter offers \$25,000 sign-on bonus for Titan firmware repo. |
| **Nov 15, 18:25** | `SIGNAL.TXT` | Vance agrees to provide core obstacle-avoidance firmware tonight. |
| **Nov 15, 18:28** | `SIGNAL.TXT` | Recruiter instructs suspect to wipe drive and use Terminal 2 drop. |
| **Nov 15, 18:30** | `SIGNAL.TXT` | Vance confirms repository copy and scheduled 22:30 flight. |
| **Nov 15, 19:05** | `HISTORY.DB` | Web search for competitor Skyline Dynamics headquarters in Zurich. |
| **Nov 15, 19:10** | `HISTORY.DB` | Web access to Proton Drive secure file upload portal. |
| **Nov 15, 19:42** | `SERVER.JPG` | Photo taken inside restricted R&D Lab 04 server room (EXIF). |
| **Nov 15, 20:05** | `HISTORY.DB` | Web search for USB slack space wiping utility. |
| **Nov 15, 20:15** | `HISTORY.DB` | Web search for Flight LX-0019 departure status at O'Hare. |
| **Nov 15, 20:18** | `_FIL_KEY.TXT` | **Deleted draft created & deleted** (Container key: `Kx9#Titan99!Alpha`). |
| **Nov 15, 20:45** | `RECEIPT.TXT` | One-way airline boarding pass issued for Flight LX-0019 to Zurich. |
| **Nov 15, 21:00** | Security Log | Suspect intercepted at facility exit turnstiles; USB drive seized. |
| **Nov 15, 22:30 (planned)** | `RECEIPT.TXT` | Scheduled flight departure (unattended; suspect in custody). |

---

## 5. Conclusion

The digital evidence strongly supports the conclusion that David Vance engaged in unauthorized staging and attempted exfiltration of AeroDyn Robotics' proprietary Titan v4 firmware. The communications, web searches, flight reservations, and server room photography establish a coherent sequence of commercial espionage, preparation for flight, and anti-forensic concealment. 

The recovery of `_FIL_KEY.TXT` through both filesystem analysis and PhotoRec carving—substantiated by identical SHA-256 digests—provides decisive proof of intent to deliver proprietary algorithms to a commercial competitor.

---

## 6. Limitations

This examination was conducted on synthetic media generated for forensic simulation and training. Browser history establishes recorded queries but does not biologically identify the user at the keyboard. FAT access dates have day-level precision rather than second-level precision. While the encryption key was recovered, the final upload status to Proton Drive cannot be determined without server-side cloud logs.

---

## 7. Recommended follow-up

1. Execute a full forensic acquisition of workstation `ENG-WS-09` to locate the source container encrypted with key `Kx9#Titan99!Alpha`.
2. Issue a preservation order and subpoena to Proton AG regarding uploads associated with the suspect's accounts.
3. Coordinate with Chicago O'Hare Airport security to inspect Locker 42B in Terminal 2 for physical media.
4. Notify legal counsel to initiate emergency injunctive relief against Skyline Dynamics.

---

## 8. Supporting documentation & Evidence Screenshots

The case documentation includes the investigation notes and log, evidence hash verification records, exported recovered files, and the following verified examination screenshots:
* **`01-signal-metadata.png`** – Autopsy metadata analysis for `SIGNAL.TXT` establishing communication timestamps.
* **`02-receipt-metadata.png`** – Autopsy metadata analysis for `RECEIPT.TXT` confirming airline reservation.
* **`03-server-photo-metadata.png`** – Autopsy metadata and EXIF analysis for `SERVER.JPG`.
* **`04-browser-history-sqlite.jpg`** – Autopsy SQLite Application viewer showing `HISTORY.DB` URLs and timestamps.
* **`05-deleted-draft-metadata.png`** – Autopsy Deleted Files tree identifying `_FIL_KEY.TXT` with red $X$ and SHA-256.
* **`06-carved-file-metadata.png`** – Autopsy `$CarvedFiles/1/f0000000.txt` metadata and unallocated carving proof.
* **`07-recovered-hash-comparison.jpg`** – Windows PowerShell independent SHA-256 hash comparison returning `True` (Match).

**Examination status:** Complete. Final Report Submitted.
