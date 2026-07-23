import os

import numpy as np
import pandas as pd
from sqlalchemy import create_engine


# --------------------------------------------------
# 1. Display settings
# --------------------------------------------------

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


# --------------------------------------------------
# 2. Extract
# --------------------------------------------------

input_file = "../data/raw_data/Nike_Sales_Uncleaned.csv"

df = pd.read_csv(input_file)

print("Raw dataset shape:", df.shape)


# --------------------------------------------------
# 3. Preserve raw data information
# --------------------------------------------------

df["Original_Revenue"] = df["Revenue"]


# --------------------------------------------------
# 4. Clean column names
# --------------------------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.replace(" ", "_")
)


# --------------------------------------------------
# 5. Clean text columns
# --------------------------------------------------

text_columns = [
    "Gender_Category",
    "Product_Line",
    "Product_Name",
    "Size",
    "Sales_Channel",
    "Region"
]

for col in text_columns:
    df[col] = (
        df[col]
        .astype("string")
        .str.strip()
    )


# Standardize text formats

df["Gender_Category"] = df["Gender_Category"].str.title()
df["Product_Line"] = df["Product_Line"].str.title()
df["Product_Name"] = df["Product_Name"].str.title()
df["Sales_Channel"] = df["Sales_Channel"].str.title()


# --------------------------------------------------
# 6. Standardize regions
# --------------------------------------------------

region_mapping = {
    "delhi": "Delhi",
    "mumbai": "Mumbai",
    "kolkata": "Kolkata",
    "pune": "Pune",
    "bengaluru": "Bengaluru",
    "bangalore": "Bengaluru",
    "hyderbad": "Hyderabad",
    "hyd": "Hyderabad",
    "hyderabad": "Hyderabad"
}

original_region = df["Region"].str.lower()

df["Region"] = (
    original_region
    .map(region_mapping)
    .fillna(original_region.str.title())
)


# --------------------------------------------------
# 7. Convert numeric columns
# --------------------------------------------------

numeric_columns = [
    "Units_Sold",
    "MRP",
    "Discount_Applied",
    "Revenue",
    "Profit"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


# Original_Revenue was created before numeric conversion

df["Original_Revenue"] = pd.to_numeric(
    df["Original_Revenue"],
    errors="coerce"
)


# --------------------------------------------------
# 8. Convert date
# --------------------------------------------------

df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce",
    format="mixed",
    dayfirst=True
)


# --------------------------------------------------
# 9. Create validation flags before correction
# --------------------------------------------------

df["Units_Was_Missing"] = df["Units_Sold"].isna()

df["Units_Was_Invalid"] = (
    df["Units_Sold"].notna()
    & (df["Units_Sold"] <= 0)
)

df["MRP_Was_Missing"] = df["MRP"].isna()

df["Discount_Was_Missing"] = df["Discount_Applied"].isna()

df["Discount_Was_Invalid"] = (
    df["Discount_Applied"].notna()
    & ~df["Discount_Applied"].between(0, 1)
)

df["Date_Was_Missing"] = df["Order_Date"].isna()


# --------------------------------------------------
# 10. Handle invalid units
# --------------------------------------------------

df.loc[
    df["Units_Sold"] <= 0,
    "Units_Sold"
] = np.nan


# Fill units using product and sales-channel median

df["Units_Sold"] = df.groupby(
    ["Product_Name", "Sales_Channel"]
)["Units_Sold"].transform(
    lambda x: x.fillna(x.median())
)

# Fallback overall median

df["Units_Sold"] = df["Units_Sold"].fillna(
    df["Units_Sold"].median()
)


# --------------------------------------------------
# 11. Handle missing MRP
# --------------------------------------------------

df["MRP"] = df.groupby(
    "Product_Name"
)["MRP"].transform(
    lambda x: x.fillna(x.median())
)

df["MRP"] = df["MRP"].fillna(
    df["MRP"].median()
)


# --------------------------------------------------
# 12. Handle invalid discount
# --------------------------------------------------

df.loc[
    ~df["Discount_Applied"].between(0, 1),
    "Discount_Applied"
] = np.nan


# Fill discount using sales-channel median

df["Discount_Applied"] = df.groupby(
    "Sales_Channel"
)["Discount_Applied"].transform(
    lambda x: x.fillna(x.median())
)

df["Discount_Applied"] = df["Discount_Applied"].fillna(
    df["Discount_Applied"].median()
)


# --------------------------------------------------
# 13. Calculate revenue
# --------------------------------------------------

df["Calculated_Revenue"] = (
    df["Units_Sold"]
    * df["MRP"]
    * (1 - df["Discount_Applied"])
).round(2)


# --------------------------------------------------
# 14. Compare original and calculated revenue
# --------------------------------------------------

df["Revenue_Difference"] = (
    df["Original_Revenue"]
    - df["Calculated_Revenue"]
).round(2)

valid_comparison = (
    df["Original_Revenue"].notna()
    & df["Calculated_Revenue"].notna()
)

df["Revenue_Match"] = pd.NA

df.loc[valid_comparison, "Revenue_Match"] = np.isclose(
    df.loc[valid_comparison, "Original_Revenue"],
    df.loc[valid_comparison, "Calculated_Revenue"],
    atol=0.01
)

revenue_mismatch_count = (
    df["Revenue_Match"] == False
).sum()


# --------------------------------------------------
# 15. Create surrogate key
# --------------------------------------------------

df.insert(
    0,
    "Sales_ID",
    range(1, len(df) + 1)
)


# --------------------------------------------------
# 16. Create output folders
# --------------------------------------------------

os.makedirs("../data/processed", exist_ok=True)
os.makedirs("../database", exist_ok=True)
os.makedirs("../reports_nike", exist_ok=True)


# --------------------------------------------------
# 17. Save processed CSV
# --------------------------------------------------

processed_file = "../data/processed/nike_sales_v1.csv"

df.to_csv(
    processed_file,
    index=False
)


# --------------------------------------------------
# 18. Load into SQLite
# --------------------------------------------------

engine = create_engine(
    "sqlite:///database/nike_sales.db"
)

df.to_sql(
    name="nike_sales_v1",
    con=engine,
    if_exists="replace",
    index=False
)


# --------------------------------------------------
# 19. Create data-quality summary
# --------------------------------------------------

quality_report = pd.DataFrame({
    "Metric": [
        "Total rows",
        "Duplicate full rows",
        "Rows with duplicate Order_ID",
        "Original missing units",
        "Original invalid units",
        "Original missing MRP",
        "Original missing discount",
        "Original invalid discount",
        "Missing or invalid dates",
        "Revenue mismatches"
    ],
    "Count": [
        len(df),
        df.duplicated().sum(),
        df["Order_ID"].duplicated(keep=False).sum(),
        df["Units_Was_Missing"].sum(),
        df["Units_Was_Invalid"].sum(),
        df["MRP_Was_Missing"].sum(),
        df["Discount_Was_Missing"].sum(),
        df["Discount_Was_Invalid"].sum(),
        df["Date_Was_Missing"].sum(),
        revenue_mismatch_count
    ]
})

quality_report.to_csv(
    "reports_nike/data_quality_report_v1.csv",
    index=False
)


# --------------------------------------------------
# 20. Verify data from database
# --------------------------------------------------

data_from_db = pd.read_sql(
    """
    SELECT *
    FROM nike_sales_v1
    LIMIT 10
    """,
    engine
)

print("\nDatabase preview:")
print(data_from_db)

print("\nCalculated Revenue Summary:")
print(df["Calculated_Revenue"].describe())

print("\nOriginal Revenue Summary:")
print(df["Original_Revenue"].describe())

print("\nData Quality Report:")
print(quality_report)

print("\nRevenue mismatch count:", revenue_mismatch_count)
print("Processed file saved:", processed_file)