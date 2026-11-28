# SpaceCom-Project
# Task 1 (Member A) — Current TLE Acquisition & Satellite Catalog

## 1. Objective
Acquire, validate, and classify current Two-Line Element (TLE) orbital data for **20 satellites** evenly distributed across four orbital regimes (**5 VLEO, 5 LEO, 5 MEO, and 5 GEO**). All selected GEO satellites are verified to maintain an elevation angle $> 10^\circ$ from the International University (IU) ground station ($10.88^\circ\text{N}, 106.80^\circ\text{E}$), and suitable VLEO/LEO candidates are flagged for downstream SatNOGS validation.

## 2. Data Sources & Provenance
- **Primary TLE Source:** CelesTrak GP Data API (`https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle` or individual `CATNR` queries).
- **Validation Reference:** SatNOGS DB & Network (`https://db.satnogs.org/` and `https://network.satnogs.org/api/observations/`).
- **Acquisition Timestamp:** `2026-11-28 09:30:00 UTC` *(update if re-downloaded)*.

## 3. Data Acquisition & Processing Pipeline
1. **Raw Data Acquisition:** Download 3-line TLE sets (Name, Line 1, Line 2) directly from CelesTrak and preserve the original raw TLE file unmodified.
2. **TLE Validation & Error Filtering:**
   - Verify standard line prefixes (`1 ` and `2 `) and exact 69-character line lengths.
   - Cross-check NORAD catalog IDs between Line 1 and Line 2.
   - Compute and verify the **Modulo-10 Checksum** for both lines.
   - **Strict Filtering:** Any record failing validation is logged and excluded before exporting to `satellite_catalog.csv`.
3. **Parameter Extraction & Classification:**
   - Extract `epoch_utc` from Line 1.
   - Compute mean altitude from Mean Motion (Line 2) to classify regimes:
     - **VLEO:** $< 450\text{ km}$
     - **LEO:** $450 - 2000\text{ km}$
     - **MEO:** $2000 - 35000\text{ km}$
     - **GEO:** $\ge 35000\text{ km}$
   - Flag `satnogs_candidate` for VLEO/LEO satellites with active SatNOGS observation records.
4. **Export Deliverables:** Generate `selected_satellites.tle` (60 lines) and `satellite_catalog.csv` (including orbital parameters, validation flags, `tle_line1`, `tle_line2`, `source_url`, and `downloaded_utc`).

## 4. Repository Structure
- `Check_Epoch.py` *(or `Member_A_Current_TLE.ipynb`)*: Main script/notebook for TLE validation, classification, and CSV export.
- `selected_satellites.tle`: Validated 3-line TLE dataset for the 20 selected satellites (60 lines total).
- `satellite_catalog.csv`: Structured catalog of the 20 satellites with orbital elements, validation status, `tle_line1`, `tle_line2`, and provenance metadata.
- `data/raw/`: Unmodified raw TLE source file(s) downloaded from CelesTrak.

## 5. How to Run (Reproducibility)
Ensure `selected_satellites.tle` is in the same directory as the script, then run:
```bash
python Check_Epoch.py
