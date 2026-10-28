#!/usr/bin/env python
# coding: utf-8

# In[2]:


from pathlib import Path
from datetime import date
import io
import re
import pandas as pd
import requests

DATA_DIR = Path('/Users/yuki/csv')
OUTPUT_DIR = DATA_DIR / 'weeks2_3_output'


# In[3]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path

data_folder = Path("/Users/yuki/csv")

csv_files = sorted(data_folder.glob("CRMLSSold*.csv"))

print("Number of CSV files found:", len(csv_files))

if not csv_files:
    raise FileNotFoundError("No Sold CSV files found.")

dataframes = []

for file in csv_files:
    df = pd.read_csv(file, low_memory=False)
    df["SourceFile"] = file.name
    dataframes.append(df)

sold = pd.concat(dataframes, ignore_index=True)

print("Total rows:", sold.shape[0])
print("Total columns:", sold.shape[1])

display(sold.head())


# In[4]:


print("Records by source file:")
print(sold["SourceFile"].value_counts().sort_index())

if "ListingKey" in sold.columns:
    duplicate_count = sold.duplicated(
        subset=["ListingKey"], keep=False
    ).sum()

    print("\nRecords sharing a ListingKey:", duplicate_count)


# In[5]:


print("Number of rows:", sold.shape[0])
print("Number of columns:", sold.shape[1])

print("\nColumn names:")
print(sold.columns.tolist())

print("\nFirst five records:")
display(sold.head())

print("\nColumn data types:")
print(sold.dtypes.to_string())


# In[6]:


if "PropertyType" in sold.columns:
    print("Unique property types:")
    print(sold["PropertyType"].unique())

    print("\nProperty type counts:")
    print(sold["PropertyType"].value_counts(dropna=False))
else:
    print("PropertyType column not found.")

    print("\nAvailable property-related columns:")
    print([
        col for col in sold.columns
        if "property" in col.lower()
    ])


# In[7]:


if "PropertyType" in sold.columns:
    property_share = (
        sold["PropertyType"]
        .fillna("Missing")
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    print("Property type share (%):")
    display(property_share)


# In[8]:


if "PropertyType" not in sold.columns:
    raise KeyError(
        "PropertyType is missing. Residential filtering cannot proceed."
    )

residential_mask = (
    sold["PropertyType"]
    .astype("string")
    .str.strip()
    .str.lower()
    .eq("residential")
    .fillna(False)
)

residential = sold.loc[residential_mask].copy()

print("Original records:", len(sold))
print("Residential records:", len(residential))
print("Excluded records:", len(sold) - len(residential))


# In[9]:


missing_report = pd.DataFrame({
    "MissingCount": residential.isnull().sum(),
    "MissingPercent": residential.isnull().mean() * 100
})

missing_report = missing_report.sort_values(
    "MissingPercent", ascending=False
)

display(missing_report.round(2))


# In[10]:


missing_report["Above90Percent"] = (
    missing_report["MissingPercent"] > 90
)

high_missing = missing_report[
    missing_report["Above90Percent"]
]

print("Columns with more than 90% missing values:")
display(high_missing)


# In[11]:


market_fields = [
    "ClosePrice", "ListPrice", "OriginalListPrice",
    "LivingArea", "LotSizeAcres", "BedroomsTotal",
    "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt",
    "CloseDate", "ListingContractDate",
    "PropertyType", "PropertySubType",
    "CountyOrParish", "City"
]

metadata_fields = [
    "ListingKey", "ListingId", "ListingKeyNumeric",
    "ListAgentEmail", "ListAgentFirstName",
    "ListAgentLastName", "ListAgentFullName",
    "BuyerAgentFirstName", "BuyerAgentLastName",
    "ListOfficeName", "BuyerOfficeName",
    "SourceFile"
]

available_market = [
    col for col in market_fields
    if col in residential.columns
]

available_metadata = [
    col for col in metadata_fields
    if col in residential.columns
]

print("Market analysis fields:")
print(available_market)

print("\nMetadata fields:")
print(available_metadata)


# In[12]:


core_fields = [
    "ClosePrice", "ListPrice", "OriginalListPrice",
    "LivingArea", "LotSizeAcres", "BedroomsTotal",
    "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt",
    "CloseDate", "ListingContractDate",
    "PropertyType", "PropertySubType",
    "CountyOrParish", "City",
    "Latitude", "Longitude", "ListingKey"
]

missing_report["Decision"] = "Retain"

missing_report.loc[
    missing_report["Above90Percent"],
    "Decision"
] = "Review for removal"

missing_report.loc[
    missing_report.index.isin(core_fields),
    "Decision"
] = "Retain core field"

display(missing_report)


# In[13]:


#Review columns recommended for removal
columns_to_drop = missing_report[
    (missing_report["MissingPercent"] > 90) &
    (~missing_report.index.isin(core_fields))
].index.tolist()

print("Columns recommended for removal:")
for col in columns_to_drop:
    print(col)

print("\nTotal columns to remove:", len(columns_to_drop))

#Drop high-missing columns
residential_clean = residential.drop(
    columns=columns_to_drop
).copy()

print("Original shape:", residential.shape)
print("Cleaned shape:", residential_clean.shape)

print(
    "Columns removed:",
    residential.shape[1] - residential_clean.shape[1]
)

#Check missing values in key fields
key_fields = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "CloseDate",
    "ListingContractDate"
]

