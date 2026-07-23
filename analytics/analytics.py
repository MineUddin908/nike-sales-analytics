import pandas as pd
from sqlalchemy import create_engine



pd.set_option("display.max_columns",None)
pd.set_option("display.width",1000)

postgres_engine = create_engine(
    "postgresql://postgres:mine@localhost:5432/nike_sales"
)
df=pd.read_sql(
    """
    select *
    from warehouse.fact_sales
    limit 10
    """,
    postgres_engine
)
print(df)
Total_Revenue=pd.read_sql(
    """
    select sum("Calculated_Revenue") as total_revenue
    from warehouse.fact_sales
    """,
    postgres_engine
)
Total_Revenue.to_csv(
    "reports_nike/total_revenue.csv",
    index=False
)
print(Total_Revenue)

total_profit= pd.read_sql(
    """
    select sum("Profit") as total_profit
    from warehouse.fact_sales
    """,
    postgres_engine
)
total_profit.to_csv(
    "reports_nike/total_profit.csv",
    index=False
)
print(total_profit)

profit_margin = pd.read_sql(
    """
    SELECT
    ROUND(
        (
            SUM("Profit") * 100.0 /
            SUM("Calculated_Revenue")
        )::numeric,
        2
    ) AS Profit_Margin_Percentage

    FROM warehouse.fact_sales
    """,
    postgres_engine
)

profit_margin.to_csv(
    "reports_nike/profit_margin.csv",
    index=False
)


print(profit_margin)

Top_Product=pd.read_sql(
    """
    select f."Product_Name",
    sum(i."Calculated_Revenue") as Revenue
    from warehouse.dim_product f 
    join warehouse.fact_sales i on i."Product_ID"= F."Product_ID"
    group by f."Product_Name"
    order by Revenue desc
    limit 10
    """,
    postgres_engine
)

Top_Product.to_csv(
    "reports_nike/Top_Product.csv",
    index=False
)

print(Top_Product)

Top_Region=pd.read_sql(
    """SELECT
    r."Region",
    SUM(f."Calculated_Revenue") AS Revenue,
    SUM(f."Profit") AS Profit

FROM warehouse.fact_sales f

JOIN warehouse.dim_region r
ON f."Region_ID" = r."Region_ID"

GROUP BY r."Region"

ORDER BY Revenue DESC;
    """,
    postgres_engine
)
Top_Region.to_csv(
    "reports_nike/Top_Region.csv",
    index=False
)
print(Top_Region)


Monthly_Sales_Trend=pd.read_sql(
    """SELECT

d."Year",
d."Month_Name",

SUM(f."Calculated_Revenue") AS Revenue

FROM warehouse.fact_sales f

JOIN warehouse.dim_date d
ON f."Date_ID"=d."Date_ID"

GROUP BY
d."Year",
d."Month",
d."Month_Name"

ORDER BY
d."Year",
d."Month";

    """,
    postgres_engine
)
Monthly_Sales_Trend.to_csv(
    "reports_nike/Monthly_Sales_Trend",
    index=False
)
print(Monthly_Sales_Trend)