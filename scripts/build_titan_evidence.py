"""
build_titan_evidence.py
Generates the complete synthetic forensic disk image for Case DF-2026-TITAN.
Creates:
 - E002-vance-usb.dd (Primary Evidence)
 - E002-vance-working.dd (Working Copy)
Embeds:
 1. PROJECT_NOTES.TXT (Active File)
 2. SIGNAL_CHAT.TXT (Active File)
 3. FLIGHT_RECEIPT.TXT (Active File)
 4. SERVER_ROOM.JPG (JPEG with EXIF tags: Make, Model, DateTimeOriginal)
 5. HISTORY.DB (Real SQLite database with Chromium microsecond timestamps)
 6. _XFIL.TXT (Deleted File with 0xE5 marker & unallocated cluster data for carving)
"""

import os
import sys
import struct
import datetime
import sqlite3
import hashlib
from PIL import Image, ImageDraw, ImageFont

# --- CONSTANTS & GEOMETRY (16MB FAT16) ---
SECTOR_SIZE = 512
SECTORS_PER_CLUSTER = 4
CLUSTER_SIZE = SECTOR_SIZE * SECTORS_PER_CLUSTER # 2048 bytes
TOTAL_SECTORS = 32768 # 16 MB
RESERVED_SECTORS = 1
NUM_FATS = 2
SECTORS_PER_FAT = 64
ROOT_DIR_ENTRIES = 512
ROOT_DIR_SECTORS = (ROOT_DIR_ENTRIES * 32) // SECTOR_SIZE # 32 sectors

FAT1_START_SECTOR = RESERVED_SECTORS # 1
FAT2_START_SECTOR = FAT1_START_SECTOR + SECTORS_PER_FAT # 65
ROOT_DIR_START_SECTOR = FAT2_START_SECTOR + SECTORS_PER_FAT # 129
DATA_START_SECTOR = ROOT_DIR_START_SECTOR + ROOT_DIR_SECTORS # 161
DISK_SIZE_BYTES = TOTAL_SECTORS * SECTOR_SIZE

def encode_dos_datetime(dt: datetime.datetime):
    year = max(1980, dt.year) - 1980
    dos_date = (year << 9) | (dt.month << 5) | dt.day
    dos_time = (dt.hour << 11) | (dt.minute << 5) | (dt.second // 2)
    return dos_date, dos_time

def format_8_3(name: str):
    parts = name.upper().split(".")
    base = parts[0][:8].ljust(8)
    ext = parts[1][:3].ljust(3) if len(parts) > 1 else "   "
    return (base + ext).encode("ascii")

def create_boot_sector():
    bs = bytearray(SECTOR_SIZE)
    bs[0:3] = b"\xEB\x3C\x90"
    bs[3:11] = b"MSDOS5.0"
    struct.pack_into("<H", bs, 11, SECTOR_SIZE)
    bs[13] = SECTORS_PER_CLUSTER
    struct.pack_into("<H", bs, 14, RESERVED_SECTORS)
    bs[16] = NUM_FATS
    struct.pack_into("<H", bs, 17, ROOT_DIR_ENTRIES)
    struct.pack_into("<H", bs, 19, TOTAL_SECTORS)
    bs[21] = 0xF8 # Media descriptor
    struct.pack_into("<H", bs, 22, SECTORS_PER_FAT)
    struct.pack_into("<H", bs, 24, 32)
    struct.pack_into("<H", bs, 26, 64)
    struct.pack_into("<I", bs, 28, 0)
    struct.pack_into("<I", bs, 32, 0)
    bs[36] = 0x80
    bs[37] = 0x00
    bs[38] = 0x29
    struct.pack_into("<I", bs, 39, 0x20261118)
    bs[43:54] = b"AERODYN_USB"
    bs[54:62] = b"FAT16   "
    bs[510] = 0x55
    bs[511] = 0xAA
    return bs

def create_directory_entry(name_8_3, attr, dt, start_cluster, file_size):
    entry = bytearray(32)
    entry[0:11] = name_8_3
    entry[11] = attr
    dos_date, dos_time = encode_dos_datetime(dt)
    struct.pack_into("<H", entry, 14, dos_time)
    struct.pack_into("<H", entry, 16, dos_date)
    struct.pack_into("<H", entry, 18, dos_date)
    struct.pack_into("<H", entry, 20, 0)
    struct.pack_into("<H", entry, 22, dos_time)
    struct.pack_into("<H", entry, 24, dos_date)
    struct.pack_into("<H", entry, 26, start_cluster)
    struct.pack_into("<I", entry, 28, file_size)
    return entry

def create_server_room_image():
    """Builds a real JPEG with EXIF tags for Autopsy."""
    img = Image.new("RGB", (480, 320), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    
    # Draw simple server rack graphic
    draw.rectangle([60, 40, 420, 280], outline=(70, 130, 180), width=3)
    for y in range(65, 270, 35):
        draw.rectangle([75, y, 405, y + 25], fill=(30, 42, 60), outline=(100, 149, 237))
        draw.ellipse([85, y + 8, 95, y + 18], fill=(0, 255, 0)) # Green LED
        draw.ellipse([102, y + 8, 112, y + 18], fill=(0, 200, 255)) # Blue LED
        draw.text((130, y + 6), f"AERODYN BLADE CHASSIS - RACK {y//35}", fill=(220, 220, 220))
        
    draw.text((80, 285), "CONFIDENTIAL - R&D LAB 04 - RESTRICTED ACCESS", fill=(255, 69, 0))
    
    # Add EXIF tags
    exif = img.getexif()
    exif[0x010F] = "Forensic Camera"     # Make
    exif[0x0110] = "Training Model"      # Model
    exif[0x0131] = "AeroDyn Security V3" # Software
    exif[0x0132] = "2026:11:15 19:42:00" # DateTime
    exif[0x9003] = "2026:11:15 19:42:00" # DateTimeOriginal
    
    temp_path = "temp_server_room.jpg"
    img.save(temp_path, "JPEG", exif=exif)
    with open(temp_path, "rb") as f:
        jpg_bytes = f.read()
    if os.path.exists(temp_path):
        os.remove(temp_path)
    return jpg_bytes

def dt_to_webkit_micros(dt_cst: datetime.datetime):
    """Converts a CST datetime (UTC-6) to Chromium microseconds since 1601-01-01 UTC."""
    dt_utc = dt_cst + datetime.timedelta(hours=6)
    epoch_1601 = datetime.datetime(1601, 1, 1, 0, 0, 0)
    diff = dt_utc - epoch_1601
    return int(diff.total_seconds() * 1_000_000)

def create_sqlite_history_db():
    """Generates a valid Chromium-format SQLite History database."""
    db_file = "temp_history.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE urls(
            id INTEGER PRIMARY KEY,
            url LONGVARCHAR,
            title LONGVARCHAR,
            visit_count INTEGER DEFAULT 0 NOT NULL,
            typed_count INTEGER DEFAULT 0 NOT NULL,
            last_visit_time INTEGER NOT NULL,
            hidden INTEGER DEFAULT 0 NOT NULL
        )
    """)
    
    searches = [
        ("https://search.internal/q=skyline+dynamics+headquarters+zurich", "Skyline Dynamics - Autonomous Systems HQ", datetime.datetime(2026, 11, 15, 19, 5, 0)),
        ("https://proton.me/drive/u/0/shared-folder-upload", "Proton Drive - Secure Encrypted Storage", datetime.datetime(2026, 11, 15, 19, 10, 0)),
        ("https://cyber-tools.net/sandisk-secure-wiper-utility", "SanDisk USB Clean Eraser & Slack Wiper", datetime.datetime(2026, 11, 15, 20, 5, 0)),
        ("https://ohare.airport/flights/departures/LX0019", "Flight LX-0019 Departure Status - Chicago O'Hare", datetime.datetime(2026, 11, 15, 20, 15, 0))
    ]
    
    for idx, (url, title, dt) in enumerate(searches, start=1):
        webkit_ts = dt_to_webkit_micros(dt)
        cur.execute("INSERT INTO urls VALUES (?, ?, ?, 1, 0, ?, 0)", (idx, url, title, webkit_ts))
        
    conn.commit()
    conn.close()
    
    with open(db_file, "rb") as f:
        db_bytes = f.read()
    if os.path.exists(db_file):
        os.remove(db_file)
    return db_bytes

def generate_titan_disk(output_img_path: str):
    print(f"[*] Initializing blank disk of {DISK_SIZE_BYTES / (1024*1024):.1f} MB...")
    disk = bytearray(DISK_SIZE_BYTES)
    
    # 1. Boot sector
    disk[0:SECTOR_SIZE] = create_boot_sector()
    
    # 2. FAT tables
    fat_size_bytes = SECTORS_PER_FAT * SECTOR_SIZE
    fat = bytearray(fat_size_bytes)
    struct.pack_into("<H", fat, 0, 0xFFF8)
    struct.pack_into("<H", fat, 2, 0xFFFF)
    
    # 3. Prepare Artifact Contents
    jpg_data = create_server_room_image()
    db_data = create_sqlite_history_db()
    
    # Exact 182-byte text for the deleted draft smoking gun
    deleted_draft_text = (
        b"TITAN_V4_FIRMWARE_ARCHIVE: Encrypted container key: Kx9#Titan99!Alpha\n"
        b"Destination: Vortex drop portal.\n"
        b"Handover: If upload fails, physical thumb drive left in Locker 42B at Terminal 2.\n"
    )
    
    artifacts = [
        {
            "name": "NOTES.TXT",
            "attr": 0x20,
            "dt": datetime.datetime(2026, 11, 14, 20, 15, 0),
            "data": (
                b"AeroDyn Robotics - Autonomous Navigation Team Sprint 42\n"
                b"Tasks:\n"
                b"1. Review Kalman filter drift calibration on Titan v4.2.\n"
                b"2. Update regression test suite for obstacle avoidance.\n"
                b"3. Prepare clean code handover before personal leave.\n"
            ),
            "deleted": False
        },
        {
            "name": "SIGNAL.TXT",
            "attr": 0x20,
            "dt": datetime.datetime(2026, 11, 15, 18, 30, 0),
            "data": (
                b"[18:22:10] Vortex_Recruiter: David, our executive team approved the package. $25k upfront sign-on bonus.\n"
                b"[18:25:34] Vance: Understood. I will have the core Titan obstacle-avoidance firmware repo ready tonight.\n"
                b"[18:28:12] Vortex_Recruiter: Make sure to purge logs and wipe the drive. Upload to the Proton link or leave in Terminal 2 locker.\n"
                b"[18:30:00] Vance: Copying the repo now. Taking the 22:30 flight to Zurich.\n"
            ),
            "deleted": False
        },
        {
            "name": "RECEIPT.TXT",
            "attr": 0x20,
            "dt": datetime.datetime(2026, 11, 15, 20, 45, 0),
            "data": (
                b"AIRLINE E-TICKET CONFIRMATION\n"
                b"Passenger: David Vance\n"
                b"Flight: LX-0019 (Chicago O'Hare ORD -> Zurich ZRH)\n"
                b"Departure: November 15, 2026 at 22:30 CST\n"
                b"Seat: 14A (Single passenger, one-way)\n"
                b"Booking Status: CONFIRMED - Boarding Pass Issued\n"
                b"Payment: Credit Card ending in 4091\n"
            ),
            "deleted": False
        },
        {
            "name": "SERVER.JPG",
            "attr": 0x20,
            "dt": datetime.datetime(2026, 11, 15, 19, 42, 0),
            "data": jpg_data,
            "deleted": False
        },
        {
            "name": "HISTORY.DB",
            "attr": 0x20,
            "dt": datetime.datetime(2026, 11, 15, 20, 20, 0),
            "data": db_data,
            "deleted": False
        },
        {
            "name": "XFIL_KEY.TXT", # In directory it will become _XFIL_KEY.TXT (0xE5)
            "attr": 0x20,
            "dt": datetime.datetime(2026, 11, 15, 20, 18, 0),
            "data": deleted_draft_text,
            "deleted": True # DELETED SMOKING GUN!
        }
    ]
    
    current_cluster = 2
    root_dir = bytearray(ROOT_DIR_ENTRIES * 32)
    entry_index = 0
    
    for item in artifacts:
        file_bytes = item["data"]
        file_size = len(file_bytes)
        num_clusters = (file_size + CLUSTER_SIZE - 1) // CLUSTER_SIZE
        if num_clusters == 0:
            num_clusters = 1
            
        start_cluster = current_cluster
        
        # Write file data into disk cluster area
        for c_idx in range(num_clusters):
            c_num = start_cluster + c_idx
            sector_offset = DATA_START_SECTOR + (c_num - 2) * SECTORS_PER_CLUSTER
            byte_offset = sector_offset * SECTOR_SIZE
            chunk = file_bytes[c_idx * CLUSTER_SIZE : (c_idx + 1) * CLUSTER_SIZE]
            disk[byte_offset : byte_offset + len(chunk)] = chunk
            
            if not item["deleted"]:
                if c_idx == num_clusters - 1:
                    struct.pack_into("<H", fat, c_num * 2, 0xFFFF)
                else:
                    struct.pack_into("<H", fat, c_num * 2, c_num + 1)
            else:
                # Mark cluster as unallocated in FAT (0x0000), but leave bytes in unallocated space!
                struct.pack_into("<H", fat, c_num * 2, 0x0000)
                
        # 8.3 filename formatting
        name_8_3 = format_8_3(item["name"])
        if item["deleted"]:
            name_8_3 = bytes([0xE5]) + name_8_3[1:] # 0xE5 deletion flag
            
        entry_bytes = create_directory_entry(
            name_8_3=name_8_3,
            attr=item["attr"],
            dt=item["dt"],
            start_cluster=start_cluster,
            file_size=file_size
        )
        root_dir[entry_index * 32 : (entry_index + 1) * 32] = entry_bytes
        entry_index += 1
        current_cluster += num_clusters
        
    # Write FATs and Root Directory
    disk[FAT1_START_SECTOR * SECTOR_SIZE : (FAT1_START_SECTOR + SECTORS_PER_FAT) * SECTOR_SIZE] = fat
    disk[FAT2_START_SECTOR * SECTOR_SIZE : (FAT2_START_SECTOR + SECTORS_PER_FAT) * SECTOR_SIZE] = fat
    disk[ROOT_DIR_START_SECTOR * SECTOR_SIZE : ROOT_DIR_START_SECTOR * SECTOR_SIZE + len(root_dir)] = root_dir
    
    os.makedirs(os.path.dirname(output_img_path), exist_ok=True)
    with open(output_img_path, "wb") as f:
        f.write(disk)
        
    print(f"[+] Forensic disk image generated successfully: {output_img_path}")
    print(f"    - Size: {len(disk):,} bytes ({len(disk)/(1024*1024):.1f} MB)")
    print(f"    - Root directory entries: {entry_index} (including deleted smoking gun)")
    print(f"    - Deleted file size: {len(deleted_draft_text)} bytes")
    print(f"    - Deleted file SHA-256: {hashlib.sha256(deleted_draft_text).hexdigest().upper()}")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    primary_img = os.path.join(base_dir, "evidence", "E002-vance-usb.dd")
    generate_titan_disk(primary_img)
