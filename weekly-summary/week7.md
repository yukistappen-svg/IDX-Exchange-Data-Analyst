# Week 7 — Outlier Detection and Data Quality
**IDX Exchange | Data Analyst Internship**

**Dataset:** CRMLS Residential Listing and Sold Data (January 2024 – April 2026)

## 1. Objective

The objective of Week 7 was to improve the reliability of residential real estate market analysis by systematically identifying extreme values in key numerical variables.

The Interquartile Range (IQR) method was applied to three variables: ClosePrice, LivingArea, and DaysOnMarket. Statistical outlier detection was combined with business-rule validation to distinguish potentially unusual observations from previously identified data quality issues.

Rather than permanently deleting outliers, the workflow created dedicated flag columns and generated separate filtered datasets. This approach preserves the original records while providing alternative analytical samples for evaluating typical residential market conditions.

## 2. Methodology

### 2.1 Interquartile Range (IQR)

The IQR method identifies observations outside the central range of a numerical distribution.

The first quartile (Q1) represents the 25th percentile, while the third quartile (Q3) represents the 75th percentile.

The IQR and filtering boundaries were calculated as follows:

\[
IQR=Q3-Q1
\]

\[
LowerBound=Q1-1.5\times IQR
\]

\[
UpperBound=Q3+1.5\times IQR
\]

Observations outside these boundaries were flagged as statistical outliers.

IQR thresholds were calculated independently for the Listing and Sold datasets using the corresponding valid numerical values.

### 2.2 Business Rules and Outlier Flags

In addition to statistical outlier detection, business rules were used to identify invalid numerical observations.

| Variable | Business Rule | Statistical Method |
|---|---|---|
| ClosePrice | Nonpositive prices are invalid | 1.5 × IQR |
| LivingArea | Nonpositive living areas are invalid | 1.5 × IQR |
| DaysOnMarket | Negative market durations are invalid | 1.5 × IQR |

The analysis also retained flags identifying observations whose values had previously been masked during earlier cleaning stages.

Three main statistical flags were created:

- `closeprice_iqr_flag`
- `livingarea_iqr_flag`
- `dom_iqr_flag`

A combined `exclude_from_analysis_flag` was used to construct the filtered datasets.

An observation was excluded from the filtered sample if it met at least one applicable exclusion criterion. Missing required closing prices were also excluded from the Sold analytical dataset.

Importantly, statistical outliers were treated as potentially unusual observations, not automatically as incorrect records.

## 3. IQR Threshold Results

The calculated IQR boundaries are summarized below.

| Dataset | Metric | Q1 | Q3 | IQR | Lower Bound | Upper Bound |
|---|---|---:|---:|---:|---:|---:|
| Listing | ClosePrice ($) | 600,000 | 1,350,000 | 750,000 | -525,000 | 2,475,000 |
| Listing | LivingArea (sqft) | 1,248 | 2,300 | 1,052 | -330 | 3,878 |
| Listing | DaysOnMarket | 5 | 21 | 16 | -19 | 45 |
| Sold | ClosePrice ($) | 575,000 | 1,300,000 | 725,000 | -512,500 | 2,387,500 |
| Sold | LivingArea (sqft) | 1,248 | 2,219 | 971 | -208.5 | 3,675.5 |
| Sold | DaysOnMarket | 8 | 48 | 40 | -52 | 108 |

The IQR results indicate that residential prices, living areas, and market durations have relatively wide upper tails.

For example, Sold properties with closing prices above $2,387,500 were flagged as statistical price outliers, while properties with living areas exceeding 3,675.5 square feet were flagged as area outliers.

The IQR upper boundary for DaysOnMarket was 45 days for Listing records and 108 days for Sold records. This difference reflects variation in the distributions of the two datasets.

Negative lower boundaries were produced mathematically by the IQR formula. Such values were not interpreted as valid negative prices or physical measurements; business-rule checks addressed invalid observations separately.

## 4. Outlier Detection Results

### 4.1 Statistical Outlier Counts

| Outlier Category | Listing Records | Listing (%) | Sold Records | Sold (%) |
|---|---:|---:|---:|---:|
| ClosePrice IQR Outliers | 9,925 | 1.815% | 30,708 | 7.418% |
| LivingArea IQR Outliers | 26,801 | 4.900% | 18,166 | 4.388% |
| DaysOnMarket IQR Outliers | 48,697 | 8.903% | 31,730 | 7.665% |
| **Any IQR Outlier** | **78,551** | **14.361%** | **64,929** | **15.685%** |

Among Listing records, DaysOnMarket generated the largest number of statistical outlier flags, with 48,697 observations.

Among Sold records, DaysOnMarket and ClosePrice were the largest contributors, flagging 31,730 and 30,708 observations, respectively.

Individual category counts overlap because a single property record may be flagged for more than one variable. Therefore, the combined outlier count is smaller than the sum of the individual counts.

### 4.2 Previously Masked Values

The workflow also detected values masked during previous data cleaning operations.

| Previously Masked Variable | Listing | Sold |
|---|---:|---:|
| ClosePrice | 5 | 14 |
| LivingArea | 428 | 166 |
| DaysOnMarket | 28 | 91 |
| **Total Flag Occurrences** | **461** | **271** |

These counts represent flag occurrences rather than necessarily distinct records.

The current business-rule checks identified no additional nonpositive ClosePrice, nonpositive LivingArea, or negative DaysOnMarket values in the selected Week 7 numerical fields. This is consistent with the earlier cleaning stages, in which some problematic values had already been converted to missing values.

## 5. Dataset Size Comparison

Following application of the combined outlier and data quality flags, separate filtered datasets were generated.

| Dataset | Before Filtering | After Filtering | Excluded Records | Excluded (%) |
|---|---:|---:|---:|---:|
| Listing | 546,962 | 468,035 | 78,927 | 14.43% |
| Sold | 413,951 | 348,846 | 65,105 | 15.73% |

The filtering procedure excluded 78,927 Listing records and 65,105 Sold records.

The resulting analytical datasets retained approximately 85.57% of Listing observations and 84.27% of Sold observations.

These exclusions were performed only in the separate filtered datasets. The full flagged datasets preserved all input observations.

## 6. Median Value Comparison

To evaluate how outlier filtering affected market statistics, median values were compared before and after filtering.

| Dataset | Metric | Before Filtering | After Filtering | Change |
|---|---|---:|---:|---:|
| Listing | Median ClosePrice | $850,000 | $825,000 | -$25,000 |
| Listing | Median LivingArea | 1,670 sqft | 1,612 sqft | -58 sqft |
| Listing | Median DaysOnMarket | 10 days | 9 days | -1 day |
| Sold | Median ClosePrice | $822,150 | $785,000 | -$37,150 |
| Sold | Median LivingArea | 1,643 sqft | 1,569 sqft | -74 sqft |
| Sold | Median DaysOnMarket | 18 days | 16 days | -2 days |

### 6.1 Impact on Closing Prices

The median closing price decreased by approximately 2.94% in the Listing dataset, from $850,000 to $825,000.

For the Sold dataset, the median closing price decreased by approximately 4.52%, from $822,150 to $785,000.

The larger decrease in the Sold dataset indicates that the combined filtering criteria had a more pronounced impact on its observed median closing price.

Because some high-value residential properties exceed the global IQR upper boundaries, the filtered sample contains fewer high-priced transactions.

The Listing price comparison refers only to observations with available closing prices and does not represent the median asking price of all listings.

### 6.2 Impact on Living Area

Median LivingArea decreased from 1,670 to 1,612 square feet for Listing records and from 1,643 to 1,569 square feet for Sold records.

These changes are consistent with the exclusion of some larger properties under the IQR filtering procedure.

### 6.3 Impact on Days on Market

Median DaysOnMarket decreased from 10 to 9 days for Listing records and from 18 to 16 days for Sold records.

This result suggests that the filtered samples contain fewer long-duration listings.

However, removing high-DOM observations can make market conditions appear more active than they are in the complete dataset.

Therefore, the filtered DOM distribution should not be used as the sole representation of market liquidity.

## 7. Key Findings

### Finding 1: Statistical outliers represent a substantial share of the data.

Approximately 14%–16% of observations were excluded under the combined IQR and data quality criteria.

This demonstrates that extreme values have a meaningful influence on the composition of the analytical datasets.

### Finding 2: Filtering reduces observed median closing prices.

Both datasets exhibited lower median closing prices after filtering.

The Sold dataset experienced a decrease of $37,150, while the Listing dataset experienced a decrease of $25,000.

This highlights the importance of documenting sample-selection rules when reporting housing market statistics.

### Finding 3: Large properties and long-duration listings affect the analytical sample.

The filtered datasets exhibited lower median living areas and shorter median market durations.

These findings indicate that the IQR procedure changes the types of properties represented in the analytical samples.

### Finding 4: Statistical outliers are not necessarily data errors.

A luxury property with a closing price above $2.4 million or a living area above 4,000 square feet may represent a legitimate residential transaction.

Similarly, a property remaining on the market for more than 108 days may reflect actual market conditions rather than a recording error.

Consequently, IQR flags should not be interpreted as proof of invalid data.

### Finding 5: Preserving flagged datasets improves analytical transparency.

Maintaining full flagged datasets alongside filtered samples allows future analysis to investigate outliers and compare alternative filtering strategies without losing original observations.

## 8. Limitations and Further Improvements

The analysis has several important limitations.

**Global IQR Thresholds:** The thresholds were calculated across each entire dataset rather than separately by county or property subtype. Housing prices and property sizes vary considerably across California markets, so legitimate properties in higher-priced regions may be disproportionately excluded.

**Potential Selection Bias:** Excluding observations whenever any one variable exceeds an IQR threshold can change the geographic, price, and property-type composition of the analytical sample.

**Previously Cleaned Data:** The Week 7 analysis was performed on datasets that had already undergone earlier data cleaning. Therefore, the before-filtering statistics represent the previously prepared data rather than completely untouched raw MLS records.

**Missing Values:** Some numerical fields remain missing. In particular, many Listing observations do not contain closing prices. Such missing values were not uniformly treated as outliers.

**Statistical Detection vs. Data Validation:** IQR identifies unusual observations based on distributional characteristics. Confirming whether a flagged value is erroneous would require additional validation against original MLS records and transaction information.

Future work could compare global IQR filtering with county-level or property-subtype-specific thresholds to reduce the potential exclusion of valid luxury and large-property transactions.

## 9. Deliverables

The Week 7 workflow produced or prepared the following outputs:

| Deliverable | Description |
|---|---|
| `Week7_Outlier_Detection.py` | Reproducible Python script for IQR detection and filtering |
| `listing_week7_flagged.csv` | Complete Listing dataset with outlier flags |
| `sold_week7_flagged.csv` | Complete Sold dataset with outlier flags |
| `listing_week7_filtered.csv` | Filtered Listing analytical dataset |
| `sold_week7_filtered.csv` | Filtered Sold analytical dataset |
| `week7_iqr_thresholds.csv` | IQR quartiles and filtering boundaries |
| `week7_outlier_flag_summary.csv` | Outlier counts and percentages |
| `week7_size_comparison.csv` | Dataset sizes before and after filtering |
| `week7_median_comparison.csv` | Median statistics before and after filtering |
| `week7_percentile_summary.csv` | Supporting percentile distribution analysis |

## 10. Conclusion

Week 7 successfully implemented a systematic outlier detection and data quality workflow using the Interquartile Range method.

The analysis identified statistical outliers in residential closing prices, living areas, and days on market, while maintaining the original observations through dedicated flag columns.

The combined filtering criteria excluded 14.43% of Listing records and 15.73% of Sold records. After filtering, median closing prices, living areas, and market durations were lower in both datasets.

These results demonstrate that statistical filtering can materially affect the composition and summary statistics of real estate market datasets.

By preserving both full flagged datasets and separate filtered analytical datasets, the workflow supports reproducible analysis, transparent quality control, and future comparisons of alternative outlier-treatment strategies.
