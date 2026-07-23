import pandas as pd
import os

# Optional: create folder for audit
os.makedirs("data/audit", exist_ok=True)

# Load raw data
df = pd.read_csv("data/raw_data/Nike_Sales_Uncleaned.csv")

# Create audit dictionary
audit_dict = {
    "Check": [
        "Total Rows",
        "Total Columns",
        "Missing Order_ID",
        "Missing Region",
        "Missing Product_Line",
        "Missing Sales_Channel",
        "Missing Gender_Category",
        "Missing Units_Sold",
        "Missing MRP",
        "Missing Discount_Applied",
        "Missing Revenue",
        "Missing Profit",
        "Duplicate Order_ID",
        "Negative Units",
        "Discount > 1",
        "Negative Revenue",
    ],
    "Count": [
        df.shape[0],
        df.shape[1],
        df["Order_ID"].isnull().sum(),
        df["Region"].isnull().sum(),
        df["Product_Line"].isnull().sum(),
        df["Sales_Channel"].isnull().sum(),
        df["Gender_Category"].isnull().sum(),
        df["Units_Sold"].isnull().sum(),
        df["MRP"].isnull().sum(),
        df["Discount_Applied"].isnull().sum(),
        df["Revenue"].isnull().sum(),
        df["Profit"].isnull().sum(),
        df["Order_ID"].duplicated().sum(),
        (df["Units_Sold"] < 0).sum(),
        (df["Discount_Applied"] > 1).sum(),
        (df["Revenue"] < 0).sum(),
    ]
}

# Convert to DataFrame
audit_df = pd.DataFrame(audit_dict)

# Save to CSV
audit_df.to_csv("data/audit/data_audit_v1.csv", index=False)

print("data_audit_v1.csv created successfully!")