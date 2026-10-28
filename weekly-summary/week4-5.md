# Weeks 4–5: Data Cleaning and Preparation — Output Summary

## 1. Overview

This phase focused on cleaning and preparing the residential MLS transaction dataset for further analysis and Tableau visualization.

The cleaning process included data type conversion, missing value treatment, numeric validation, date consistency checks, geographic validation, and duplicate detection.

The primary objective was to improve data reliability while preserving useful transaction records.

## 2. Dataset Overview

| Metric | Count |
|---|---:|
| Initial Records | 414,054 |
| Exact Duplicate Records Removed | 48 |
| Final Records | 414,006 |

The cleaned dataset retains transactions with identified data quality issues, using Boolean flags to support further investigation and analysis-specific filtering.

## 3. Missing Value Analysis

Missing values were examined across all columns before applying cleaning operations.

Several nonessential fields had high missing percentages, including:

- OriginatingSystemName: 89.25%
- ElementarySchool: 86.69%
- HighSchool: 82.60%
- CoListOfficeName: 76.33%
- SubdivisionName: 62.81%

These fields were removed because of their high missing rates and limited relevance to the current analysis.

Core analytical fields showed relatively low missing rates:

- ClosePrice: 2 missing values
- LivingArea: 234 missing values
- Latitude and Longitude: 4,104 missing values each

Missing values in essential fields were retained rather than replaced with arbitrary values.

## 4. Numeric Data Validation

Numeric fields were converted to appropriate data types and checked for invalid values.

| Invalid Condition | Records |
|---|---:|
| ClosePrice ≤ 0 | 1 |
| LivingArea ≤ 0 | 150 |
| DaysOnMarket < 0 | 48 |
| Negative Bedrooms | 0 |
| Negative Bathrooms | 0 |
| Total Unique Invalid Records | 199 |

Only 0.048% of the original dataset contained flagged numeric inconsistencies.

Invalid values were flagged rather than automatically removed to preserve transaction information.

## 5. Date Consistency Checks

Four date fields were converted to datetime format:

- CloseDate
- PurchaseContractDate
- ListingContractDate
- ContractStatusChangeDate

Transaction timelines were checked against the expected sequence:

**Listing Date → Purchase Contract Date → Close Date**

| Date Issue | Records |
|---|---:|
| Listing Date After Close Date | 61 |
| Purchase Date After Close Date | 239 |
| Listing Date After Purchase Date | 268 |
| Total Unique Date Inconsistencies | 507 |

The overall date inconsistency rate was approximately 0.122%.

These records were flagged for further review rather than automatically corrected.

## 6. Geographic Data Quality

Latitude and longitude values were examined to identify missing, zero, positive-longitude, and geographically implausible coordinates.

| Geographic Issue | Records |
|---|---:|
| Missing Coordinates | 4,104 |
| Zero Coordinates | 27 |
| Positive Longitude | 31 |
| Outside California Bounding Box | 33 |
| Non-California State Codes | 29 |

A total of 4,208 records (approximately 1.016%) were flagged for geographic data quality issues after incorporating state-code validation.

The dataset contained 414,025 records labeled as California transactions and 29 records with other state codes.

Some of these records had coordinates consistent with their reported out-of-state locations, while others showed potential discrepancies between geographic coordinates and state labels.

Because the coordinate screening used an approximate California bounding box rather than precise state boundaries, suspicious records were retained for further validation.

## 7. Duplicate Record Analysis

Duplicate analysis identified 48 exact duplicate records, which were removed.

Additional investigation identified 290 groups of repeated ListingKey values after exact duplicate removal.

Among these groups:

- All 290 groups contained different closing dates.
- 71 groups contained different closing prices.
- No groups contained different ListingId values.

These records were retained and flagged because the observed differences could reflect transaction updates, duplicated source records, or other data inconsistencies.

Further validation is necessary before treating all repeated ListingKey records as independent transactions.

## 8. Final Data Quality Assessment

The final data quality summary reported:

| Category | Flagged Records | Percentage |
|---|---:|---:|
| Invalid Numeric Values | 199 | 0.048% |
| Date Inconsistencies | 507 | 0.122% |
| Geographic Issues | 4,208 | 1.016% |
| Duplicate Listings | 584 | 0.141% |
| Any Data Quality Issue | 5,470 | 1.321% |

*Note: These categories may overlap. The overall count reflects records flagged by at least one quality check.*

The cleaning process preserved the majority of the dataset while identifying potentially unreliable records through explicit validation flags.

## 9. Conclusion

The residential MLS dataset was prepared for subsequent exploratory analysis and Tableau visualization.

The main outcomes were:

- Standardized date and numeric fields
- Removed unnecessary and high-missingness columns
- Preserved missing values in essential analytical fields
- Flagged invalid prices, property characteristics, and transaction timelines
- Identified geographic inconsistencies
- Removed exact duplicates while retaining unresolved listing-level conflicts

The resulting dataset supports further market analysis, including price trends, transaction activity, property characteristics, and geographic comparisons. Analysis-specific filtering will be necessary to exclude invalid observations and avoid double-counting unresolved duplicate listings.
