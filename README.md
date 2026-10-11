# ECommerce-Sales-Project
A step-by-step portfolio project using Python, SQL, Excel, Power BI, and machine learning.

## Dataset
Download the UCI Online Retail II dataset:
https://archive.ics.uci.edu/dataset/502/online+retail+ii

Save the downloaded Excel file as:
`data/online_retail_II.xlsx`

Create the `data` folder at the project root. The source workbook may contain two sheets (Year 2009-2010 and Year 2010-2011). The Python script reads all sheets.

## Setup
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
```

## Steps
1. Download the dataset and place it at `data/online_retail_II.xlsx`.
2. Connect MySQL to Python to convert CSV files to MySQL: `python import_csv_to_mysql.py `
3. Run `python 01_clean_and_analyze.py` from the project root.
4. Inspect outputs in `output/`: `cleaned_transactions.csv`, `monthly_sales.csv`, `country_sales.csv`, `product_sales.csv`, `customer_rfm.csv`, `sales_forecast.csv`.
5. Import `output/cleaned_transactions.csv` into MySQL using `sql/01_schema_and_import.sql` (follow comments; use MySQL Workbench Table Data Import Wizard if easier).
6. Run the SQL analysis queries in `sql/02_analysis_queries.sql`.
7. Open `excel/Sales_Analysis_Template.xlsx`; replace the sample rows in `Transactions` with cleaned data. Build PivotTables using the instructions sheet.
8. In Power BI Desktop, import `output/cleaned_transactions.csv` and build visuals using `powerbi/PowerBI_Guide.md`.
9. Run the machine-learning sections of the Python script and report the actual metrics printed by your run.
10. Update the README with screenshots and your real findings. Never invent results.

## Important data definitions
- `LineRevenue = Quantity * UnitPrice`. Returns/negative quantities are kept in the raw source but excluded from the main sales analysis by the cleaning script.
- This is line-level transaction data, not a pre-existing profit dataset. Do not claim profit unless you add and document a cost assumption.
- The forecast is a simple monthly baseline and is not guaranteed to be accurate; compare against a time-based holdout.
