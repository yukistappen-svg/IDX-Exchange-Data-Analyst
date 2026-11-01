#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from pathlib import Path

folder = Path("/Users/yuki/csv/")

# Load Week 4-5 flagged datasets
listing = pd.read_csv(
    folder / "listing_week45_flagged.csv",
    low_memory=False
)

sold = pd.read_csv(
    folder / "sold_week45_flagged.csv",
    low_memory=False
)

print("Listing:", listing.shape)
print("Sold:", sold.shape)

# Verify required columns
required_cols = [
    "ClosePrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket",
    "CloseDate",
    "ListingContractDate",
    "PurchaseContractDate",
    "PropertyType",
    "PropertySubType",
    "CountyOrParish",
    "MLSAreaMajor",
    "ListOfficeName",
    "BuyerOfficeName",
    "Latitude",
    "Longitude"
]

for name, df in [("Listing", listing), ("Sold", sold)]:
    missing = [c for c in required_cols if c not in df.columns]
    assert not missing, f"{name} missing columns: {missing}"

    assert df["PropertyType"].eq("Residential").all()

print("Input validation passed!")


# In[2]:


# ============================================================
# WEEK 6 - FEATURE ENGINEERING
# ============================================================

date_cols = [
    "CloseDate",
    "ListingContractDate",
    "PurchaseContractDate"
]

def engineer_features(df, dataset_name):

    df = df.copy()

    # ----------------------------------------
    # 1. Convert date fields
    # ----------------------------------------

    for col in date_cols:
        df[col] = pd.to_datetime(
            df[col],
            errors="coerce"
        )

    # ----------------------------------------
    # 2. Select cleaned numeric fields
    # ----------------------------------------

    def get_numeric(clean_col, raw_col):
        column = clean_col if clean_col in df.columns else raw_col
        return pd.to_numeric(df[column], errors="coerce")

    close_price = get_numeric("ClosePrice_Clean", "ClosePrice")
    original_price = get_numeric(
        "OriginalListPrice_Clean", "OriginalListPrice"
    )
    living_area = get_numeric("LivingArea_Clean", "LivingArea")
    dom_clean = get_numeric("DaysOnMarket_Clean", "DaysOnMarket")

    # ----------------------------------------
    # 3. Price Ratio
    # ClosePrice / OriginalListPrice
    # ----------------------------------------

    valid_price_ratio = (
        (close_price > 0) &
        (original_price > 0)
    )

    df["PriceRatio"] = (
        close_price.where(valid_price_ratio) /
        original_price.where(valid_price_ratio)
    )

    # Handbook uses the same formula
    df["CloseToOriginalListRatio"] = df["PriceRatio"]

    # ----------------------------------------
    # 4. Price per Square Foot
    # ----------------------------------------

    valid_ppsf = (
        (close_price > 0) &
        (living_area > 0)
    )

    df["PricePerSqFt"] = (
        close_price.where(valid_ppsf) /
        living_area.where(valid_ppsf)
    )

    # ----------------------------------------
    # 5. Days on Market
    # ----------------------------------------

    df["DaysOnMarket_Metric"] = pd.to_numeric(
        df["DaysOnMarket"], errors="coerce"
    )

    # Validated DOM for market analytics
    df["DaysOnMarket_Analysis"] = dom_clean.where(
        dom_clean.between(0, 730)
    )

    # ----------------------------------------
    # 6. Year / Month / YrMo
    # ----------------------------------------

    if dataset_name == "Sold":
        analysis_date = df["CloseDate"]
    else:
        analysis_date = df["ListingContractDate"]

    df["Year"] = analysis_date.dt.year
    df["Month"] = analysis_date.dt.month
    df["YrMo"] = analysis_date.dt.strftime("%Y-%m")

    # ----------------------------------------
    # 7. Listing to Contract Days
    # ----------------------------------------

    df["ListingToContractDays"] = (
        df["PurchaseContractDate"] -
        df["ListingContractDate"]
    ).dt.days

    # ----------------------------------------
    # 8. Contract to Close Days
    # ----------------------------------------

    df["ContractToCloseDays"] = (
        df["CloseDate"] -
        df["PurchaseContractDate"]
    ).dt.days

    # ----------------------------------------
    # 9. Flag invalid durations
    # ----------------------------------------

    df["invalid_listing_to_contract_flag"] = (
        df["ListingToContractDays"] < 0
    )

    df["invalid_contract_to_close_flag"] = (
        df["ContractToCloseDays"] < 0
    )

    # Do not use negative durations in statistics
    df.loc[
        df["invalid_listing_to_contract_flag"],
        "ListingToContractDays"
    ] = np.nan

    df.loc[
        df["invalid_contract_to_close_flag"],
        "ContractToCloseDays"
    ] = np.nan

    return df


