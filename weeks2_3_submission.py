"""Weeks 2-3: MLS structure, Residential validation, and exploratory analysis.

Run this script in Jupyter with %run followed by its full file path.
Inputs: original monthly CSVs. Outputs: weeks2_3_output under DATA_DIR.
Records and columns are retained; potential issues are reported for review.
"""

from pathlib import Path
from datetime import date
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA_DIR = Path('/Users/yuki/csv')
OUTPUT_DIR = DATA_DIR / 'weeks2_3_output'
NUMERIC_FIELDS = [
    'ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea',
    'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger',
    'DaysOnMarket', 'YearBuilt',
]
CORE_FIELDS = set(NUMERIC_FIELDS + [
    'PropertyType', 'CountyOrParish', 'ListingId', 'ListingKey',
    'ListingContractDate', 'OnMarketDate', 'CloseDate',
])
MARKET_FIELDS = CORE_FIELDS | {
    'City', 'PostalCode', 'StandardStatus', 'PropertySubType',
    'Latitude', 'Longitude', 'StateOrProvince', 'OffMarketDate',
}


def load_months(kind):
    pattern = re.compile(rf'CRMLS{kind}(\d{{6}})(_filled)?\.csv')
    files = {}
    current_month = date.today().strftime('%Y%m')
    for path in sorted(DATA_DIR.iterdir()):
        match = pattern.fullmatch(path.name)
        if not path.is_file() or not match:
            continue
        month = match.group(1)
        if not '202401' <= month < current_month:
            continue
        if month in files:
            raise ValueError(f'Duplicate {kind} month {month}: '
                             f'{files[month].name}, {path.name}')
        files[month] = path
    if not files:
        raise FileNotFoundError(f'No monthly {kind} files in {DATA_DIR}')
    frames, inventory = [], []
    for month, path in sorted(files.items()):
        # Preserve identifiers as text. Normalize blank values to true nulls.
        frame = pd.read_csv(path, dtype=str, encoding='utf-8-sig',
                            keep_default_na=False)
        frame = frame.replace(r'^\s*$', pd.NA, regex=True)
        if 'PropertyType' not in frame.columns:
            raise ValueError(f'Missing PropertyType in {path.name}')
        inventory.append({'month': month, 'file': path.name, 'rows': len(frame)})
        frames.append(frame)
    return pd.concat(frames, ignore_index=True, sort=False), pd.DataFrame(inventory)


def numeric_values(series):
    # Remove common price/area formatting; flag other nonnumeric values.
    text = series.astype('string').str.strip().str.replace(r'[$,]', '', regex=True)
    values = pd.to_numeric(text, errors='coerce')
    return values.replace([float('inf'), float('-inf')], float('nan'))


