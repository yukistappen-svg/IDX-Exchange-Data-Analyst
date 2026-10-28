#!/usr/bin/env python
# coding: utf-8

# In[30]:


import pandas as pd
import numpy as np

# Load the filtered residential dataset
sold = pd.read_csv(
    "/Users/yuki/csv/residential_filtered.csv",
    low_memory=False
)

# Check dataset dimensions
print("Rows:", sold.shape[0])
print("Columns:", sold.shape[1])

# Preview the dataset
sold.head()


# In[31]:


# Create a copy for cleaning
df = sold.copy()

# Columns required for Weeks 4-5
required_columns = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate",
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "Latitude",
    "Longitude"
]

# Check which columns exist
print("Available columns:")
print([col for col in required_columns if col in df.columns])

print("\nMissing columns:")
print([col for col in required_columns if col not in df.columns])


# In[32]:


date_cols = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate"
]

# Check original data types
print("Date columns before conversion:")
print(df[date_cols].dtypes)

# Preview original date values
display(df[date_cols].head(10))

# Record missing values before conversion
missing_before = df[date_cols].isna().sum()

# Convert date columns to datetime
for col in date_cols:
    df[col] = pd.to_datetime(
        df[col],
        errors="coerce"
    )

# Record missing values after conversion
missing_after = df[date_cols].isna().sum()

# Count newly invalid dates
invalid_dates = missing_after - missing_before

print("Date columns after conversion:")
print(df[date_cols].dtypes)

print("\nNewly invalid dates after conversion:")
print(invalid_dates)


# In[33]:


# Step 4: Remove unnecessary or redundant columns

columns_to_drop = [
    "source_csv_row",
    "ListingKeyNumeric",
    "StreetNumberNumeric",
    "ListAgentFirstName",
    "ListAgentLastName",
    "CoListAgentFirstName",
    "CoListAgentLastName",
    "BuyerAgentFirstName",
    "BuyerAgentLastName",
    "ListAgentEmail",
    "BuyerAgentMlsId",
    "BuyerAgencyCompensation",
    "BuyerAgencyCompensationType",
    "LotSizeDimensions",
    "BuyerOfficeAOR"
]

# Record column count before cleaning
cols_before = df.shape[1]

# Remove columns if they exist
df = df.drop(columns=columns_to_drop, errors="ignore")

# Check results
print("Columns before:", cols_before)
print("Columns after:", df.shape[1])
print("Columns removed:", cols_before - df.shape[1])


# In[34]:


# Confirm remaining dataset structure

print("Dataset shape:", df.shape)

print("\nRemaining columns:")
print(df.columns.tolist())

print("\nDuplicate rows:")
print(df.duplicated().sum())


# In[35]:


# Step 5.1: Missing Value Analysis

missing_summary = pd.DataFrame({
    "Missing Count": df.isnull().sum(),
    "Missing Percentage": (df.isnull().sum() / len(df) * 100).round(2)
})

# Sort by missing percentage
missing_summary = missing_summary.sort_values(
    by="Missing Percentage",
    ascending=False
)

# Display columns with missing values
display(missing_summary[missing_summary["Missing Count"] > 0])


# In[36]:


# Step 5.3: Remove high-missingness columns

high_missing_cols = [
    "OriginatingSystemName",
    "OriginatingSystemSubName",
    "ElementarySchool",
    "MiddleOrJuniorSchool",
    "HighSchool",
    "latfilled",
    "lonfilled",
    "CoListOfficeName",
    "SubdivisionName"
]

# Only remove columns that exist
cols_to_remove = [
    col for col in high_missing_cols
    if col in df.columns
]

cols_before = df.shape[1]

df = df.drop(columns=cols_to_remove)

print("Columns before:", cols_before)
print("Columns after:", df.shape[1])
print("Columns removed:", len(cols_to_remove))

print("\nRemoved columns:")
print(cols_to_remove)


# In[37]:


# Step 5.4: Standardize missing text values

text_cols = df.select_dtypes(
    include=["object", "string"]
).columns

for col in text_cols:
    df[col] = df[col].astype("string").str.strip()

    df[col] = df[col].replace(
        ["", "N/A", "NA", "NULL", "null", "None"],
        pd.NA
    )

print("Missing values standardized successfully.")


# In[38]:


# Step 6.1: Convert numeric columns

numeric_cols = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "LotSizeArea",
    "LotSizeSquareFeet",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "Latitude",
    "Longitude",
    "ParkingTotal",
    "GarageSpaces",
    "Stories",
    "MainLevelBedrooms",
    "AssociationFee"
]

# Keep only columns that exist
numeric_cols = [col for col in numeric_cols if col in df.columns]

# Check data types before conversion
print("Before conversion:")
print(df[numeric_cols].dtypes)

# Convert to numeric
conversion_issues = {}

for col in numeric_cols:
    original = df[col]
    converted = pd.to_numeric(original, errors="coerce")

    conversion_issues[col] = (
        original.notna() & converted.isna()
    ).sum()

    df[col] = converted

print("\nAfter conversion:")
print(df[numeric_cols].dtypes)

print("\nValues that failed numeric conversion:")
print(pd.Series(conversion_issues))


# In[39]:


# Step 6.2: Flag invalid numeric values

df["invalid_close_price_flag"] = df["ClosePrice"] <= 0

df["invalid_living_area_flag"] = df["LivingArea"] <= 0

df["negative_dom_flag"] = df["DaysOnMarket"] < 0

df["negative_bedrooms_flag"] = df["BedroomsTotal"] < 0

df["negative_bathrooms_flag"] = df["BathroomsTotalInteger"] < 0

# Combine all numeric quality flags
numeric_flags = [
    "invalid_close_price_flag",
    "invalid_living_area_flag",
    "negative_dom_flag",
    "negative_bedrooms_flag",
    "negative_bathrooms_flag"
]

df[numeric_flags] = df[numeric_flags].fillna(False)

df["invalid_numeric_flag"] = df[numeric_flags].any(axis=1)

# Display flag counts
print("Invalid Numeric Value Summary:")
print(df[numeric_flags].sum())

print("\nTotal records with invalid numeric values:")
print(df["invalid_numeric_flag"].sum())


# In[40]:


# Step 6.3: Calculate invalid numeric record percentage

total_rows = len(df)
invalid_rows = df["invalid_numeric_flag"].sum()

invalid_pct = invalid_rows / total_rows * 100

print(f"Total records: {total_rows:,}")
print(f"Invalid numeric records: {invalid_rows:,}")
print(f"Invalid percentage: {invalid_pct:.2f}%")


# In[41]:


# Step 7.1: Date Consistency Checks

# 1. Listing date occurs after closing date
df["listing_after_close_flag"] = (
    df["ListingContractDate"] > df["CloseDate"]
)

# 2. Purchase contract date occurs after closing date
df["purchase_after_close_flag"] = (
    df["PurchaseContractDate"] > df["CloseDate"]
)

# 3. Listing date occurs after purchase contract date
df["negative_timeline_flag"] = (
    df["ListingContractDate"] > df["PurchaseContractDate"]
)

# Combine all date flags
date_flags = [
    "listing_after_close_flag",
    "purchase_after_close_flag",
    "negative_timeline_flag"
]

df["invalid_date_flag"] = df[date_flags].any(axis=1)

# Display summary
print("Date Consistency Summary:")
print(df[date_flags].sum())

print("\nTotal records with date inconsistencies:")
print(df["invalid_date_flag"].sum())


# In[42]:


# Step 7.2: Calculate date inconsistency percentages

date_summary = pd.DataFrame({
    "Invalid Count": df[date_flags].sum(),
    "Percentage (%)": (
        df[date_flags].sum() / len(df) * 100
    ).round(3)
})

display(date_summary)

print(
    "\nOverall date inconsistency rate:",
    f"{df['invalid_date_flag'].mean() * 100:.3f}%"
)


# In[43]:


# Step 8.1: Geographic Data Quality Checks

lat = df["Latitude"]
lon = df["Longitude"]

# 1. Missing coordinates
df["missing_coordinates_flag"] = (
    lat.isna() | lon.isna()
)

# 2. Zero coordinates
df["zero_coordinates_flag"] = (
    (lat == 0) | (lon == 0)
)

# 3. Positive longitude
df["positive_longitude_flag"] = (
    lon > 0
)

# 4. Coordinates outside California bounding box
df["out_of_state_coordinates_flag"] = (
    lat.notna()
    & lon.notna()
    & ~df["zero_coordinates_flag"]
    & ~df["positive_longitude_flag"]
    & (
        ~lat.between(32.5, 42.1)
        | ~lon.between(-124.5, -114.0)
    )
)

# Combine geographic flags
geo_flags = [
    "missing_coordinates_flag",
    "zero_coordinates_flag",
    "positive_longitude_flag",
    "out_of_state_coordinates_flag"
]

df["invalid_geographic_flag"] = df[geo_flags].any(axis=1)

print("Geographic Data Quality Summary:")
print(df[geo_flags].sum())

print("\nTotal records with geographic issues:")
print(df["invalid_geographic_flag"].sum())


# In[44]:


# Step 8.2: Geographic Data Quality Summary

geo_summary = pd.DataFrame({
    "Invalid Count": df[geo_flags].sum(),
    "Percentage (%)": (
        df[geo_flags].sum() / len(df) * 100
    ).round(3)
})

display(geo_summary)

print(
    "\nOverall geographic issue rate:",
    f"{df['invalid_geographic_flag'].mean() * 100:.3f}%"
)


# In[45]:


# Step 8.3: Check state distribution

print("State distribution:")
print(df["StateOrProvince"].value_counts(dropna=False).head(20))


# In[46]:


# Step 9.1: Flag non-California records

df["non_ca_state_flag"] = (
    df["StateOrProvince"].str.upper() != "CA"
).fillna(False)

print("Non-California records:")
print(df["non_ca_state_flag"].sum())

# Inspect records
display(
    df.loc[
        df["non_ca_state_flag"],
        [
            "StateOrProvince",
            "City",
            "CountyOrParish",
            "Latitude",
            "Longitude",
            "ClosePrice"
        ]
    ]
)


# In[47]:


# Step 9.2: Compare state and coordinate flags

print("Non-CA records:", df["non_ca_state_flag"].sum())

print(
    "Non-CA records with geographic issues:",
    (
        df["non_ca_state_flag"]
        & df["invalid_geographic_flag"]
    ).sum()
)

print(
    "Non-CA records without geographic issues:",
    (
        df["non_ca_state_flag"]
        & ~df["invalid_geographic_flag"]
    ).sum()
)


# In[48]:


# Step 9.3: Update geographic quality flags

# Flag records whose state is not California
df["non_ca_state_flag"] = (
    df["StateOrProvince"].str.upper().ne("CA")
).fillna(False)

# Update overall geographic issue flag
df["invalid_geographic_flag"] = (
    df[
        [
            "missing_coordinates_flag",
            "zero_coordinates_flag",
            "positive_longitude_flag",
            "out_of_state_coordinates_flag",
            "non_ca_state_flag"
        ]
    ].any(axis=1)
)

print("Updated Geographic Data Quality Summary:")
print(
    df[
        [
            "missing_coordinates_flag",
            "zero_coordinates_flag",
            "positive_longitude_flag",
            "out_of_state_coordinates_flag",
            "non_ca_state_flag"
        ]
    ].sum()
)

print("\nTotal unique geographic issue records:")
print(df["invalid_geographic_flag"].sum())


# In[49]:


# Step 10.1: Check duplicate records

print("Exact duplicate rows:")
print(df.duplicated().sum())

print("\nDuplicate ListingKey values:")
print(df.duplicated(subset=["ListingKey"]).sum())

# Display duplicate ListingKeys
duplicate_listings = df[
    df.duplicated(subset=["ListingKey"], keep=False)
]

display(
    duplicate_listings[
        [
            "ListingKey",
            "ListingId",
            "CloseDate",
            "ClosePrice",
            "City"
        ]
    ].head(20)
)

# Step 10.2: Remove exact duplicates

rows_before = len(df)

df = df.drop_duplicates().copy()

print("Rows before:", rows_before)
print("Rows after:", len(df))
print("Rows removed:", rows_before - len(df))


# In[ ]:





# In[ ]:





# In[50]:


# Step 10.3: Investigate duplicate ListingKeys

duplicate_keys = df[
    df.duplicated(subset=["ListingKey"], keep=False)
].copy()

# Summarize repeated listings
duplicate_summary = (
    duplicate_keys
    .groupby("ListingKey")
    .agg(
        record_count=("ListingKey", "size"),
        unique_close_dates=("CloseDate", "nunique"),
        unique_close_prices=("ClosePrice", "nunique"),
        unique_listing_ids=("ListingId", "nunique")
    )
    .reset_index()
)

print("Duplicate ListingKey groups:", len(duplicate_summary))

print(
    "\nGroups with different close dates:",
    (duplicate_summary["unique_close_dates"] > 1).sum()
)

print(
    "\nGroups with different close prices:",
    (duplicate_summary["unique_close_prices"] > 1).sum()
)

print(
    "\nGroups with different ListingIds:",
    (duplicate_summary["unique_listing_ids"] > 1).sum()
)

display(duplicate_summary.head(20))


# In[51]:


# Step 10.4: Flag duplicate ListingKeys

df["duplicate_listing_flag"] = (
    df.duplicated(subset=["ListingKey"], keep=False)
    & df["ListingKey"].notna()
)

# Check results
print("Records with duplicate ListingKeys:")
print(df["duplicate_listing_flag"].sum())

print("\nUnique duplicated ListingKeys:")
print(
    df.loc[
        df["duplicate_listing_flag"],
        "ListingKey"
    ].nunique()
)

print("\nFinal dataset shape:")
print(df.shape)


# In[52]:


# Step 11.1: Create Overall Data Quality Flag

# Combine all data quality issues
df["data_quality_issue_flag"] = (
    df["invalid_numeric_flag"]
    | df["invalid_date_flag"]
    | df["invalid_geographic_flag"]
    | df["duplicate_listing_flag"]
)

# Count records with any data quality issue
total_records = len(df)
flagged_records = df["data_quality_issue_flag"].sum()
clean_records = total_records - flagged_records

print("FINAL DATA QUALITY SUMMARY")
print("=" * 45)

print(f"Total records: {total_records:,}")
print(f"Records with quality issues: {flagged_records:,}")
print(f"Records without flagged issues: {clean_records:,}")

print(
    f"\nData quality issue rate: "
    f"{flagged_records / total_records * 100:.2f}%"
)


# In[53]:


# Step 11.2: Generate Data Quality Summary Table

quality_summary = pd.DataFrame({
    "Category": [
        "Invalid Numeric Values",
        "Date Inconsistencies",
        "Geographic Issues",
        "Duplicate Listings",
        "Any Data Quality Issue"
    ],
    "Flagged Records": [
        df["invalid_numeric_flag"].sum(),
        df["invalid_date_flag"].sum(),
        df["invalid_geographic_flag"].sum(),
        df["duplicate_listing_flag"].sum(),
        df["data_quality_issue_flag"].sum()
    ]
})

quality_summary["Percentage (%)"] = (
    quality_summary["Flagged Records"]
    / len(df) * 100
).round(3)

display(quality_summary)


# In[54]:


# Step 11.3: Confirm Final Data Types

check_cols = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate",
    "ClosePrice",
    "ListPrice",
    "LivingArea",
    "DaysOnMarket",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "Latitude",
    "Longitude"
]

print("FINAL DATA TYPE CONFIRMATION")
print("=" * 45)

print(df[check_cols].dtypes)

print("\nFinal dataset dimensions:")
print(df.shape)


# In[55]:


# Step 12.1: Export Cleaned Dataset

from pathlib import Path

# Define output directory
output_dir = Path("/Users/yuki/csv/weeks_4_5")
output_dir.mkdir(parents=True, exist_ok=True)

# Save cleaned dataset
output_file = output_dir / "sold_cleaned.csv"

df.to_csv(
    output_file,
    index=False,
    date_format="%Y-%m-%d"
)

print("Cleaned dataset saved successfully!")
print("File:", output_file)
print("Final rows:", len(df))
print("Final columns:", len(df.columns))


# In[56]:


# Step 12.2: Export Data Quality Report

report_file = output_dir / "data_quality_report.csv"

quality_summary.to_csv(
    report_file,
    index=False
)

print("Data Quality Report saved!")
print("File:", report_file)

display(quality_summary)


# In[57]:


# Step 12.3: Verify exported dataset

saved_df = pd.read_csv(
    output_file,
    low_memory=False
)

print("Export Verification")
print("=" * 40)

print("Original rows:", len(df))
print("Saved rows:", len(saved_df))

print("Original columns:", len(df.columns))
print("Saved columns:", len(saved_df.columns))

print("\nExport successful:",
      saved_df.shape == df.shape)


# In[ ]:




