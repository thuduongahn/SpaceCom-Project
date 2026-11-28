import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TLE_FILE = BASE_DIR / "selected_satellites.tle"
OUTPUT_CSV = BASE_DIR / "satellite_catalog.csv"

SOURCE_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
DOWNLOADED_UTC = "2026-11-28 09:30:00 UTC"

SATNOGS_CANDIDATE_IDS = {25544, 48274, 41914, 44538, 25994, 43798, 43013, 26958}


def compute_checksum(line: str) -> int:
    total = 0
    for ch in line[:68]:
        if ch.isdigit():
            total += int(ch)
        elif ch == "-":
            total += 1
    return total % 10


def parse_epoch(line1: str) -> datetime:
    ep = line1[18:32].strip()
    yy = int(ep[:2])
    year = 2000 + yy if yy < 57 else 1900 + yy
    day_of_year = float(ep[2:])
    return datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_of_year - 1.0)


def classify_orbit(mean_motion_rev_day: float) -> tuple[str, float]:
    mu = 398600.4418
    re = 6378.137
    omega = mean_motion_rev_day * 2.0 * math.pi / 86400.0
    a = (mu / (omega**2)) ** (1.0 / 3.0)
    alt = a - re
    if alt < 450:
        return "VLEO", alt
    elif alt < 2000:
        return "LEO", alt
    elif alt < 35000:
        return "MEO", alt
    return "GEO", alt


with open(TLE_FILE, "r", encoding="utf-8") as f:
    lines = [line.rstrip("\r\n") for line in f if line.strip()]

catalog_rows = []
invalid_records = []

for i in range(0, len(lines), 3):
    name, l1, l2 = lines[i].strip(), lines[i + 1], lines[i + 2]

    prefix_ok = l1.startswith("1 ") and l2.startswith("2 ")
    norad1 = l1[2:7].strip()
    norad2 = l2[2:7].strip()
    norad_match = (norad1 == norad2) and norad1.isdigit()

    cs1_ok = (len(l1) == 69) and l1[68].isdigit() and (compute_checksum(l1) == int(l1[68]))
    cs2_ok = (len(l2) == 69) and l2[68].isdigit() and (compute_checksum(l2) == int(l2[68]))
    is_valid = prefix_ok and norad_match and cs1_ok and cs2_ok

    if not is_valid:
        invalid_records.append((name, norad1, norad2, cs1_ok, cs2_ok))
        print(f"[SKIPPED - INVALID TLE] {name} (NORAD: {norad1}/{norad2})")
        continue

    epoch_dt = parse_epoch(l1)
    inc = float(l2[8:16])
    ecc = float("0." + l2[26:33].strip())
    mean_motion = float(l2[52:63])
    regime, mean_alt = classify_orbit(mean_motion)
    norad_int = int(norad1)

    catalog_rows.append({
        "norad_id": norad_int,
        "name": name,
        "orbit_regime": regime,
        "epoch_utc": epoch_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "norad_match": norad_match,
        "checksum_line1_ok": cs1_ok,
        "checksum_line2_ok": cs2_ok,
        "mean_alt_km": round(mean_alt, 1),
        "inclination_deg": round(inc, 4),
        "eccentricity": round(ecc, 7),
        "mean_motion_rev_day": round(mean_motion, 8),
        "satnogs_candidate": norad_int in SATNOGS_CANDIDATE_IDS,
        "tle_line1": l1,
        "tle_line2": l2,
        "source_url": SOURCE_URL,
        "downloaded_utc": DOWNLOADED_UTC,
    })

if invalid_records:
    print(f"\n[WARNING] Skipped {len(invalid_records)} invalid TLE record(s) from CSV export.")
#Export satellite.csv: 
if catalog_rows:
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=catalog_rows[0].keys())
        writer.writeheader()
        writer.writerows(catalog_rows)

    print(f"Exported {len(catalog_rows)} satellites -> {OUTPUT_CSV}")
    print(f"Columns ({len(catalog_rows[0])}): {list(catalog_rows[0].keys())}")