def analyze(kind):
    folder = OUTPUT_DIR / kind.lower()
    folder.mkdir(parents=True, exist_ok=True)
    raw, inventory = load_months(kind)
    inventory.to_csv(folder / 'monthly_file_inventory.csv', index=False)

    # Report original categories before applying the exact requested filter.
    counts = raw['PropertyType'].value_counts(dropna=False)
    types = counts.rename_axis('PropertyType').reset_index(name='rows')
    types['percentage'] = types['rows'] / len(raw) * 100 if len(raw) else 0
    types.to_csv(folder / 'property_type_summary.csv', index=False)
    mask = raw['PropertyType'].eq('Residential').fillna(False)
    residential = raw.loc[mask].copy()
    if residential.empty:
        raise ValueError(f'{kind}: no exact Residential matches; review type summary')
    residential.to_csv(folder / 'filtered_residential.csv', index=False)

    missing = residential.isna().sum()
    report = pd.DataFrame({
        'column': residential.columns,
        'dtype_as_loaded': [str(value) for value in residential.dtypes],
        'missing_count': missing.to_numpy(),
        'missing_percentage': missing.to_numpy() / len(residential) * 100,
    })
    report['above_90_percent_missing'] = report['missing_percentage'] > 90
    report['core_field'] = report['column'].isin(CORE_FIELDS)
    # Field roles are suggestions requiring domain review, not automatic drops.
    report['field_role'] = report['column'].map(
        lambda name: 'market_analysis' if name in MARKET_FIELDS else
        'metadata' if any(token in name.lower() for token in
                          ['key', 'id', 'timestamp', 'modification', 'source',
                           'agent', 'office', 'system']) else 'review_required'
    )
    report['recommended_action'] = report.apply(
        lambda row: 'retain_core_field' if row['core_field'] else
        'consider_drop_after_review' if row['above_90_percent_missing'] else
        'retain_pending_review', axis=1
    )
    report.sort_values('missing_percentage', ascending=False).to_csv(
        folder / 'missing_value_report.csv', index=False)
    report[['column', 'missing_count']].to_csv(folder / 'null_count_summary.csv', index=False)
    report[['column', 'dtype_as_loaded', 'field_role', 'core_field',
            'recommended_action']].to_csv(folder / 'column_structure.csv', index=False)

    summaries, outliers, numbers = [], [], {}
    unavailable = []
    for field in NUMERIC_FIELDS:
        if field not in residential.columns:
            unavailable.append(field)
            summaries.append({'field': field, 'status': 'column_not_available'})
            continue
        values = numeric_values(residential[field])
        numbers[field] = values
        valid = values.dropna().astype(float)
        invalid = residential[field].notna() & values.isna()
        row = {'field': field, 'status': 'available', 'valid_count': len(valid),
               'missing_count': int(residential[field].isna().sum()),
               'invalid_numeric_count': int(invalid.sum())}
        if not valid.empty:
            row.update({'min': valid.min(), 'max': valid.max(),
                        'mean': valid.mean(), 'median': valid.median()})
            for percentile in [1, 5, 25, 50, 75, 95, 99]:
                row[f'p{percentile:02d}'] = valid.quantile(percentile / 100)
            q1, q3 = valid.quantile(.25), valid.quantile(.75)
            iqr = q3 - q1
            # Extreme outliers use 3*IQR fences and remain in the dataset.
            lower, upper = q1 - 3 * iqr, q3 + 3 * iqr
            flags = ((values < lower) | (values > upper)).fillna(False)
            row.update({'extreme_lower_fence': lower, 'extreme_upper_fence': upper,
                        'extreme_outlier_count': int(flags.sum())})
            for index in values.index[flags]:
                outliers.append({'combined_row_index': index, 'field': field,
                                 'value': values.loc[index],
                                 'lower_fence': lower, 'upper_fence': upper})
            fig, axes = plt.subplots(1, 2, figsize=(11, 4))
            axes[0].hist(valid, bins=50, edgecolor='white')
            axes[0].set(title=f'{field}: histogram', xlabel=field, ylabel='Records')
            axes[1].boxplot(valid, vert=False)
            axes[1].set(title=f'{field}: boxplot', xlabel=field)
            fig.suptitle(f'{kind}: Residential (all valid values)')
            fig.tight_layout()
            fig.savefig(folder / f'{field}_distribution.png', dpi=150)
            plt.close(fig)
        summaries.append(row)
    summary = pd.DataFrame(summaries)
    summary.to_csv(folder / 'numeric_distribution_summary.csv', index=False)
    summary[summary['field'].isin(['ClosePrice', 'LivingArea', 'DaysOnMarket'])].to_csv(
        folder / 'required_numeric_summary.csv', index=False)
    pd.DataFrame(outliers, columns=['combined_row_index', 'field', 'value',
                                  'lower_fence', 'upper_fence']).to_csv(
        folder / 'extreme_outliers.csv', index=False)

    notes = [
        f'Dataset: {kind}', f'Run date: {date.today()}',
        f'Available months: {inventory.month.min()} through {inventory.month.max()}',
        f'Rows before filtering: {len(raw):,}',
        f'Rows after filtering: {len(residential):,}',
        f'Columns: {len(residential.columns)}',
        'Filter: PropertyType equals Residential exactly.',
        'Unique property types: ' + ', '.join(
            str(value) for value in raw['PropertyType'].dropna().unique()),
        f'Missing PropertyType records: {raw.PropertyType.isna().sum():,}',
        f'Residential share of all original records: {mask.mean() * 100:.2f}%',
        'Blank strings and whitespace are treated as nulls.',
        'Other textual missing-value codes require review; they are preserved.',
        'Numeric types are converted only for analysis; CSV values are preserved.',
        'No columns or outlier records are dropped.',
        'Extreme outliers: outside Q1 - 3*IQR or Q3 + 3*IQR.',
        'If IQR is zero, any value different from the quartiles is flagged.',
        'Unavailable numeric fields: ' + (', '.join(unavailable) or 'None'),
    ]
    expected = pd.period_range('2024-01', pd.Timestamp.today().to_period('M') - 1,
                               freq='M').strftime('%Y%m')
    absent = sorted(set(expected) - set(inventory.month))
    notes.append('Missing required months: ' + (', '.join(absent) or 'None'))

    if kind == 'Sold':
        if 'ClosePrice' in numbers:
            prices = numbers['ClosePrice'].dropna()
            notes.extend([f'Mean ClosePrice: {prices.mean():,.2f}',
                          f'Median ClosePrice: {prices.median():,.2f}'])
        if 'ClosePrice' in numbers and 'ListPrice' in numbers:
            close, listed = numbers['ClosePrice'], numbers['ListPrice']
            eligible = close.notna() & listed.notna() & (close > 0) & (listed > 0)
            denominator = int(eligible.sum())
            notes.append(f'Price comparison denominator (valid positive pairs): {denominator:,}')
            for label, condition in [('above', close > listed), ('below', close < listed),
                                     ('equal to', close == listed)]:
                percentage = (condition & eligible).sum() / denominator * 100 if denominator else float('nan')
                notes.append(f'Sold {label} list price: {percentage:.2f}%')
        if 'CountyOrParish' in residential and 'ClosePrice' in numbers:
            county = pd.DataFrame({'county': residential['CountyOrParish'],
                                   'ClosePrice': numbers['ClosePrice']}).dropna()
            ranking = county.groupby('county')['ClosePrice'].agg(
                valid_price_count='count', median_close_price='median',
                mean_close_price='mean').sort_values('median_close_price', ascending=False)
            ranking.to_csv(folder / 'county_price_summary.csv')
            notes.append('County rankings include all valid numeric prices; review sample sizes and outliers.')
        listing_date = next((field for field in ['ListingContractDate', 'OnMarketDate']
                             if field in residential), None)
        if listing_date and 'CloseDate' in residential:
            start = pd.to_datetime(residential[listing_date], errors='coerce', utc=True,
                                   format='mixed')
            end = pd.to_datetime(residential['CloseDate'], errors='coerce', utc=True,
                                 format='mixed')
            comparable = start.notna() & end.notna()
            issue = comparable & (end < start)
            residential.loc[issue].to_csv(folder / 'date_consistency_issues.csv', index=False)
            notes.extend([f'Date comparison field: {listing_date}',
                          f'Comparable date pairs: {comparable.sum():,}',
                          f'Close date before listing date: {issue.sum():,}',
                          f'Invalid nonblank {listing_date}: {(residential[listing_date].notna() & start.isna()).sum():,}',
                          f'Invalid nonblank CloseDate: {(residential.CloseDate.notna() & end.isna()).sum():,}'])
        else:
            notes.append('Date consistency check unavailable: required date columns not found.')

    (folder / 'analysis_notes.txt').write_text('\n'.join(notes) + '\n', encoding='utf-8')
    print('\n' + '\n'.join(notes))
    print('\nRequired numeric summary:')
    print(summary[summary.field.isin(['ClosePrice', 'LivingArea', 'DaysOnMarket'])].to_string(index=False))
    return notes


