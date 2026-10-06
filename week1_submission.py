"""Week 1: Combine monthly MLS files and keep Residential records.

Run: python3 week1_aggregation.py
The output folder also contains a submission copy of this script with actual
row counts recorded as comments. Original monthly CSV files are read only.
"""

from pathlib import Path
from datetime import date
import re
import pandas as pd


DATA_DIR = Path('/Users/yuki/csv')
OUTPUT_DIR = DATA_DIR / 'week1_output'
START_MONTH = '202401'


def required_months():
    """January 2024 through the most recently completed calendar month."""
    today = date.today()
    year, month = 2024, 1
    months = []
    while (year, month) < (today.year, today.month):
        months.append(f'{year:04d}{month:02d}')
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return months


def combine(kind, months, notes):
    # Count each monthly file before concatenation; compare its sum to the
    # combined row count. Filtering happens only after concatenation.
    pattern = re.compile(rf'CRMLS{kind}(\d{{6}})(_filled)?\.csv')
    files = {}
    for path in sorted(DATA_DIR.iterdir()):
        match = pattern.fullmatch(path.name)
        if not path.is_file() or not match or match.group(1) not in months:
            continue
        month = match.group(1)
        if month in files:
            raise ValueError(f'Two {kind} files for {month}: '
                             f'{files[month].name}, {path.name}. '
                             'Choose one version to avoid double counting.')
        files[month] = path

    if not files:
        raise FileNotFoundError(f'No monthly {kind} CSV files in {DATA_DIR}')

    missing = [month for month in months if month not in files]
    notes.append(f'{kind}: available months {min(files)} through {max(files)}')
    notes.append(f'{kind}: missing required months: {", ".join(missing) or "None"}')
    if missing:
        print(f'WARNING: {kind} is missing months: {", ".join(missing)}')

    frames = []
    for month, path in sorted(files.items()):
        # Read as strings to preserve identifiers and original CSV values.
        frame = pd.read_csv(path, dtype=str, keep_default_na=False,
                            encoding='utf-8-sig')
        if 'PropertyType' not in frame.columns:
            raise ValueError(f'{path.name} has no PropertyType column')
        notes.append(f'Before concatenation: {path.name} = {len(frame):,} rows')
        frames.append(frame)

    before_concat = sum(len(frame) for frame in frames)
    combined = pd.concat(frames, ignore_index=True, sort=False)
    notes.append(f'{kind}: total rows before concatenation = {before_concat:,}')
    notes.append(f'{kind}: rows after concatenation = {len(combined):,}')
    if len(combined) != before_concat:
        raise ValueError(f'{kind}: concatenation row count mismatch')

    before_filter = len(combined)
    residential = combined.loc[combined['PropertyType'] == 'Residential'].copy()
    notes.append(f'{kind}: rows before Residential filter = {before_filter:,}')
    notes.append(f'{kind}: rows after Residential filter = {len(residential):,}')
    return residential


def main():
    if not DATA_DIR.is_dir():
        raise FileNotFoundError(f'Data folder not found: {DATA_DIR}')
    months = required_months()
    notes = [f'Run date: {date.today().isoformat()}',
             f'Required period: {START_MONTH} through {months[-1]}',
             'Missing months are reported; outputs contain available files only.',
             'No duplicate removal is performed during concatenation.']

    listings = combine('Listing', months, notes)
    sold = combine('Sold', months, notes)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    listings.to_csv(OUTPUT_DIR / 'combined_listings_residential.csv', index=False)
    sold.to_csv(OUTPUT_DIR / 'combined_sold_residential.csv', index=False)

    # Save actual row counts as comments in the .py submission copy.
    source = Path(__file__).read_text(encoding='utf-8')
    source = source.split('

# === ACTUAL ROW COUNTS ===
# Run date: 2026-10-05
# Required period: 202401 through 202609
# Missing months are reported; outputs contain available files only.
# No duplicate removal is performed during concatenation.
# Listing: available months 202401 through 202604
# Listing: missing required months: 202605, 202606, 202607, 202608, 202609
# Before concatenation: CRMLSListing202401.csv = 27,454 rows
# Before concatenation: CRMLSListing202402.csv = 27,447 rows
# Before concatenation: CRMLSListing202403.csv = 32,282 rows
# Before concatenation: CRMLSListing202404.csv = 36,503 rows
# Before concatenation: CRMLSListing202405.csv = 38,796 rows
# Before concatenation: CRMLSListing202406.csv = 35,893 rows
# Before concatenation: CRMLSListing202407.csv = 36,340 rows
# Before concatenation: CRMLSListing202408.csv = 35,305 rows
# Before concatenation: CRMLSListing202409.csv = 34,625 rows
# Before concatenation: CRMLSListing202410.csv = 34,730 rows
# Before concatenation: CRMLSListing202411.csv = 25,128 rows
# Before concatenation: CRMLSListing202412.csv = 19,417 rows
# Before concatenation: CRMLSListing202501.csv = 37,469 rows
# Before concatenation: CRMLSListing202502.csv = 33,983 rows
# Before concatenation: CRMLSListing202503.csv = 38,492 rows
# Before concatenation: CRMLSListing202504.csv = 40,187 rows
# Before concatenation: CRMLSListing202505.csv = 40,271 rows
# Before concatenation: CRMLSListing202506.csv = 26,399 rows
# Before concatenation: CRMLSListing202507.csv = 27,345 rows
# Before concatenation: CRMLSListing202508.csv = 25,210 rows
# Before concatenation: CRMLSListing202509.csv = 26,923 rows
# Before concatenation: CRMLSListing202510.csv = 27,586 rows
# Before concatenation: CRMLSListing202511.csv = 20,677 rows
# Before concatenation: CRMLSListing202512.csv = 18,773 rows
# Before concatenation: CRMLSListing202601.csv = 2,606 rows
# Before concatenation: CRMLSListing202602.csv = 32,884 rows
# Before concatenation: CRMLSListing202603.csv = 39,153 rows
# Before concatenation: CRMLSListing202604.csv = 39,020 rows
# Listing: total rows before concatenation = 860,898
# Listing: rows after concatenation = 860,898
# Listing: rows before Residential filter = 860,898
# Listing: rows after Residential filter = 547,162
# Sold: available months 202401 through 202604
# Sold: missing required months: 202605, 202606, 202607, 202608, 202609
# Before concatenation: CRMLSSold202401_filled.csv = 17,958 rows
# Before concatenation: CRMLSSold202402.csv = 19,925 rows
# Before concatenation: CRMLSSold202403_filled.csv = 23,276 rows
# Before concatenation: CRMLSSold202404_filled.csv = 24,640 rows
# Before concatenation: CRMLSSold202405_filled.csv = 26,487 rows
# Before concatenation: CRMLSSold202406_filled.csv = 24,328 rows
# Before concatenation: CRMLSSold202407_filled.csv = 26,240 rows
# Before concatenation: CRMLSSold202408.csv = 24,558 rows
# Before concatenation: CRMLSSold202409.csv = 21,267 rows
# Before concatenation: CRMLSSold202410.csv = 23,274 rows
# Before concatenation: CRMLSSold202411.csv = 20,279 rows
# Before concatenation: CRMLSSold202412.csv = 20,241 rows
# Before concatenation: CRMLSSold202501_filled.csv = 18,738 rows
# Before concatenation: CRMLSSold202502.csv = 18,702 rows
# Before concatenation: CRMLSSold202503.csv = 21,445 rows
# Before concatenation: CRMLSSold202504.csv = 23,262 rows
# Before concatenation: CRMLSSold202505.csv = 23,154 rows
# Before concatenation: CRMLSSold202506.csv = 22,883 rows
# Before concatenation: CRMLSSold202507.csv = 23,646 rows
# Before concatenation: CRMLSSold202508.csv = 22,972 rows
# Before concatenation: CRMLSSold202509.csv = 22,443 rows
# Before concatenation: CRMLSSold202510.csv = 23,233 rows
# Before concatenation: CRMLSSold202511.csv = 19,088 rows
# Before concatenation: CRMLSSold202512.csv = 20,538 rows
# Before concatenation: CRMLSSold202601.csv = 16,487 rows
# Before concatenation: CRMLSSold202602.csv = 19,010 rows
# Before concatenation: CRMLSSold202603.csv = 23,372 rows
# Before concatenation: CRMLSSold202604.csv = 24,261 rows
# Sold: total rows before concatenation = 615,707
# Sold: rows after concatenation = 615,707
# Sold: rows before Residential filter = 615,707
# Sold: rows after Residential filter = 414,054
