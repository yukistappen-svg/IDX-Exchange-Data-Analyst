#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from pathlib import Path

# CSV 文件所在文件夹
folder = Path("/Users/yuki/csv/")

# 获取文件夹中所有 CSV 文件
csv_files = sorted(folder.glob("*.csv"))

print(f"Total CSV files: {len(csv_files)}")

# 显示所有文件名
for file in csv_files:
    print(file.name)


# In[2]:


# Separate Listing and Sold files
listing_files = sorted(folder.glob("CRMLSListing*.csv"))
sold_files = sorted(folder.glob("CRMLSSold*.csv"))

print("Listing files:", len(listing_files))
print("Sold files:", len(sold_files))

print("\nListing date range:")
print(listing_files[0].name, "to", listing_files[-1].name)

print("\nSold date range:")
print(sold_files[0].name, "to", sold_files[-1].name)


# In[3]:


# Read all Listing CSV files
listing_dfs = []

for file in listing_files:
    df = pd.read_csv(file, low_memory=False)
    listing_dfs.append(df)
    print(f"{file.name}: {len(df):,} rows")

print(f"\nTotal Listing rows: {sum(len(df) for df in listing_dfs):,}")


# Read all Sold CSV files
sold_dfs = []

for file in sold_files:
    df = pd.read_csv(file, low_memory=False)
    sold_dfs.append(df)
    print(f"{file.name}: {len(df):,} rows")

print(f"\nTotal Sold rows: {sum(len(df) for df in sold_dfs):,}")


# In[4]:


# Combine all monthly Listing datasets
listing_combined = pd.concat(
    listing_dfs,
    ignore_index=True
)

# Combine all monthly Sold datasets
sold_combined = pd.concat(
    sold_dfs,
    ignore_index=True
)

# Check row counts after concatenation
print("Listing combined:", listing_combined.shape)
print("Sold combined:", sold_combined.shape)


# In[5]:


# Verify row counts
assert len(listing_combined) == 860898, "Listing row count mismatch!"
assert len(sold_combined) == 615707, "Sold row count mismatch!"

print("All row counts match. Concatenation successful!")


# In[6]:


# Check property type distribution in Listing
print("Listing Property Types:")
print(listing_combined["PropertyType"].value_counts(dropna=False))

print("\nSold Property Types:")
print(sold_combined["PropertyType"].value_counts(dropna=False))


# In[7]:


# Filter Residential properties only
listing_residential = listing_combined[
    listing_combined["PropertyType"] == "Residential"
].copy()

sold_residential = sold_combined[
    sold_combined["PropertyType"] == "Residential"
].copy()

# Compare row counts before and after filtering
print("Listing:")
print(f"Before filtering: {len(listing_combined):,}")
print(f"After filtering:  {len(listing_residential):,}")

print("\nSold:")
print(f"Before filtering: {len(sold_combined):,}")
print(f"After filtering:  {len(sold_residential):,}")


# In[8]:


# 1. Verify concatenation row counts
assert len(listing_combined) == sum(len(df) for df in listing_dfs)
assert len(sold_combined) == sum(len(df) for df in sold_dfs)

# 2. Verify all remaining properties are Residential
assert listing_residential["PropertyType"].eq("Residential").all()
assert sold_residential["PropertyType"].eq("Residential").all()

# 3. Verify expected residential row counts
assert len(listing_residential) == 547162
assert len(sold_residential) == 414054

# 4. Check dataset dimensions
print("Listing Residential:", listing_residential.shape)
print("Sold Residential:", sold_residential.shape)

print("\nAll validation checks passed!")


# In[9]:


# Export Residential datasets to CSV
listing_residential.to_csv(
    folder / "combined_listing_residential.csv",
    index=False
)

sold_residential.to_csv(
    folder / "combined_sold_residential.csv",
    index=False
)

print("Both Residential datasets exported successfully!")


# In[ ]:




