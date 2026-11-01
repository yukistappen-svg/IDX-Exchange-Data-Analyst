# Week 1 Summary: Monthly Dataset Aggregation

### 1. Data Loading
- Imported 56 monthly CRMLS CSV files using Python (Pandas and Pathlib).
- **Time period:** January 2024 – April 2026.
- **Datasets:** 28 Listing files and 28 Sold files.

### 2. Data Concatenation
- Used `pd.concat()` to combine monthly datasets into two separate DataFrames.
- **Listing:** 860,898 records.
- **Sold:** 615,707 records.
- **Total:** 1,476,605 records.

### 3. Residential Filtering
- Filtered both datasets using `PropertyType == "Residential"`.
- Excluded non-residential property types, including commercial properties, land, and rentals.

| Dataset | Before Filtering | After Filtering | Retention Rate |
|---|---:|---:|---:|
| Listing | 860,898 | 547,162 | 63.6% |
| Sold | 615,707 | 414,054 | 67.2% |
| **Total** | **1,476,605** | **961,216** | **65.1%** |

### 4. Data Validation
- Verified that row counts before and after concatenation matched.
- Confirmed that all remaining records were classified as Residential.
- Used Python `assert` statements to validate data consistency.
- All validation checks passed.

### 5. Data Export
Prepared two filtered datasets for export:
- `combined_listing_residential.csv` — 547,162 records.
- `combined_sold_residential.csv` — 414,054 records.

### Key Accomplishments

Successfully consolidated 56 monthly CRMLS files into two datasets and filtered them to retain **961,216 residential property records**. Validated the aggregation and filtering results to establish a consistent foundation for subsequent data cleaning, exploratory data analysis (EDA), and Tableau visualization.

### Next Steps
- Confirm successful CSV exports and save the Python script.
- Obtain additional monthly files if required to cover the full reporting period.
- Proceed with data quality checks, missing value analysis, and outlier detection.