key_missing = pd.DataFrame({
    "MissingCount": residential_clean[key_fields].isnull().sum(),
    "MissingPercent": (
        residential_clean[key_fields].isnull().mean() * 100
    )
})

display(key_missing.round(2))


# In[14]:


#Part 3 — Numeric Distribution Review
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

numeric_columns = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt"
]

for col in numeric_columns:
    residential_clean[col] = pd.to_numeric(
        residential_clean[col],
        errors="coerce"
    )

print("Numeric data types:")
print(residential_clean[numeric_columns].dtypes)

#Generate percentile summaries
numeric_summary = residential_clean[
    numeric_columns
].describe(
    percentiles=[
        0.01, 0.05, 0.25, 0.50,
        0.75, 0.95, 0.99
    ]
).T

numeric_summary = numeric_summary.rename(
    columns={
        "50%": "Median",
        "mean": "Mean",
        "min": "Min",
        "max": "Max",
        "std": "StdDev"
    }
)

display(numeric_summary.round(2))




# In[15]:


#Generate histograms
for col in numeric_columns:
    data = residential_clean[col].dropna()

    upper_limit = data.quantile(0.99)
    lower_limit = data.quantile(0.01)

    plot_data = data[
        (data >= lower_limit) &
        (data <= upper_limit)
    ]

    plt.figure(figsize=(12, 6))

    sns.histplot(
        plot_data,
        bins=50,
        color="steelblue",
        edgecolor="white"
    )

    plt.title(f"Distribution of {col} (1st–99th Percentile)")
    plt.xlabel(col)
    plt.ylabel("Frequency")

    plt.tight_layout()
    plt.show()


# In[16]:


for col in numeric_columns:
    data = residential_clean[col].dropna()

    lower = data.quantile(0.01)
    upper = data.quantile(0.99)

    central_data = data[
        (data >= lower) &
        (data <= upper)
    ]

    fig, axes = plt.subplots(
        2, 1,
        figsize=(12, 5)
    )

    sns.boxplot(
        x=data,
        ax=axes[0],
        color="lightgray",
        showfliers=True,
        flierprops={
            "marker": ".",
            "markersize": 2,
            "alpha": 0.3
        }
    )

    axes[0].set_title(
        f"{col} - Full Distribution"
    )

    sns.boxplot(
        x=central_data,
        ax=axes[1],
        color="steelblue",
        showfliers=False
    )

    axes[1].set_title(
        f"{col} - Central 98% Distribution"
    )

    plt.tight_layout()
    plt.show()


# In[17]:


#Identify extreme outliers
outlier_results = []

for col in numeric_columns:
    data = residential_clean[col].dropna()

    if data.empty:
        continue

    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 3 * IQR
    upper_bound = Q3 + 3 * IQR

    outliers = data[
        (data < lower_bound) |
        (data > upper_bound)
    ]

    outlier_results.append({
        "Variable": col,
        "LowerBound": lower_bound,
        "UpperBound": upper_bound,
        "OutlierCount": len(outliers),
        "OutlierPercent": len(outliers) / len(data) * 100
    })

outlier_summary = pd.DataFrame(outlier_results)

display(outlier_summary.round(2))


# In[18]:


#Save required numeric distribution summary
required_columns = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket"
]

final_numeric_summary = numeric_summary.loc[
    required_columns
]

final_numeric_summary.to_csv(
    "/Users/yuki/csv/numeric_distribution_summary.csv",
    index_label="Variable"
)

print("Numeric distribution summary saved.")

#Save missing value report
missing_report.to_csv(
    "/Users/yuki/csv/missing_value_report.csv",
    index_label="Column"
)

print("Missing value report saved.")

#Save filtered dataset
residential_clean.to_csv(
    "/Users/yuki/csv/residential_filtered.csv",
    index=False
)

print("Filtered dataset saved.")
print("Final rows:", residential_clean.shape[0])
print("Final columns:", residential_clean.shape[1])


# In[19]:


residential_clean.to_csv(
    "/Users/yuki/csv/residential_filtered.csv",
    index=False
)

print("Filtered dataset saved.")
print("Final rows:", residential_clean.shape[0])
print("Final columns:", residential_clean.shape[1])


# In[ ]:




