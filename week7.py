#!/usr/bin/env python
# coding: utf-8

# In[1]:


# ============================================================
# WEEK 7 - OUTLIER DETECTION AND DATA QUALITY
# IDX Exchange - Data Analyst Internship
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path

folder = Path("/Users/yuki/csv/")

# Load Week 6 engineered datasets
listing = pd.read_csv(
    folder / "listing_week6_engineered.csv",
    low_memory=False
)

sold = pd.read_csv(
    folder / "sold_week6_engineered.csv",
    low_memory=False
)

datasets = {
    "Listing": listing,
    "Sold": sold
}

for name, df in datasets.items():
    print(f"{name}: {df.shape}")

print("\nData loaded successfully!")


# In[2]:


# ============================================================
# STEP 2: DEFINE IQR FUNCTION
# ============================================================

def calculate_iqr_bounds(series, multiplier=1.5):

    values = pd.to_numeric(
        series, errors="coerce"
    )

    values = values.replace(
        [np.inf, -np.inf], np.nan
    ).dropna()

    if values.empty:
        return np.nan, np.nan, np.nan, np.nan, np.nan

    Q1 = values.quantile(0.25)
    Q3 = values.quantile(0.75)

    IQR = Q3 - Q1

    lower = Q1 - multiplier * IQR
    upper = Q3 + multiplier * IQR

    return Q1, Q3, IQR, lower, upper


# In[3]:


# ============================================================
# STEP 3: CREATE OUTLIER FLAGS
# ============================================================

def detect_outliers(df, dataset_name):

    df = df.copy()

    # ----------------------------------------
    # 1. Select numeric fields
    # ----------------------------------------

    def get_numeric(clean_col, raw_col):

        col = clean_col if clean_col in df.columns else raw_col

        return pd.to_numeric(
            df[col], errors="coerce"
        ).replace([np.inf, -np.inf], np.nan)

    close = get_numeric(
        "ClosePrice_Clean", "ClosePrice"
    )

    area = get_numeric(
        "LivingArea_Clean", "LivingArea"
    )

    dom = get_numeric(
        "DaysOnMarket_Clean", "DaysOnMarket"
    )

    # Keep values used in Week 7 analysis
    df["ClosePrice_W7"] = close
    df["LivingArea_W7"] = area
    df["DaysOnMarket_W7"] = dom

    # ----------------------------------------
    # 2. Business Rule Flags
    # ----------------------------------------

    df["invalid_close_price_flag_w7"] = (
        close.notna() & (close <= 0)
    )

    df["invalid_living_area_flag_w7"] = (
        area.notna() & (area <= 0)
    )

    df["invalid_dom_flag_w7"] = (
        dom.notna() & (dom < 0)
    )

    # Detect values already masked during
    # previous cleaning stages
    for raw_col, value_col, flag_col in [
        ("ClosePrice", "ClosePrice_W7",
         "previously_masked_close_flag"),
        ("LivingArea", "LivingArea_W7",
         "previously_masked_area_flag"),
        ("DaysOnMarket", "DaysOnMarket_W7",
         "previously_masked_dom_flag")
    ]:

        raw = pd.to_numeric(
            df[raw_col], errors="coerce"
        )

        df[flag_col] = (
            raw.notna() &
            df[value_col].isna()
        )

    # ----------------------------------------
    # 3. Calculate IQR thresholds
    # ----------------------------------------

    metrics = {
        "ClosePrice": close.where(close > 0),
        "LivingArea": area.where(area > 0),
        "DaysOnMarket": dom.where(dom >= 0)
    }

    bounds = {}

    for metric, values in metrics.items():

        Q1, Q3, IQR, lower, upper = (
            calculate_iqr_bounds(values)
        )

        bounds[metric] = {
            "Q1": Q1,
            "Q3": Q3,
            "IQR": IQR,
            "Lower": lower,
            "Upper": upper
        }

    # ----------------------------------------
    # 4. IQR Outlier Flags
    # ----------------------------------------

    def make_iqr_flag(values, metric):

        lower = bounds[metric]["Lower"]
        upper = bounds[metric]["Upper"]

        if pd.isna(lower) or pd.isna(upper):
            return pd.Series(
                False, index=df.index
            )

        return (
            values.notna() &
            (
                (values < lower) |
                (values > upper)
            )
        )

    df["closeprice_iqr_flag"] = make_iqr_flag(
        metrics["ClosePrice"], "ClosePrice"
    )

    df["livingarea_iqr_flag"] = make_iqr_flag(
        metrics["LivingArea"], "LivingArea"
    )

    df["dom_iqr_flag"] = make_iqr_flag(
        metrics["DaysOnMarket"], "DaysOnMarket"
    )

    # ----------------------------------------
    # 5. Combined Flags
    # ----------------------------------------

    business_flags = [
        "invalid_close_price_flag_w7",
        "invalid_living_area_flag_w7",
        "invalid_dom_flag_w7",
        "previously_masked_close_flag",
        "previously_masked_area_flag",
        "previously_masked_dom_flag"
    ]

    iqr_flags = [
        "closeprice_iqr_flag",
        "livingarea_iqr_flag",
        "dom_iqr_flag"
    ]

    df["business_rule_issue_flag_w7"] = (
        df[business_flags].any(axis=1)
    )

    df["any_iqr_outlier_flag"] = (
        df[iqr_flags].any(axis=1)
    )

    df["any_outlier_flag"] = (
        df["business_rule_issue_flag_w7"] |
        df["any_iqr_outlier_flag"]
    )

    # Missing closing prices are expected
    # in some Listing records.
    # Sold records need valid closing prices.

    df["missing_required_close_flag"] = (
        (dataset_name == "Sold") &
        close.isna()
    )

    # Final filter decision
    df["exclude_from_analysis_flag"] = (
        df["any_outlier_flag"] |
        df["missing_required_close_flag"]
    )

    return df, bounds