def main():
    if not DATA_DIR.is_dir():
        raise FileNotFoundError(f'Data folder not found: {DATA_DIR}')
    notes = []
    for kind in ['Listing', 'Sold']:
        notes.extend(analyze(kind))
    source = Path(__file__).read_text(encoding='utf-8')
    source = source.split('

# === RUN DOCUMENTATION ===
# Dataset: Listing
# Run date: 2026-10-05
# Available months: 202401 through 202604
# Rows before filtering: 860,898
# Rows after filtering: 547,162
# Columns: 84
# Filter: PropertyType equals Residential exactly.
# Unique property types: ManufacturedInPark, CommercialSale, Residential, ResidentialLease, Land, ResidentialIncome, CommercialLease, BusinessOpportunity
# Missing PropertyType records: 0
# Residential share of all original records: 63.56%
# Blank strings and whitespace are treated as nulls.
# Other textual missing-value codes require review; they are preserved.
# Numeric types are converted only for analysis; CSV values are preserved.
# No columns or outlier records are dropped.
# Extreme outliers: outside Q1 - 3*IQR or Q3 + 3*IQR.
# If IQR is zero, any value different from the quartiles is flagged.
# Unavailable numeric fields: None
# Missing required months: 202605, 202606, 202607, 202608, 202609
# Dataset: Sold
# Run date: 2026-10-05
# Available months: 202401 through 202604
# Rows before filtering: 615,707
# Rows after filtering: 414,054
# Columns: 84
# Filter: PropertyType equals Residential exactly.
# Unique property types: Residential, CommercialLease, Land, ResidentialLease, ManufacturedInPark, ResidentialIncome, CommercialSale, BusinessOpportunity
# Missing PropertyType records: 0
# Residential share of all original records: 67.25%
# Blank strings and whitespace are treated as nulls.
# Other textual missing-value codes require review; they are preserved.
# Numeric types are converted only for analysis; CSV values are preserved.
# No columns or outlier records are dropped.
# Extreme outliers: outside Q1 - 3*IQR or Q3 + 3*IQR.
# If IQR is zero, any value different from the quartiles is flagged.
# Unavailable numeric fields: None
# Missing required months: 202605, 202606, 202607, 202608, 202609
# Mean ClosePrice: 1,193,864.08
# Median ClosePrice: 823,000.00
# Price comparison denominator (valid positive pairs): 414,051
# Sold above list price: 40.10%
# Sold below list price: 42.55%
# Sold equal to list price: 17.35%
# County rankings include all valid numeric prices; review sample sizes and outliers.
# Date comparison field: ListingContractDate
# Comparable date pairs: 414,053
# Close date before listing date: 61
# Invalid nonblank ListingContractDate: 0
# Invalid nonblank CloseDate: 0
