# Week 6 — Feature Engineering and Market Metrics
**IDX Exchange | Data Analyst Internship**

## 1. Objective

The objective of Week 6 was to develop analytical features from the cleaned CRMLS residential real estate datasets to support housing market analysis and future Tableau dashboards.

The project focused on constructing price-related indicators, transaction timeline metrics, and time-series variables. Geographic enrichment was also performed by linking residential properties to California school district boundaries using their latitude and longitude coordinates.

Finally, segmented summary statistics were generated to identify differences in residential market conditions across counties.

## 2. Dataset Overview

The analysis utilized the Week 4–5 validated residential datasets, including the previously integrated monthly 30-year fixed mortgage rate data from FRED.

| Dataset | Number of Records |
|---|---:|
| Residential Listing | 546,962 |
| Residential Sold | 413,951 |
| **Total** | **960,913** |

Feature engineering was performed without changing the number of property records.

## 3. Feature Engineering

The following variables were constructed using Python and Pandas.

| Engineered Feature | Calculation | Analytical Purpose |
|---|---|---|
| Price Ratio | ClosePrice / OriginalListPrice | Measures the relationship between final sale price and initial asking price |
| Close-to-Original-List Ratio | ClosePrice / OriginalListPrice | Evaluates the final sale price relative to the original listing price |
| Price Per Square Foot (PPSF) | ClosePrice / LivingArea | Standardizes prices across properties of different sizes |
| Days on Market | Original DaysOnMarket field | Measures the recorded time a property remained on the market |
| Year | Extracted from transaction date | Supports annual market analysis |
| Month | Extracted from transaction date | Supports monthly grouping |
| YrMo | YYYY-MM format | Enables time-series analysis |
| Listing-to-Contract Days | PurchaseContractDate − ListingContractDate | Measures the time between listing and accepted contract |
| Contract-to-Close Days | CloseDate − PurchaseContractDate | Measures the duration between contract signing and closing |

For Sold records, Year, Month, and YrMo were derived from CloseDate. For Listing records, they were derived from ListingContractDate.

Price Ratio and Close-to-Original-List Ratio follow the same formula, as specified in the internship handbook.

Missing or invalid denominators were excluded from ratio calculations. Negative transaction timeline values were flagged and excluded from the corresponding derived duration fields.

## 4. Feature Validation Results

The engineered features were validated to confirm that the transformation process preserved all property records and that generated numerical ratios and durations satisfied the implemented validation checks.

| Validation Metric | Listing | Sold |
|---|---:|---:|
| Rows Before | 546,962 | 413,951 |
| Rows After | 546,962 | 413,951 |
| Valid Price Ratios | 136,869 | 413,177 |
| Valid Price Per Sq Ft | 137,525 | 413,539 |
| School District Matches | 466,249 | 409,632 |
| Validation Status | Passed | Passed |

The lower number of valid price ratios in the Listing dataset is largely associated with missing closing prices for properties without recorded sales.

Both datasets preserved their original row counts after feature engineering and geographic enrichment.

## 5. Sample Engineered Metrics

The following observations are taken from the actual Sold dataset output. Values are displayed with rounding where appropriate.

| County | Close Price | Price Ratio | PPSF ($/sqft) | DOM |
|---|---:|---:|---:|---:|
| San Mateo | $240,000 | 0.48 | 210.53 | 777 |
| San Diego | $815,000 | 1.07 | 412.87 | 33 |
| San Diego | $810,000 | 1.09 | 410.33 | 228 |
| San Luis Obispo | $2,100,000 | 1.00 | 562.10 | 0 |
| Mendocino | $1,950,000 | 1.00 | 928.57 | -36 |
| Santa Clara | $2,340,000 | Missing | 958.23 | 0 |
| San Diego | $1,485,000 | 0.96 | 927.55 | 0 |
| Los Angeles | $1,130,000 | 1.13 | 529.03 | 1 |
| Los Angeles | $1,060,000 | 1.01 | 552.95 | 34 |
| San Mateo | $2,150,000 | Missing | 977.27 | 0 |

The sample confirms that the engineered price ratio and PPSF variables were populated for records with valid input values.

Some records contain missing original listing prices, resulting in missing price ratios. Original DOM values also reveal anomalies such as negative or unusually high market durations; these are retained for data quality review rather than treated as valid market durations.

The full sample output additionally includes Year, Month, YrMo, ListingToContractDays, ContractToCloseDays, and school district information.

## 6. California School District Enrichment

School district geographic boundary data for the 2024–25 school year was integrated using GeoPandas.

The school district dataset contained 937 geographic boundary records and 54 attributes.

| School District Type | Records |
|---|---:|
| Elementary | 516 |
| Unified | 345 |
| High | 76 |
| **Total** | **937** |

Property coordinates were converted into geographic points and spatially matched to district polygons using a spatial join.

**Matching results:**

- Listing: 466,249 properties matched to at least one school district.
- Sold: 409,632 properties matched to at least one school district.

Where multiple school district boundaries overlapped, matching district names were retained without generating additional property records.

The enrichment allows future housing market analysis at the school district level. These geographic matches represent boundary associations, not verification of individual school enrollment eligibility.

## 7. County-Level Segmented Analysis

Residential Sold records were grouped by CountyOrParish to calculate transaction counts, median close prices, average close prices, median PPSF, median DOM, median price ratios, and median contract-to-close periods.

### Top 10 Counties by Median Residential Close Price

| County | Transactions | Median Close Price | Median PPSF | Median DOM |
|---|---:|---:|---:|---:|
| San Mateo | 7,277 | $1,700,000 | $1,051.86 | 12 |
| Santa Clara | 18,452 | $1,600,000 | $966.49 | 10 |
| Santa Cruz | 2,998 | $1,200,000 | $736.40 | 18 |
| San Francisco | 956 | $1,198,950 | $886.36 | 16 |
| Orange | 46,591 | $1,175,000 | $672.81 | 14 |
| Marin | 146 | $1,165,000 | $678.86 | 21 |
| Alameda | 19,526 | $1,131,440 | $700.93 | 14 |
| Monterey | 3,987 | $910,000 | $592.61 | 19 |
| Los Angeles | 102,851 | $900,000 | $608.44 | 19 |
| San Diego | 51,144 | $899,000 | $591.12 | 15 |

### Key Findings

**Regional Price Differences:** San Mateo County recorded the highest median residential closing price at $1.70 million, followed by Santa Clara County at $1.60 million.

**Price per Square Foot:** San Mateo and Santa Clara also recorded the highest median PPSF among the reported counties, indicating relatively high housing prices after accounting for property size.

**Market Activity:** Los Angeles County had the largest transaction count among the ten counties, with 102,851 valid closing-price records.

**Market Speed:** Santa Clara County recorded a median DOM of 10 days, compared with 19 days in Los Angeles County.

**Negotiation Outcomes:** Santa Clara's median close-to-original-list ratio was 1.02, indicating a typical closing price approximately 2% above the original listing price among observations with valid ratios.

These results highlight differences in residential pricing, market activity, and transaction timing across California counties.

## 8. Data Quality Considerations

The feature engineering workflow retained existing quality flags and preserved original numerical fields where available.

Several potentially anomalous values remain in the data, including unusually high or negative Days on Market, extreme price ratios, and long contract-to-close periods.

Although basic feature validation passed, additional outlier investigation would be necessary before using all derived indicators for production-level forecasting or causal analysis.

The segmented summary should therefore be interpreted as an exploratory market analysis based on the current analytical filters.

Furthermore, transaction counts represent dataset records and may not always correspond to uniquely identified property transactions where nonidentical duplicate ListingKey records remain.

## 9. Deliverables

The Week 6 deliverables consist of:

- A Python script implementing all required engineered metrics.
- Sample output demonstrating the populated feature columns.
- County-level segmented summary statistics.
- Geographic school district enrichment results.
- Engineered residential datasets suitable for downstream Tableau analysis.

## 10. Conclusion

Week 6 successfully transformed the validated residential MLS datasets into feature-enriched analytical datasets.

New price, property size, transaction timeline, and time-series indicators were generated using Pandas, while California school district boundaries were integrated using GeoPandas.

The completed features and segmented summaries provide a foundation for geographic market comparisons, pricing analysis, transaction efficiency monitoring, and the development of interactive Tableau dashboards.
