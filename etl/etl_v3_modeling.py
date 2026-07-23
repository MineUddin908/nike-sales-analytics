import pandas as pd
from sqlalchemy import create_engine, insert
import os

postgres_engine = create_engine(
    "postgresql://postgres:mine@localhost:5432/nike_sales"
)

engine=create_engine("sqlite:///database/nike_sales.db")

df=pd.read_sql(
    """
    select * 
    from nike_sales_validated
    """,
    engine
)
dim_product = df[
    [
        "Product_Name",
        "Product_Line",
        "Gender_Category",
        "Size"
    ]
].drop_duplicates()


dim_product = dim_product.reset_index(drop=True)


dim_product.insert(
    0,
    "Product_ID",
    range(1,len(dim_product)+1)
)

dim_region = df[
    [
        "Region"
    ]
].drop_duplicates()


dim_region = dim_region.reset_index(drop=True)


dim_region.insert(
    0,
    "Region_ID",
    range(1,len(dim_region)+1)
)
dim_channel = df[
    [
        "Sales_Channel"
    ]
].drop_duplicates()


dim_channel = dim_channel.reset_index(drop=True)


dim_channel.insert(
    0,
    "Channel_ID",
    range(1,len(dim_channel)+1)
)
df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce"
)
dim_date = pd.DataFrame()


dim_date["Full_Date"] = (
    df["Order_Date"]
    .drop_duplicates()
)


dim_date = dim_date.sort_values(
    "Full_Date"
)


dim_date = dim_date.reset_index(
    drop=True
)


dim_date.insert(
    0,
    "Date_ID",
    dim_date["Full_Date"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)


dim_date["Year"] = (
    dim_date["Full_Date"]
    .dt.year
)


dim_date["Month"] = (
    dim_date["Full_Date"]
    .dt.month
)


dim_date["Month_Name"] = (
    dim_date["Full_Date"]
    .dt.month_name()
)


dim_date["Quarter"] = (
    dim_date["Full_Date"]
    .dt.quarter
)


dim_date["Day"] = (
    dim_date["Full_Date"]
    .dt.day
)

fact=df.merge(
    dim_product,
    on=[
        "Product_Name",
        "Product_Line",
        "Gender_Category",
        "Size"
    ],
    how="left"
)

print(df.shape)
fact = fact.merge(
    dim_region,
    on="Region",
    how="left"
)
fact = fact.merge(
    dim_channel,
    on="Sales_Channel",
    how="left"
)
fact = fact.merge(
    dim_date,
    left_on="Order_Date",
    right_on="Full_Date",
    how="left"
)

fact_sales = fact[
[
    "Sales_ID",
    "Order_ID",

    "Product_ID",
    "Region_ID",
    "Channel_ID",
    "Date_ID",

    "Units_Sold",
    "MRP",
    "Discount_Applied",

    "Calculated_Revenue",
    "Profit"
]
]

dim_product.to_sql(
    "dim_product",
     postgres_engine,
    schema="warehouse",
    if_exists="replace",
    index=False
)
dim_region.to_sql(
    "dim_region",
    postgres_engine,
    schema="warehouse",
    if_exists="replace",
    index=False
)


dim_channel.to_sql(
    "dim_channel",
    postgres_engine,
    schema="warehouse",
    if_exists="replace",
    index=False
)


dim_date.to_sql(
    "dim_date",
    postgres_engine,
    schema="warehouse",
    if_exists="replace",
    index=False
)


fact_sales.to_sql(
    "fact_sales",
    postgres_engine,
    schema="warehouse",
    if_exists="replace",
    index=False
)