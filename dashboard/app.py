import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import os


# ==========================
# Database Connection
# ==========================

engine = create_engine(
    "postgresql://postgres:mine@localhost:5432/nike_sales"
)


# ==========================
# Title
# ==========================

st.title("Nike Sales Analytics Dashboard")

# ============================
# Sidebar Filters
# ============================

st.sidebar.header("Filters")


years = pd.read_sql(
    """
    SELECT DISTINCT "Year"
    FROM warehouse.dim_date
    ORDER BY "Year"
    """,
    engine
)


selected_year = st.sidebar.multiselect(
    "Select Year",
    years["Year"].tolist(),
    default=years["Year"].tolist()
)



regions = pd.read_sql(
    """
    SELECT DISTINCT "Region"
    FROM warehouse.dim_region
    ORDER BY "Region"
    """,
    engine
)


selected_region = st.sidebar.multiselect(
    "Select Region",
    regions["Region"].tolist(),
    default=regions["Region"].tolist()
)



channels = pd.read_sql(
    """
    SELECT DISTINCT "Sales_Channel"
    FROM warehouse.dim_channel
    ORDER BY "Sales_Channel"
    """,
    engine
)


selected_channel = st.sidebar.multiselect(
    "Select Sales Channel",
    channels["Sales_Channel"].tolist(),
    default=channels["Sales_Channel"].tolist()
)


# ==========================
# KPI Section
# ==========================

kpi = pd.read_sql(
f"""
SELECT

SUM(f."Calculated_Revenue") AS revenue,

SUM(f."Profit") AS profit,

COUNT(f."Order_ID") AS orders


FROM warehouse.fact_sales f


JOIN warehouse.dim_date d
ON f."Date_ID" = d."Date_ID"


JOIN warehouse.dim_region r
ON f."Region_ID" = r."Region_ID"


JOIN warehouse.dim_channel c
ON f."Channel_ID" = c."Channel_ID"


WHERE d."Year" IN ({','.join(map(str,selected_year))})

AND r."Region" IN ({','.join([f"'{x}'" for x in selected_region])})

AND c."Sales_Channel" IN ({','.join([f"'{x}'" for x in selected_channel])})

""",
engine
)

col1, col2, col3 = st.columns(3)


col1.metric(
    "Total Revenue",
    round(kpi["revenue"][0], 2)
)


col2.metric(
    "Total Profit",
    round(kpi["profit"][0], 2)
)


col3.metric(
    "Total Orders",
    kpi["orders"][0]
)

region_sales = pd.read_sql(
f"""

SELECT

r."Region",

SUM(f."Calculated_Revenue") AS revenue


FROM warehouse.fact_sales f


JOIN warehouse.dim_region r

ON f."Region_ID" = r."Region_ID"


JOIN warehouse.dim_date d

ON f."Date_ID" = d."Date_ID"


WHERE d."Year" IN ({','.join(map(str,selected_year))})


GROUP BY r."Region"


ORDER BY revenue DESC


""",
engine
)


fig_region = px.bar(
    region_sales,
    x="Region",
    y="revenue",
    title="Revenue by Region"
)


st.plotly_chart(
    fig_region,
    use_container_width=True,
    key="region_chart"
)
channel_sales = pd.read_sql(
f"""

SELECT


c."Sales_Channel",

SUM(f."Calculated_Revenue") AS revenue


FROM warehouse.fact_sales f


JOIN warehouse.dim_channel c

ON f."Channel_ID" = c."Channel_ID"


JOIN warehouse.dim_date d

ON f."Date_ID" = d."Date_ID"


WHERE d."Year" IN ({','.join(map(str,selected_year))})


GROUP BY c."Sales_Channel"


ORDER BY revenue DESC


""",
engine
)



fig_channel = px.pie(
    channel_sales,
    names="Sales_Channel",
    values="revenue",
    title="Sales Channel Contribution"
)



st.plotly_chart(
    fig_channel,
    use_container_width=True,
    key="channel_chart"
)

# ==========================
# Monthly Revenue Trend
# ==========================

monthly_sales = pd.read_sql(
    """

    SELECT

    d."Month_Name",

    d."Month",

    SUM(f."Calculated_Revenue") AS Revenue


    FROM warehouse.fact_sales f


    JOIN warehouse.dim_date d

    ON f."Date_ID" = d."Date_ID"


    GROUP BY

    d."Month_Name",
    d."Month"


    ORDER BY d."Month"


    """,
    engine
)


fig_monthly = px.line(
    monthly_sales,
    x="Month_Name",
    y="revenue",
    title="Monthly Revenue Trend"
)


st.plotly_chart(
    fig_monthly,
    key="monthly_revenue_chart"
)



# ==========================
# Top 10 Products
# ==========================

product_sales = pd.read_sql(
    """

    SELECT

    p."Product_Name",

    SUM(f."Calculated_Revenue") AS Revenue


    FROM warehouse.fact_sales f


    JOIN warehouse.dim_product p

    ON f."Product_ID" = p."Product_ID"


    GROUP BY

    p."Product_Name"


    ORDER BY Revenue DESC


    LIMIT 10


    """,
    engine
)



fig_product = px.bar(
    product_sales,
    x="Product_Name",
    y="revenue",
    title="Top 10 Products"
)


st.plotly_chart(
    fig_product,
    key="top_product_chart"
)