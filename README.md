# Nike Sales Analytics

## Project Summary
This project provides an end-to-end **ETL pipeline** and **analytics dashboard** for Nike sales data. 
It covers data cleaning, validation, modeling, and visualization, allowing users to monitor key metrics,
monthly trends, top products, and regional performance.

---

## Project Structure
pythonProject1/
├── analytics/ # Python scripts for analytics
│ └── analytics.py
├── dashboard/ # Streamlit dashboard
│ └── app.py
├── data/ # Raw, validated, rejected, processed datasets
│ ├── raw_data/
│ ├── validated/
│ ├── rejected/
│ ├── processed/
│ └── audit/
├── etl/ # ETL pipeline scripts
│ ├── etl_v1_cleaning.py
│ ├── etl_v2_validation.py
│ └── etl_v3_modeling.py
├── reports/ # Generated reports and summaries
├── reports_nike/ # KPI reports and charts
├── database/ # Database files
├── data_audit.py
├── .gitignore
└── README.md

---

## Features

- **Data Cleaning & Validation**  
  Remove duplicates, missing values, and invalid entries.
  
- **ETL Pipeline**  
  Three stages: cleaning, validation, and modeling.

- **Analytics Dashboard**  
  Visualizations for revenue, profit, top products, and regions using Streamlit and Plotly.

- **Reports**  
  Generate CSV summaries and KPI reports for decision-making.

- **Filters**  
  Dashboard supports year, region, and sales channel filtering.

---

## Requirements

- Python 3.10+
- Pandas
- SQLAlchemy
- Streamlit
- Plotly
- PostgreSQL or SQLite

Install dependencies:

```bash
pip install -r requirements.txt
Usage
Clone the repository:
git clone https://github.com/MineUddin908/nike-sales-analytics.git
cd nike-sales-analytics
Run ETL pipeline:
python etl/etl_v1_cleaning.py
python etl/etl_v2_validation.py
python etl/etl_v3_modeling.py
Start the dashboard:
streamlit run dashboard/app.py
Open the browser to view interactive charts and KPIs.

Reports

Reports are saved in:

reports/ → summary CSVs
reports_nike/ → top products, top regions, profit margin, total revenue/profit, monthly trends
Notes
Keep data/raw_data/ for original datasets.
.gitignore includes database files and large datasets to avoid unnecessary uploads.
Ensure database credentials are configured correctly in analytics.py.
Author

MD MAIN UDDIN
GitHub: MineUddin908
Email: mdmainuddin908@gmail.com