# Apply to both datasets
listing_week6 = engineer_features(listing, "Listing")
sold_week6 = engineer_features(sold, "Sold")

print("Listing:", listing_week6.shape)
print("Sold:", sold_week6.shape)


# In[3]:


# ============================================================
# FEATURE VALIDATION
# ============================================================

new_metrics = [
    "PriceRatio",
    "CloseToOriginalListRatio",
    "PricePerSqFt",
    "DaysOnMarket_Metric",
    "DaysOnMarket_Analysis",
    "Year",
    "Month",
    "YrMo",
    "ListingToContractDays",
    "ContractToCloseDays"
]

for name, df in [
    ("Listing", listing_week6),
    ("Sold", sold_week6)
]:

    print(f"\n=== {name.upper()} FEATURE VALIDATION ===")

    display(df[new_metrics].head(10))

    print("\nMissing values:")
    display(df[new_metrics].isna().sum().to_frame("Missing"))

    print("\nSummary statistics:")
    numeric_metrics = [
        "PriceRatio",
        "PricePerSqFt",
        "DaysOnMarket_Analysis",
        "ListingToContractDays",
        "ContractToCloseDays"
    ]

    display(df[numeric_metrics].describe().round(2))

    # Validation
    assert df["PriceRatio"].dropna().gt(0).all()
    assert df["PricePerSqFt"].dropna().gt(0).all()
    assert df["ListingToContractDays"].dropna().ge(0).all()
    assert df["ContractToCloseDays"].dropna().ge(0).all()

    print("Feature validation passed!")


# In[4]:


# ============================================================
# SEGMENT ANALYSIS
# ============================================================

def create_segment_summary(df, group_col, min_count=1):

    valid = df[
        (df["ClosePrice_Clean"] > 0) &
        df[group_col].notna()
    ].copy()

    summary = (
        valid.groupby(group_col)
        .agg(
            Transaction_Count=("ListingKey", "size"),
            Median_ClosePrice=("ClosePrice_Clean", "median"),
            Mean_ClosePrice=("ClosePrice_Clean", "mean"),
            Median_PricePerSqFt=("PricePerSqFt", "median"),
            Median_DOM=("DaysOnMarket_Analysis", "median"),
            Median_PriceRatio=("PriceRatio", "median"),
            Median_ContractToCloseDays=(
                "ContractToCloseDays", "median"
            )
        )
        .reset_index()
    )

    summary = summary[
        summary["Transaction_Count"] >= min_count
    ]

    return summary.sort_values(
        "Transaction_Count",
        ascending=False
    )


# Property Type
property_type_summary = create_segment_summary(
    sold_week6, "PropertyType"
)

# Property Subtype
subtype_summary = create_segment_summary(
    sold_week6, "PropertySubType"
)

# County
county_summary = create_segment_summary(
    sold_week6, "CountyOrParish", min_count=100
)

# MLS Area
mls_area_summary = create_segment_summary(
    sold_week6, "MLSAreaMajor", min_count=30
)

# Listing Office
listing_office_summary = create_segment_summary(
    sold_week6, "ListOfficeName", min_count=30
)

# Buyer Office
buyer_office_summary = create_segment_summary(
    sold_week6, "BuyerOfficeName", min_count=30
)

print("=== PROPERTY SUBTYPE ===")
display(subtype_summary.head(10).round(2))

print("\n=== COUNTY ===")
display(
    county_summary.sort_values(
        "Median_ClosePrice", ascending=False
    ).head(10).round(2)
)

print("\n=== MLS AREA ===")
display(mls_area_summary.head(10).round(2))

print("\n=== LISTING OFFICE ===")
display(listing_office_summary.head(10).round(2))

print("\n=== BUYER OFFICE ===")
display(buyer_office_summary.head(10).round(2))


# In[5]:


get_ipython().run_line_magic('pip', 'install geopandas pyogrio shapely')


# In[6]:


import geopandas as gpd

# Official California school district GeoJSON
school_url = (
    "https://gis.data.ca.gov/api/download/v1/items/"
    "b0e3b936426a47ce9d9a2e77e2bb86cc/"
    "geojson?layers=0"
)

school_file = folder / "california_school_districts_2024_25.geojson"

# Download once and cache locally
if not school_file.exists():
    import requests

    response = requests.get(school_url, timeout=180)
    response.raise_for_status()
    school_file.write_bytes(response.content)

# Read boundaries
districts = gpd.read_file(school_file)

print("Districts shape:", districts.shape)
print("CRS:", districts.crs)
print("Columns:")
print(districts.columns.tolist())

display(districts.head())


# In[7]:


# ============================================================
# SCHOOL DISTRICT SPATIAL JOIN
# ============================================================

# Ensure WGS84 coordinates
districts = districts.to_crs("EPSG:4326")

# Identify district name column
name_candidates = [
    "DistrictName", "District_Name", "DISTRICTNAME",
    "NAME", "Name", "name", "District"
]

district_name_col = next(
    (c for c in name_candidates if c in districts.columns),
    None
)

# Also search other column names containing "name"
if district_name_col is None:
    candidates = [
        c for c in districts.columns
        if "name" in c.lower() and c != "geometry"
    ]
    if len(candidates) == 1:
        district_name_col = candidates[0]

if district_name_col is None:
    raise ValueError(
        "School district name column not identified. "
        f"Available columns: {districts.columns.tolist()}"
    )

type_candidates = [
    "DistrictType", "District_Type",
    "DISTRICTTYPE", "district_type"
]

district_type_col = next(
    (c for c in type_candidates if c in districts.columns),
    None
)

if district_type_col is None:
    raise ValueError(
        "DistrictType column not found. "
        f"Available columns: {districts.columns.tolist()}"
    )

print("District name:", district_name_col)
print("District type:", district_type_col)

display(
    districts[district_type_col]
    .value_counts(dropna=False)
)


# In[8]:


def add_school_districts(df, districts, chunk_size=50000):

    result = df.copy()

    # Store a list of all matching districts
    result["SchoolDistricts_2024_25"] = pd.Series(
        pd.NA, index=result.index, dtype="string"
    )

    result["SchoolDistrictTypes_2024_25"] = pd.Series(
        pd.NA, index=result.index, dtype="string"
    )

    lat = pd.to_numeric(
        result["Latitude_Clean"], errors="coerce"
    )
    lon = pd.to_numeric(
        result["Longitude_Clean"], errors="coerce"
    )

    state = (
        result["StateOrProvince"]
        .astype("string")
        .str.upper()
        .str.strip()
    )

    valid = (
        lat.notna() &
        lon.notna() &
        state.eq("CA").fillna(False)
    )

    # Avoid carrying all property columns into spatial join
    work = pd.DataFrame({
        "_row_id": np.arange(len(result)),
        "lat": lat.to_numpy(),
        "lon": lon.to_numpy()
    }).loc[valid.to_numpy()]

    boundaries = districts[
        [district_name_col, district_type_col, "geometry"]
    ].copy()

    matched_ids = []
    matched_names = []
    matched_types = []

    for start in range(0, len(work), chunk_size):

        chunk = work.iloc[start:start + chunk_size]

        points = gpd.GeoDataFrame(
            chunk[["_row_id"]].copy(),
            geometry=gpd.points_from_xy(
                chunk["lon"], chunk["lat"]
            ),
            crs="EPSG:4326"
        )

        joined = gpd.sjoin(
            points,
            boundaries,
            how="left",
            predicate="intersects"
        )

        # Multiple district polygons can cover one point.
        # Collect matches instead of duplicating properties.
        matched = joined.dropna(
            subset=[district_name_col]
        ).copy()

        if not matched.empty:

            def combine_unique(series):
                values = sorted(
                    set(series.dropna().astype(str))
                )
                return " | ".join(values)

            grouped = matched.groupby("_row_id").agg(
                names=(district_name_col, combine_unique),
                types=(district_type_col, combine_unique)
            )

            matched_ids.extend(grouped.index.tolist())
            matched_names.extend(grouped["names"].tolist())
            matched_types.extend(grouped["types"].tolist())

    # Match back by positional row identifier
    if matched_ids:
        result.iloc[
            matched_ids,
            result.columns.get_loc("SchoolDistricts_2024_25")
        ] = matched_names

        result.iloc[
            matched_ids,
            result.columns.get_loc("SchoolDistrictTypes_2024_25")
        ] = matched_types

    result["school_district_matched_flag"] = (
        result["SchoolDistricts_2024_25"].notna()
    )

    assert len(result) == len(df)

    return result


listing_week6 = add_school_districts(
    listing_week6, districts
)

sold_week6 = add_school_districts(
    sold_week6, districts
)

print("Listing school district matches:",
      listing_week6["school_district_matched_flag"].sum())

print("Sold school district matches:",
      sold_week6["school_district_matched_flag"].sum())


# In[9]:


# ============================================================
# FINAL WEEK 6 VALIDATION
# ============================================================

for name, original, enriched in [
    ("Listing", listing, listing_week6),
    ("Sold", sold, sold_week6)
]:

    print(f"\n=== {name.upper()} ===")

    print("Rows before:", len(original))
    print("Rows after:", len(enriched))

    # Validate row counts
    assert len(original) == len(enriched)

    # Validate engineered indicators
    assert enriched["PricePerSqFt"].dropna().gt(0).all()
    assert enriched["PriceRatio"].dropna().gt(0).all()

    assert enriched[
        "ListingToContractDays"
    ].dropna().ge(0).all()

    assert enriched[
        "ContractToCloseDays"
    ].dropna().ge(0).all()

    print("Valid Price Ratios:",
          enriched["PriceRatio"].notna().sum())

    print("Valid Price Per Sq Ft:",
          enriched["PricePerSqFt"].notna().sum())

    print("School District Matches:",
          enriched["school_district_matched_flag"].sum())

    print("Validation passed!")


# In[10]:


sample_cols = [
    "ListingKey",
    "CountyOrParish",
    "PropertySubType",
    "ClosePrice",
    "OriginalListPrice",
    "LivingArea",
    "PriceRatio",
    "CloseToOriginalListRatio",
    "PricePerSqFt",
    "DaysOnMarket_Metric",
    "Year",
    "Month",
    "YrMo",
    "ListingToContractDays",
    "ContractToCloseDays",
    "SchoolDistricts_2024_25"
]

print("=== WEEK 6 ENGINEERED METRICS SAMPLE ===")

display(
    sold_week6[sample_cols].head(10).round(2)
)


# In[11]:


# ============================================================
# EXPORT WEEK 6 OUTPUTS
# ============================================================

# Main engineered datasets
listing_week6.to_csv(
    folder / "listing_week6_engineered.csv",
    index=False
)

sold_week6.to_csv(
    folder / "sold_week6_engineered.csv",
    index=False
)

# Segmented summary tables
subtype_summary.to_csv(
    folder / "week6_property_subtype_summary.csv",
    index=False
)

county_summary.to_csv(
    folder / "week6_county_summary.csv",
    index=False
)

mls_area_summary.to_csv(
    folder / "week6_mls_area_summary.csv",
    index=False
)

listing_office_summary.to_csv(
    folder / "week6_listing_office_summary.csv",
    index=False
)

buyer_office_summary.to_csv(
    folder / "week6_buyer_office_summary.csv",
    index=False
)

print("All Week 6 datasets exported successfully!")

print("Listing:", listing_week6.shape)
print("Sold:", sold_week6.shape)


# In[ ]:




