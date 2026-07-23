import os

import numpy as np
import pandas as pd

from sqlalchemy import create_engine


# ==================================================
# 1. Display settings
# ==================================================

pd.set_option(
    "display.max_columns",
    None
)

pd.set_option(
    "display.width",
    1000
)


# ==================================================
# 2. Create folders
# ==================================================

os.makedirs(
    "../reports_nike",
    exist_ok=True
)

os.makedirs(
    "../data/validated",
    exist_ok=True
)

os.makedirs(
    "../data/rejected",
    exist_ok=True
)


# ==================================================
# 3. Database connection
# ==================================================

engine = create_engine(
    "sqlite:///database/nike_sales.db"
)


# ==================================================
# 4. Load ETL V1 output
# ==================================================

df = pd.read_sql(
    """
    SELECT *
    FROM nike_sales_v1
    """,
    engine
)


print(
    "Source rows:",
    len(df)
)


# ==================================================
# 5. Create validation columns
# ==================================================

df["rejection_reason"] = ""

df["warning_reason"] = ""

df["audit_note"] = ""


# ==================================================
# 6. Revenue Difference
# ==================================================
# Only compare.
# No new revenue calculation.

df["Revenue_Difference"] = (
    df["Original_Revenue"]
    -
    df["Calculated_Revenue"]
).round(2)



# ==================================================
# 7. Completeness Validation
# ==================================================
# After V1 these should ideally be zero.


# Units

df.loc[
    df["Units_Sold"].isna(),
    "rejection_reason"
] += "Missing Units_Sold; "



# MRP

df.loc[
    df["MRP"].isna(),
    "rejection_reason"
] += "Missing MRP; "



# Discount

df.loc[
    df["Discount_Applied"].isna(),
    "rejection_reason"
] += "Missing Discount; "



# Revenue

df.loc[
    df["Calculated_Revenue"].isna(),
    "rejection_reason"
] += "Missing Calculated Revenue; "



# Order Date

df.loc[
    df["Order_Date"].isna(),
    "rejection_reason"
] += "Missing Order Date; "



# ==================================================
# 8. Business Rule Validation
# ==================================================


# Units must be positive

df.loc[
    df["Units_Sold"] <= 0,
    "rejection_reason"
] += "Invalid Units_Sold; "



# MRP must be positive

df.loc[
    df["MRP"] <= 0,
    "rejection_reason"
] += "Invalid MRP; "



# Discount must be between 0 and 1

df.loc[
    ~df["Discount_Applied"].between(0,1),
    "rejection_reason"
] += "Invalid Discount; "



# Revenue cannot be negative

df.loc[
    df["Calculated_Revenue"] < 0,
    "rejection_reason"
] += "Negative Revenue; "




# ==================================================
# 9. Duplicate Validation
# ==================================================

df["Duplicate_Order_ID"] = df.duplicated(
    subset=["Order_ID"],
    keep=False
)


df.loc[
    df["Duplicate_Order_ID"],
    "warning_reason"
] += "Duplicate Order_ID; "



# ==================================================
# 10. Revenue Quality Check
# ==================================================
# Not rejection.
# Only business warning/report.


df["Revenue_Mismatch"] = (
    df["Revenue_Difference"].abs()
    > 0.01
)


# ==================================================
# 11. Audit Information from V1
# ==================================================
# These are not errors.


df.loc[
    df["Units_Was_Missing"]
    .fillna(False),
    "audit_note"
] += "Units Imputed in V1; "



df.loc[
    df["Units_Was_Invalid"]
    .fillna(False),
    "audit_note"
] += "Invalid Units Corrected in V1; "



df.loc[
    df["MRP_Was_Missing"]
    .fillna(False),
    "audit_note"
] += "MRP Imputed in V1; "



df.loc[
    df["Discount_Was_Missing"]
    .fillna(False),
    "audit_note"
] += "Discount Imputed in V1; "



df.loc[
    df["Discount_Was_Invalid"]
    .fillna(False),
    "audit_note"
] += "Invalid Discount Corrected in V1; "



# ==================================================
# 12. Clean text columns
# ==================================================

df["rejection_reason"] = (
    df["rejection_reason"]
    .str.rstrip("; ")
)


df["warning_reason"] = (
    df["warning_reason"]
    .str.rstrip("; ")
)


df["audit_note"] = (
    df["audit_note"]
    .str.rstrip("; ")
)



# ==================================================
# 13. Record Status
# ==================================================

df["Record_Status"] = np.select(

    [

        df["rejection_reason"] != "",

        df["warning_reason"] != ""

    ],

    [

        "Rejected",

        "Warning"

    ],

    default="Valid"

)



# ==================================================
# 14. Split Data
# ==================================================

valid_df = df[
    df["Record_Status"] == "Valid"
].copy()



warning_df = df[
    df["Record_Status"] == "Warning"
].copy()



rejected_df = df[
    df["Record_Status"] == "Rejected"
].copy()



# ==================================================
# 15. Quality Report
# ==================================================

quality_report = pd.DataFrame({

    "Metric":[

        "Total Rows",

        "Valid Rows",

        "Warning Rows",

        "Rejected Rows",

        "Missing Units After V1",

        "Missing MRP After V1",

        "Missing Discount After V1",

        "Missing Order Date After V1",

        "Invalid Units",

        "Invalid MRP",

        "Invalid Discount",

        "Negative Revenue",

        "Revenue Mismatch",

        "Duplicate Order ID",

        "Units Imputed in V1",

        "MRP Imputed in V1",

        "Discount Imputed in V1"

    ],


    "Count":[

        len(df),

        len(valid_df),

        len(warning_df),

        len(rejected_df),


        df["Units_Sold"].isna().sum(),

        df["MRP"].isna().sum(),

        df["Discount_Applied"].isna().sum(),

        df["Order_Date"].isna().sum(),


        (df["Units_Sold"] <= 0).sum(),

        (df["MRP"] <= 0).sum(),

        (~df["Discount_Applied"]
         .between(0,1)).sum(),


        (df["Calculated_Revenue"] < 0).sum(),


        df["Revenue_Mismatch"].sum(),


        df["Duplicate_Order_ID"].sum(),


        df["Units_Was_Missing"]
        .fillna(False)
        .sum(),


        df["MRP_Was_Missing"]
        .fillna(False)
        .sum(),


        df["Discount_Was_Missing"]
        .fillna(False)
        .sum()

    ]

})



# ==================================================
# 16. Save CSV
# ==================================================

valid_df.to_csv(
    "data/validated/nike_sales_validated.csv",
    index=False
)


warning_df.to_csv(
    "reports_nike/nike_sales_warning.csv",
    index=False
)


rejected_df.to_csv(
    "data/rejected/nike_sales_rejected.csv",
    index=False
)


quality_report.to_csv(
    "reports_nike/data_quality_report_v2.csv",
    index=False
)



# ==================================================
# 17. Save Database Tables
# ==================================================

valid_df.to_sql(
    "nike_sales_validated",
    engine,
    if_exists="replace",
    index=False
)



warning_df.to_sql(
    "nike_sales_warning",
    engine,
    if_exists="replace",
    index=False
)



rejected_df.to_sql(
    "nike_sales_rejected",
    engine,
    if_exists="replace",
    index=False
)



quality_report.to_sql(
    "nike_sales_quality_report_v2",
    engine,
    if_exists="replace",
    index=False
)



# ==================================================
# 18. Final Summary
# ==================================================

print("\n========== ETL V2 Summary ==========")

print(
    "Total Rows:",
    len(df)
)


print(
    "Valid Rows:",
    len(valid_df)
)


print(
    "Warning Rows:",
    len(warning_df)
)


print(
    "Rejected Rows:",
    len(rejected_df)
)



print("\n========== Quality Report ==========")

print(
    quality_report
)


print(
    "\nETL V2 Completed Successfully"
)

print(
    rejected_df["rejection_reason"]
    .value_counts()
)