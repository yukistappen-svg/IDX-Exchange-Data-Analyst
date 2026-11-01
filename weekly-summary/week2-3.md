# Weeks 2–3: Dataset Structuring, Validation & Exploratory Data Analysis

### Objective

To improve the quality and consistency of the consolidated CRMLS residential real estate datasets through data validation, missing value analysis, outlier treatment, and exploratory data analysis (EDA), preparing the data for further market analysis and visualization.

### 1. Dataset Structure and Validation

- Loaded the consolidated Listing and Sold datasets covering January 2024 through April 2026.
- Inspected dataset dimensions, column names, data types, and completeness.
- Identified and removed 11 redundant columns from the Listing dataset after checking for duplicate values and discrepancies.
- Verified that all observations were classified as `Residential`.

**Initial dataset dimensions:**

| Dataset | Records | Columns After Duplicate Column Removal |
|---|---:|---:|
| Listing | 547,162 | 73 |
| Sold | 414,054 | 84 |

### 2. Missing Value Analysis

- Calculated missing counts and percentages for each variable.
- Identified 13 Listing columns and 15 Sold columns with missing rates exceeding 90%.
- Removed high-missingness, nonessential columns while retaining core analytical variables.

**Remaining columns:**
- Listing: 60
- Sold: 69

### 3. Data Cleaning and Outlier Treatment

Performed data quality checks and applied documented cleaning rules to key numerical variables.

**Price Validation**
- Identified suspected 1,000-fold scaling errors in `ClosePrice` and `OriginalListPrice`.
- Applied 113 provisional field-level price corrections while preserving original values.
- Excluded records with cleaned price fields above the provisional $50 million threshold: 200 Listing records and 55 Sold records.
- Flagged 5 additional Listing and 13 Sold close prices below $10,000 as missing for conventional residential price analysis.

**Days on Market (DOM)**
- Identified negative and unusually high DOM values.
- Created `DaysOnMarket_Clean`, replacing negative values and values above 730 days with missing values.
- Preserved original DOM data for traceability.

**Property Size and Characteristics**
- Created cleaned variables for living area, lot size, bedrooms, and bathrooms.
- Flagged nonpositive living areas and unusually large values above 20,000 square feet.
- Flagged lot sizes above 100 acres.
- Flagged bedroom and bathroom counts exceeding 20.
- Retained original fields alongside the cleaned variables.

These thresholds were applied as provisional analytical rules rather than definitive evidence of erroneous property records.

### 4. Date Consistency and Duplicate Validation

- Checked chronological consistency across listing, contract, and closing dates.
- Identified 530 Listing records and 507 Sold records with at least one date sequence issue.
- Created `DateIssueFlag` to retain and track potentially inconsistent records.
- Investigated repeated `ListingKey` values.
- Removed 48 exact duplicate Sold records while retaining nonidentical records sharing a ListingKey for further review.

### 5. Exploratory Data Analysis (EDA)

Conducted descriptive statistics, percentile analysis, histograms, and boxplots to evaluate housing price distributions and property characteristics.

**Key Findings**

- Residential sale prices displayed a positively skewed distribution, with mean prices exceeding median prices.
- The median cleaned Sold close price was approximately $822,500 in the pre-deduplication numeric summary.
- Median Days on Market was 10 days for Listing and 18 days for Sold.
- Following final deduplication, 42.55% of valid Sold records closed below asking price, 40.10% above asking price, and 17.36% at asking price.
- The median sale-to-list price ratio was 100%.
- San Mateo County had the highest median residential close price at $1.70 million, followed by Santa Clara County at $1.60 million.

### 6. Final Dataset

| Dataset | Final Records |
|---|---:|
| Listing | 546,962 |
| Sold | 413,951 |
| **Total** | **960,913** |

Final dataset validation confirmed that all remaining observations were Residential and that cleaned values satisfied the selected validation thresholds.

### Key Accomplishments

Successfully structured, validated, and cleaned approximately 961,000 residential MLS records. Improved data consistency by removing redundant columns, addressing missing values, identifying potential scaling errors, treating outliers, flagging date inconsistencies, and removing exact duplicate records.

The resulting datasets provide a more reliable foundation for residential market analysis, mortgage rate enrichment, and Tableau visualization.

### Deliverables

- `listing_residential_cleaned.csv`
- `sold_residential_cleaned.csv`
- Data cleaning and validation code in Jupyter Notebook, to be saved as a `.py` script
- Descriptive statistics, percentile summaries, and EDA findings
