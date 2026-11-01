# Mortgage Rate Enrichment: FRED Data Integration

### Objective

To enrich the cleaned CRMLS Listing and Sold datasets with historical U.S. 30-year fixed mortgage rates from the Federal Reserve Economic Data (FRED) database, enabling further analysis of the relationship between mortgage financing conditions and residential real estate market activity.

### 1. Mortgage Rate Data Collection

- Retrieved the `MORTGAGE30US` series directly from FRED using Python and Pandas.
- Obtained weekly observations of the U.S. 30-year fixed mortgage rate, sourced from Freddie Mac.
- Retrieved 2,901 observations covering April 2, 1971, through October 29, 2026.
- Validated the date and mortgage rate fields and confirmed zero missing values.

### 2. Weekly-to-Monthly Aggregation

- Converted weekly observation dates into monthly periods using Pandas.
- Calculated the arithmetic mean of weekly mortgage rates within each calendar month.
- Restricted the monthly series to the MLS analysis period of January 2024 through April 2026.
- Generated 28 monthly mortgage rate observations, with no missing values.

**Example Monthly Mortgage Rates**

| Month | Average 30-Year Mortgage Rate |
|---|---:|
| January 2024 | 6.6425% |
| February 2024 | 6.7760% |
| March 2024 | 6.8200% |
| April 2024 | 6.9925% |
| April 2026 | 6.3320% |

### 3. Monthly Key Creation

Created a common `year_month` key to align MLS records with monthly FRED observations.

- **Sold dataset:** Derived the matching month from `CloseDate`.
- **Listing dataset:** Derived the matching month from `ListingContractDate`.

Confirmed that all MLS observations fell within January 2024 through April 2026 and that neither dataset contained missing monthly keys.

### 4. Mortgage Rate Integration

Performed a left join using Pandas `merge()` to attach the monthly mortgage rate to each residential property observation.

- Used `year_month` as the common join key.
- Applied `validate="many_to_one"` to ensure each MLS observation matched at most one monthly mortgage rate.
- Preserved all original MLS records.
- Added `rate_30yr_fixed` to both datasets.

### 5. Merge Validation

Validated row counts, mortgage rate completeness, matching periods, and observed rate ranges.

| Validation Metric | Listing | Sold |
|---|---:|---:|
| Records Before Merge | 546,962 | 413,951 |
| Records After Merge | 546,962 | 413,951 |
| Missing Mortgage Rates | 0 | 0 |
| Minimum Monthly Rate | 6.0475% | 6.0475% |
| Maximum Monthly Rate | 7.0600% | 7.0600% |
| Merge Status | Passed | Passed |

All 960,913 MLS records were successfully matched with monthly mortgage rate observations without changing the number of records.

### 6. Final Enriched Datasets

| Dataset | Records | Columns |
|---|---:|---:|
| Listing with Mortgage Rates | 546,962 | 71 |
| Sold with Mortgage Rates | 413,951 | 80 |

The enriched datasets include cleaned MLS variables, a monthly matching key, and the corresponding monthly average 30-year fixed mortgage rate.

### Key Accomplishments

Successfully integrated an external macroeconomic time series into two large-scale residential real estate datasets. Automated the retrieval of mortgage rate data, converted weekly observations into monthly averages, created standardized temporal matching keys, and validated the completeness of both joins.

The enriched data enables future analysis of relationships between mortgage rate fluctuations, residential sale prices, listing activity, transaction volume, and Days on Market.

### Deliverables

- `listing_with_mortgage_rates.csv`
- `sold_with_mortgage_rates.csv`
- Python code for FRED data retrieval, monthly aggregation, merging, and validation, to be saved as a `.py` script