# Apply to both datasets

listing_flagged, listing_bounds = detect_outliers(
    listing, "Listing"
)

sold_flagged, sold_bounds = detect_outliers(
    sold, "Sold"
)

print("Listing:", listing_flagged.shape)
print("Sold:", sold_flagged.shape)

print("\nOutlier flags created successfully!")


# In[4]:


# ============================================================
# STEP 4: IQR THRESHOLD SUMMARY
# ============================================================

threshold_results = []

for name, bounds in [
    ("Listing", listing_bounds),
    ("Sold", sold_bounds)
]:

    for metric, values in bounds.items():

        threshold_results.append({
            "Dataset": name,
            "Metric": metric,
            "Q1": values["Q1"],
            "Q3": values["Q3"],
            "IQR": values["IQR"],
            "Lower_Bound": values["Lower"],
            "Upper_Bound": values["Upper"]
        })

iqr_threshold_summary = pd.DataFrame(
    threshold_results
)

display(
    iqr_threshold_summary.round(2)
)


# In[5]:


# ============================================================
# STEP 5: OUTLIER FLAG SUMMARY
# ============================================================

flag_columns = [
    "invalid_close_price_flag_w7",
    "invalid_living_area_flag_w7",
    "invalid_dom_flag_w7",
    "previously_masked_close_flag",
    "previously_masked_area_flag",
    "previously_masked_dom_flag",
    "closeprice_iqr_flag",
    "livingarea_iqr_flag",
    "dom_iqr_flag",
    "business_rule_issue_flag_w7",
    "any_iqr_outlier_flag",
    "any_outlier_flag",
    "missing_required_close_flag",
    "exclude_from_analysis_flag"
]

flag_results = []

for name, df in [
    ("Listing", listing_flagged),
    ("Sold", sold_flagged)
]:

    for col in flag_columns:

        flag_results.append({
            "Dataset": name,
            "Flag": col,
            "Flagged_Rows": int(df[col].sum()),
            "Percentage": round(
                df[col].mean() * 100, 3
            )
        })

outlier_flag_summary = pd.DataFrame(
    flag_results
)

display(outlier_flag_summary)


# In[6]:


# ============================================================
# STEP 6: CREATE FILTERED DATASETS
# ============================================================

listing_filtered = listing_flagged.loc[
    ~listing_flagged["exclude_from_analysis_flag"]
].copy()

sold_filtered = sold_flagged.loc[
    ~sold_flagged["exclude_from_analysis_flag"]
].copy()

print("=== LISTING ===")
print("Before:", len(listing_flagged))
print("After:", len(listing_filtered))
print(
    "Excluded:",
    len(listing_flagged) - len(listing_filtered)
)

print("\n=== SOLD ===")
print("Before:", len(sold_flagged))
print("After:", len(sold_filtered))
print(
    "Excluded:",
    len(sold_flagged) - len(sold_filtered)
)


# In[7]:


# ============================================================
# STEP 7: BEFORE VS AFTER COMPARISON
# ============================================================

def compare_before_after(
    original, filtered, dataset_name
):

    metrics = [
        "ClosePrice_W7",
        "LivingArea_W7",
        "DaysOnMarket_W7"
    ]

    results = []

    for metric in metrics:

        before = pd.to_numeric(
            original[metric], errors="coerce"
        )

        after = pd.to_numeric(
            filtered[metric], errors="coerce"
        )

        results.append({
            "Dataset": dataset_name,
            "Metric": metric,
            "Before_Median": before.median(),
            "After_Median": after.median(),
            "Median_Change": (
                after.median() - before.median()
            ),
            "Before_Valid_Count": before.notna().sum(),
            "After_Valid_Count": after.notna().sum()
        })

    return pd.DataFrame(results)


listing_comparison = compare_before_after(
    listing_flagged,
    listing_filtered,
    "Listing"
)

sold_comparison = compare_before_after(
    sold_flagged,
    sold_filtered,
    "Sold"
)

median_comparison = pd.concat(
    [listing_comparison, sold_comparison],
    ignore_index=True
)

print("=== MEDIAN COMPARISON ===")

display(median_comparison.round(2))

# ============================================================
# DATASET SIZE COMPARISON
# ============================================================

size_results = []

for name, full, filtered in [
    ("Listing", listing_flagged, listing_filtered),
    ("Sold", sold_flagged, sold_filtered)
]:

    before = len(full)
    after = len(filtered)

    excluded = before - after

    size_results.append({
        "Dataset": name,
        "Before_Rows": before,
        "After_Rows": after,
        "Excluded_Rows": excluded,
        "Excluded_Percentage": round(
            excluded / before * 100, 2
        )
    })

size_comparison = pd.DataFrame(size_results)

display(size_comparison)


# In[8]:


# ============================================================
# STEP 8: PERCENTILE ANALYSIS
# ============================================================

percentiles = [
    0.01, 0.05, 0.25,
    0.50, 0.75, 0.95, 0.99
]

percentile_results = []

for name, df in [
    ("Listing", listing_flagged),
    ("Sold", sold_flagged)
]:

    for metric in [
        "ClosePrice_W7",
        "LivingArea_W7",
        "DaysOnMarket_W7"
    ]:

        values = pd.to_numeric(
            df[metric], errors="coerce"
        )

        # Exclude business-rule-invalid values
        if metric == "DaysOnMarket_W7":
            values = values.where(values >= 0)
        else:
            values = values.where(values > 0)

        result = values.quantile(percentiles)

        row = {
            "Dataset": name,
            "Metric": metric
        }

        for p, value in result.items():

            key = f"P{int(round(p * 100))}"

            row[key] = value

        percentile_results.append(row)

percentile_summary = pd.DataFrame(
    percentile_results
)

display(percentile_summary.round(2))


# In[9]:


# ============================================================
# STEP 9: FINAL VALIDATION
# ============================================================

for name, original, flagged, filtered in [
    ("Listing", listing, listing_flagged, listing_filtered),
    ("Sold", sold, sold_flagged, sold_filtered)
]:

    # Flagged dataset preserves all input records
    assert len(original) == len(flagged)

    # Original columns remain available
    assert set(original.columns).issubset(
        set(flagged.columns)
    )

    # Filtered dataset contains no excluded records
    assert not filtered[
        "exclude_from_analysis_flag"
    ].any()

    # All key outlier flags exist
    for col in [
        "closeprice_iqr_flag",
        "livingarea_iqr_flag",
        "dom_iqr_flag",
        "any_outlier_flag"
    ]:

        assert col in flagged.columns

        assert pd.api.types.is_bool_dtype(
            flagged[col]
        )

    print(f"{name}: Validation passed!")

print("\nAll Week 7 validations passed!")


# In[10]:


# ============================================================
# STEP 10: EXPORT
# ============================================================

# Full flagged datasets
listing_flagged.to_csv(
    folder / "listing_week7_flagged.csv",
    index=False
)

sold_flagged.to_csv(
    folder / "sold_week7_flagged.csv",
    index=False
)

# Clean filtered datasets
listing_filtered.to_csv(
    folder / "listing_week7_filtered.csv",
    index=False
)

sold_filtered.to_csv(
    folder / "sold_week7_filtered.csv",
    index=False
)

# Statistical reports
iqr_threshold_summary.to_csv(
    folder / "week7_iqr_thresholds.csv",
    index=False
)

outlier_flag_summary.to_csv(
    folder / "week7_outlier_flag_summary.csv",
    index=False
)

size_comparison.to_csv(
    folder / "week7_size_comparison.csv",
    index=False
)

median_comparison.to_csv(
    folder / "week7_median_comparison.csv",
    index=False
)

percentile_summary.to_csv(
    folder / "week7_percentile_summary.csv",
    index=False
)

print("=== WEEK 7 EXPORT COMPLETE ===")

print("All flagged and filtered datasets saved.")
print("All comparison reports saved.")
print("Output folder:", folder)


# In[ ]:




