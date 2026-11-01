# Week 6 — Feature Engineering and Market Metrics
**IDX Exchange | Data Analyst Internship**

## 1. Objective

The objective of Week 6 was to develop analytical features from CRMLS residential real estate datasets and identify market patterns across property types, geographic regions, and real estate brokerage offices.

The analysis focused on three major components:

1. **Feature Engineering:** Creating price, property size, transaction duration, and time-series indicators.
2. **Geographic Enrichment:** Matching residential properties to California school district boundaries.
3. **Segmented Market Analysis:** Comparing housing market performance across property categories, geographic locations, and brokerage offices.

## 2. Dataset Overview

The analysis used the residential Listing and Sold datasets prepared during Weeks 4–5, including previously integrated monthly 30-year fixed mortgage rates.

| Dataset | Records |
|---|---:|
| Residential Listing | 546,962 |
| Residential Sold | 413,951 |
| **Total** | **960,913** |

Both datasets retained their original record counts following feature engineering.

## 3. Feature Engineering

The following variables were created using Python and Pandas.

| Engineered Metric | Calculation | Purpose |
|---|---|---|
| PriceRatio | ClosePrice / OriginalListPrice | Measures the relationship between closing and original asking prices |
| CloseToOriginalListRatio | ClosePrice / OriginalListPrice | Evaluates final selling prices relative to initial listings |
| PricePerSqFt | ClosePrice / LivingArea | Standardizes prices by property size |
| DaysOnMarket_Metric | DaysOnMarket | Measures recorded market exposure |
| Year | Year extracted from relevant date | Annual analysis |
| Month | Month extracted from relevant date | Monthly analysis |
| YrMo | YYYY-MM | Monthly time-series grouping |
| ListingToContractDays | PurchaseContractDate − ListingContractDate | Measures the listing-to-contract period |
| ContractToCloseDays | CloseDate − PurchaseContractDate | Measures the contract-to-closing period |

For Sold records, Year and Month were derived from CloseDate. For Listing records, these variables were derived from ListingContractDate.

PriceRatio and CloseToOriginalListRatio share the same calculation, consistent with the internship requirements.

### Feature Validation

| Validation Metric | Listing | Sold |
|---|---:|---:|
| Original Records | 546,962 | 413,951 |
| Records After Engineering | 546,962 | 413,951 |
| Valid Price Ratios | 136,869 | 413,177 |
| Valid Price Per Sq Ft | 137,525 | 413,539 |
| School District Matches | 466,249 | 409,632 |

All row-count preservation and implemented numerical validation checks passed.

Some derived features contained missing values because their source fields were missing or unsuitable for calculation.

## 4. Sample Engineered Metrics

The following sample demonstrates newly generated metrics from the residential Sold dataset.

| County | Close Price | Price Ratio | PPSF ($/sqft) | DOM | Listing-to-Contract Days | Contract-to-Close Days |
|---|---:|---:|---:|---:|---:|---:|
| San Mateo | $240,000 | 0.48 | 210.53 | 777 | 777 | 65 |
| San Diego | $815,000 | 1.07 | 412.87 | 33 | 114 | 919 |
| San Diego | $810,000 | 1.09 | 410.33 | 228 | 255 | 778 |
| San Luis Obispo | $2,100,000 | 1.00 | 562.10 | 0 | 0 | 48 |
| Mendocino | $1,950,000 | 1.00 | 928.57 | -36 | 32 | 34 |
| Santa Clara | $2,340,000 | Missing | 958.23 | 0 | 33 | Missing |
| San Diego | $1,485,000 | 0.96 | 927.55 | 0 | 1 | 21 |
| Los Angeles | $1,130,000 | 1.13 | 529.03 | 1 | 1 | 17 |
| Los Angeles | $1,060,000 | 1.01 | 552.95 | 34 | 34 | 6 |
| San Mateo | $2,150,000 | Missing | 977.27 | 0 | 5 | Missing |

All sample transactions were assigned to January 2024 (`YrMo = 2024-01`), based on CloseDate.

The sample illustrates successful computation of price-related and transaction timeline indicators. It also reveals several values requiring additional data quality investigation, including negative DOM, unusually long transaction periods, and extreme price ratios.

## 5. School District Enrichment

California school district boundary data for the 2024–25 school year was integrated using GeoPandas.

The geographic dataset contained 937 school district boundary records, classified as follows:

| District Type | Number of Records |
|---|---:|
| Elementary | 516 |
| Unified | 345 |
| High | 76 |
| **Total** | **937** |

Spatial joins were performed using each property's geographic coordinates.

The process successfully matched 466,249 Listing records and 409,632 Sold records to at least one school district.

Where elementary and high school district boundaries overlapped, multiple matching names were retained within the property record to prevent duplicate observations.

This enrichment enables subsequent analysis of housing market conditions at the school district level.

## 6. Segmented Market Analysis

Following feature engineering, residential Sold records were grouped across property characteristics, geographic regions, and brokerage offices.

The following statistics were calculated for each segment:

- Transaction Count
- Median and Mean Close Price
- Median Price Per Square Foot
- Median Days on Market
- Median Price Ratio
- Median Contract-to-Close Days

Transaction counts represent valid closing-price records in each segment, subject to the current dataset's duplicate-record treatment.

### 6.1 Property Analysis

#### PropertyType

The input datasets had already been filtered to Residential properties. Consequently, PropertyType provides the overall residential market classification rather than a comparison across commercial and residential property categories.

#### PropertyType

The dataset was filtered to include residential properties only. Therefore, the PropertyType segment contains a single category: Residential.

**Table: Residential Property Type Summary**

| PropertyType | Transaction Count | Median Close Price | Mean Close Price | Median PPSF | Median DOM | Median Price Ratio | Median Contract-to-Close Days |
|---|---:|---:|---:|---:|---:|---:|---:|
| Residential | 413,935 | $822,150 | $1,137,018.80 | $537.43 | 18 | 1.00 | 29 |

**Key Findings**

The residential market analysis includes 413,935 transactions with valid closing prices. The median closing price was $822,150, while the mean closing price was approximately $1.14 million.

The mean closing price being higher than the median suggests a right-skewed price distribution, potentially influenced by high-value properties.

The median price per square foot was $537.43, and the median Days on Market was 18 days.

The median Price Ratio was 1.00, indicating that the typical closing price was approximately equal to the original listing price among transactions with valid ratios.

The median Contract-to-Close period was 29 days.

Since the dataset includes only Residential properties, more detailed comparisons are conducted using PropertySubType in the following section.

#### PropertySubType

PropertySubType provides a more detailed comparison of housing categories.

| Property Subtype | Transactions | Median Close Price | Median PPSF | Median DOM |
|---|---:|---:|---:|---:|
| SingleFamilyResidence | 309,644 | $893,000 | $532.67 | 17 |
| Condominium | 68,467 | $628,000 | $565.08 | 24 |
| Townhouse | 24,282 | $805,000 | $562.14 | 17 |
| ManufacturedOnLand | 5,342 | $324,450 | $225.69 | 30 |
| Duplex | 2,255 | $915,000 | $544.97 | 21 |
| StockCooperative | 1,663 | $360,000 | $395.92 | 20 |
| Cabin | 470 | $238,000 | $287.76 | 47 |
| Triplex | 336 | $1,102,500 | $464.19 | 30 |
| MixedUse | 205 | $700,000 | $436.78 | 52 |
| Quadruplex | 141 | $1,250,500 | $370.12 | 34 |

**Key Findings**

Single-family residences dominated residential transactions, accounting for 309,644 records. Their median closing price was $893,000, with a median DOM of 17 days.

Condominiums had a lower median total closing price of $628,000 but a slightly higher median PPSF of $565.08 compared with single-family residences at $532.67. This suggests that lower total property prices do not necessarily imply lower prices per unit of living area.

Townhouses recorded a median closing price of $805,000 and a median DOM of 17 days, similar to single-family residences in market exposure.

Manufactured homes and cabins generally recorded lower median closing prices but longer market durations. Cabins had a median DOM of 47 days, while mixed-use properties recorded 52 days.

These findings suggest that property category is an important dimension for analyzing price levels and market liquidity.

### 6.2 Geographic Analysis

#### CountyOrParish

The following table presents the ten counties with the highest median closing prices among the displayed qualifying county groups.

| County | Transactions | Median Close Price | Median PPSF | Median DOM | Median Price Ratio |
|---|---:|---:|---:|---:|---:|
| San Mateo | 7,277 | $1,700,000 | $1,051.86 | 12 | 1.01 |
| Santa Clara | 18,452 | $1,600,000 | $966.49 | 10 | 1.02 |
| Santa Cruz | 2,998 | $1,200,000 | $736.40 | 18 | 0.98 |
| San Francisco | 956 | $1,198,950 | $886.36 | 16 | 1.00 |
| Orange | 46,591 | $1,175,000 | $672.81 | 14 | 0.99 |
| Marin | 146 | $1,165,000 | $678.86 | 21 | 0.97 |
| Alameda | 19,526 | $1,131,440 | $700.93 | 14 | 1.02 |
| Monterey | 3,987 | $910,000 | $592.61 | 19 | 0.98 |
| Los Angeles | 102,851 | $900,000 | $608.44 | 19 | 1.00 |
| San Diego | 51,144 | $899,000 | $591.12 | 15 | 0.99 |

**Key Findings**

San Mateo County recorded the highest median closing price at $1.70 million and the highest median PPSF at $1,051.86 among the reported counties.

Santa Clara County followed with a median closing price of $1.60 million. Its median DOM of 10 days and median price ratio of 1.02 suggest relatively fast transactions and closing prices modestly above original asking prices.

Los Angeles County recorded the highest number of valid closing-price records in this comparison, with 102,851 transactions, despite having a lower median closing price of $900,000.

These findings demonstrate that higher transaction volume does not necessarily correspond to higher median housing prices.

#### MLSAreaMajor

MLSAreaMajor provides a more granular geographic segmentation.

| MLS Area | Transactions | Median Close Price | Median PPSF | Median DOM |
|---|---:|---:|---:|---:|
| 699 - Not Defined | 43,415 | $1,225,000 | $776.69 | 13 |
| SRCAR - Southwest Riverside County | 20,194 | $585,000 | $293.57 | 23 |
| 252 - Riverside | 5,253 | $655,000 | $379.34 | 20 |
| 248 - Corona | 3,326 | $755,275.50 | $396.89 | 21 |
| LAC - Lancaster | 3,069 | $475,000 | $270.86 | 25 |
| VIC - Victorville | 2,922 | $438,000 | $237.92 | 25 |
| 274 - San Bernardino | 2,895 | $499,900 | $352.76 | 20 |
| 263 - Banning/Beaumont/Cherry Valley | 2,885 | $499,686 | $259.74 | 30 |
| 686 - Ontario | 2,622 | $650,549 | $417.66 | 19 |
| 259 - Moreno Valley | 2,622 | $555,000 | $312.28 | 18 |

**Key Findings**

Southwest Riverside County recorded 20,194 transactions, with a median closing price of $585,000 and median PPSF of $293.57.

Corona recorded a higher median closing price of approximately $755,276 and median PPSF of $396.89 compared with Riverside and Southwest Riverside County.

Victorville and Lancaster had lower median closing prices of $438,000 and $475,000, respectively.

The category `699 - Not Defined` accounted for 43,415 transactions and should be interpreted as an unspecified MLS area rather than a single geographic market.

The MLS-level analysis demonstrates substantial variation within broader regional markets.

### 6.3 Competitive Intelligence

Brokerage performance was evaluated using both ListOfficeName and BuyerOfficeName.

The listing office represents the brokerage associated with the selling-side listing. The buyer office represents the brokerage associated with the purchasing side.

These two dimensions provide complementary perspectives on brokerage transaction participation.

#### ListOfficeName

| Listing Office | Transactions | Median Close Price | Median PPSF | Median DOM |
|---|---:|---:|---:|---:|
| Compass | 29,095 | $1,350,000 | $757.78 | 14 |
| Coldwell Banker Realty | 18,689 | $1,195,000 | $695.01 | 16 |
| Keller Williams Realty | 8,120 | $870,000 | $540.32 | 15 |
| First Team Real Estate | 5,794 | $960,000 | $609.14 | 13 |
| Berkshire Hathaway HomeServices California Properties* | 5,477 | $950,000 | $598.48 | 23 |
| eXp Realty of California Inc | 4,820 | $790,000 | $532.29 | 19 |
| Real Broker | 4,719 | $845,000 | $557.88 | 15 |
| Intero Real Estate Services | 4,519 | $1,375,000 | $847.63 | 11 |
| eXp Realty of California, Inc. | 3,591 | $760,000 | $494.23 | 13 |
| Equity Union | 3,524 | $860,000 | $477.46 | 28 |

*The Berkshire Hathaway name was truncated in the displayed dataset output.*

**Key Findings**

Compass recorded the highest listing-side transaction count among the displayed offices, with 29,095 records, followed by Coldwell Banker Realty with 18,689.

Intero Real Estate Services recorded a median closing price of $1.375 million and a median DOM of 11 days, indicating its observed transactions were concentrated in relatively high-priced properties with shorter recorded market durations.

Compass also operated within a higher-priced market segment, with a median closing price of $1.35 million.

However, differences in median price and DOM should not be interpreted as direct measures of brokerage performance without controlling for location, property type, and transaction characteristics.

#### BuyerOfficeName

| Buyer Office | Transactions | Median Close Price | Median PPSF | Median DOM |
|---|---:|---:|---:|---:|
| Compass | 27,177 | $1,325,000 | $751.74 | 14 |
| Coldwell Banker Realty | 14,952 | $1,194,000 | $689.19 | 16 |
| NONMEMBER MRML | 8,834 | $503,425.50 | $289.96 | 26 |
| Keller Williams Realty | 6,369 | $835,000 | $533.76 | 17 |
| Real Broker | 6,161 | $800,000 | $541.80 | 18 |
| eXp Realty of California Inc | 5,278 | $835,000 | $570.03 | 19 |
| First Team Real Estate | 5,238 | $900,000 | $597.52 | 14 |
| eXp Realty of California, Inc. | 4,696 | $728,950 | $494.51 | 18 |
| Berkshire Hathaway HomeServices California Properties* | 4,260 | $975,000 | $607.48 | 20 |
| Intero Real Estate Services | 3,663 | $1,335,000 | $816.26 | 12 |

*The Berkshire Hathaway name was truncated in the displayed dataset output.*

**Key Findings**

Compass led buyer-side participation among the displayed offices with 27,177 transactions, followed by Coldwell Banker Realty with 14,952.

Real Broker recorded 6,161 buyer-side transactions compared with 4,719 listing-side transactions, indicating greater observed participation on the buyer side in these summaries.

Intero Real Estate Services had a median buyer-side closing price of $1.335 million and a median PPSF of $816.26, consistent with relatively high-priced transaction exposure.

The `NONMEMBER MRML` category recorded 8,834 buyer-side transactions but should not automatically be treated as a conventional brokerage company.

**Brokerage Name Standardization**

The dataset contains inconsistent brokerage naming conventions. For example, `eXp Realty of California Inc` and `eXp Realty of California, Inc.` appear as separate categories.

Future competitive intelligence analysis should standardize verified company identities before calculating combined market participation or brokerage rankings.

## 7. Overall Market Insights

The segmented analysis reveals several important patterns.

**1. Property characteristics influence housing prices and market durations.** Single-family residences dominate transaction volume, while condominiums have a slightly higher median price per square foot.

**2. Geographic location is a major source of price variation.** San Mateo and Santa Clara lead the reported county comparisons in median home prices, while Inland Empire MLS areas generally show lower median prices.

**3. Market volume and property prices are not directly proportional.** Los Angeles County has considerably more transaction records than San Mateo County but a lower median closing price.

**4. Brokerage participation differs by transaction side.** Compass and Coldwell Banker Realty have substantial representation on both sides, while several other brokerages show differences between listing-side and buyer-side transaction counts.

**5. Data standardization remains important.** Unspecified MLS areas, inconsistent office names, and unusual transaction metrics can influence segmented comparisons.

## 8. Data Quality and Limitations

The analysis followed a flag-based data quality approach to preserve original property observations.

Previously validated numerical fields were used where available, and the analysis excluded invalid closing prices from grouped transaction summaries.

Nevertheless, several limitations remain:

- Negative and unusually high Days on Market values occur in the raw data.
- Extreme PriceRatio and PPSF observations require further investigation.
- Some contract-to-close intervals are unusually long.
- Nonidentical records with duplicate ListingKey values may remain.
- Brokerage names have not been comprehensively standardized.
- Results describe observed market differences and should not be interpreted as causal effects.

The current segmented summaries should therefore be considered exploratory analysis rather than final production-level market benchmarks.

## 9. Conclusion

Week 6 successfully developed a range of market indicators and performed segmented analysis across residential property types, counties, MLS areas, and real estate brokerage offices.

The findings indicate substantial differences in housing prices, transaction activity, market exposure, and brokerage participation across California residential markets.

In particular, San Mateo and Santa Clara exhibited relatively high median closing prices, single-family residences dominated residential transaction volume, and Compass recorded substantial listing-side and buyer-side transaction activity.

The engineered datasets and segmented summaries provide a foundation for subsequent Tableau dashboard development, geographic market comparisons, and more advanced real estate market analysis.
