"""
Run from project root:
    python python/01_clean_and_analyze.py

Input: data/online_retail_II.xlsx
Outputs: output/*.csv and output/*.png

This script does not invent results: it prints metrics calculated from your downloaded dataset.
"""
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "online_retail_II.xlsx"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}\n"
        "Download UCI Online Retail II and save it as data/online_retail_II.xlsx"
    )

# Read all sheets, since the UCI workbook commonly splits transactions by period.
raw = pd.read_excel(DATA_PATH, sheet_name=None)
df = pd.concat(raw.values(), ignore_index=True)
df.columns = [str(c).strip().replace(" ", "") for c in df.columns]

# Normalize common source column names.
rename = {
    "Invoice": "Invoice",
    "StockCode": "StockCode",
    "Description": "Description",
    "Quantity": "Quantity",
    "InvoiceDate": "InvoiceDate",
    "Price": "Price",
    "UnitPrice": "Price",
    "CustomerID": "CustomerID",
    "Country": "Country",
}
df = df.rename(columns=rename)
required = ["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "CustomerID", "Country"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing expected columns: {missing}. Found: {list(df.columns)}")

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
for c in ["Quantity", "Price", "CustomerID"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

print("Raw rows:", len(df))
print("Duplicate rows:", int(df.duplicated().sum()))
print("Missing values before cleaning:\n", df[required].isna().sum())

# Clean invalid rows and duplicates. Keep only positive sales lines for core analysis.
df = df.drop_duplicates()
df = df.dropna(subset=["Invoice", "StockCode", "Quantity", "InvoiceDate", "Price", "Country"])
df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]
df["CustomerID"] = df["CustomerID"].astype("Int64")
df["LineRevenue"] = df["Quantity"] * df["Price"]
df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
df["InvoiceYear"] = df["InvoiceDate"].dt.year
df["InvoiceDay"] = df["InvoiceDate"].dt.date.astype(str)

# Export clean line-level data.
clean_cols = ["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price",
              "CustomerID", "Country", "LineRevenue", "InvoiceMonth", "InvoiceYear", "InvoiceDay"]
clean = df[clean_cols].copy()
clean.to_csv(OUT / "cleaned_transactions.csv", index=False)

# Summary outputs
monthly = clean.groupby("InvoiceMonth", as_index=False).agg(
    Revenue=("LineRevenue", "sum"),
    Orders=("Invoice", "nunique"),
    UnitsSold=("Quantity", "sum"),
    Customers=("CustomerID", "nunique")
)
monthly["AverageOrderValue"] = monthly["Revenue"] / monthly["Orders"].replace(0, np.nan)
monthly.to_csv(OUT / "monthly_sales.csv", index=False)

country = clean.groupby("Country", as_index=False).agg(
    Revenue=("LineRevenue", "sum"),
    Orders=("Invoice", "nunique"),
    Customers=("CustomerID", "nunique"),
    UnitsSold=("Quantity", "sum")
).sort_values("Revenue", ascending=False)
country.to_csv(OUT / "country_sales.csv", index=False)

product = clean.groupby(["StockCode", "Description"], as_index=False).agg(
    Revenue=("LineRevenue", "sum"),
    UnitsSold=("Quantity", "sum"),
    Orders=("Invoice", "nunique")
).sort_values("Revenue", ascending=False)
product.to_csv(OUT / "product_sales.csv", index=False)

# Customer RFM (snapshot date is one day after the latest transaction date).
customer_data = clean.dropna(subset=["CustomerID"]).copy()
snapshot = customer_data["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)
rfm = customer_data.groupby("CustomerID").agg(
    LastPurchase=("InvoiceDate", "max"),
    Frequency=("Invoice", "nunique"),
    Monetary=("LineRevenue", "sum")
).reset_index()
rfm["Recency"] = (snapshot - rfm["LastPurchase"].dt.normalize()).dt.days
rfm = rfm[["CustomerID", "Recency", "Frequency", "Monetary"]]
rfm.to_csv(OUT / "customer_rfm.csv", index=False)

# K-Means segmentation. Log-transform skewed positive RFM data, then standardize.
rfm_model = rfm[(rfm["Frequency"] > 0) & (rfm["Monetary"] > 0)].copy()
if len(rfm_model) >= 4:
    features = np.log1p(rfm_model[["Recency", "Frequency", "Monetary"]].astype(float))
    scaler = StandardScaler()
    X = scaler.fit_transform(features)
    model = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm_model["Segment"] = model.fit_predict(X)
    rfm_model.to_csv(OUT / "customer_segments.csv", index=False)
    print("\nCustomer segment counts:\n", rfm_model["Segment"].value_counts().sort_index())
else:
    warnings.warn("Not enough customers for clustering; skipping customer_segments.csv")

# Simple forecasting baseline: last 3 months average predicts the next month.
# This is a baseline, not a claim that it is the best forecasting model.
monthly_sorted = monthly.sort_values("InvoiceMonth").reset_index(drop=True)
if len(monthly_sorted) >= 6:
    actual = monthly_sorted["Revenue"].astype(float).to_numpy()
    # Rolling one-step predictions on the final 3 months using prior up-to-3-month average.
    preds, truths = [], []
    for i in range(max(3, len(actual)-3), len(actual)):
        preds.append(float(np.mean(actual[max(0, i-3):i])))
        truths.append(float(actual[i]))
    mae = mean_absolute_error(truths, preds)
    rmse = float(np.sqrt(mean_squared_error(truths, preds)))
    print(f"\nBaseline time-based holdout MAE: {mae:,.2f}")
    print(f"Baseline time-based holdout RMSE: {rmse:,.2f}")
    next_pred = float(np.mean(actual[-3:]))
    next_month = (pd.Period(monthly_sorted["InvoiceMonth"].iloc[-1], freq="M") + 1).strftime("%Y-%m")
    pd.DataFrame([{"ForecastMonth": next_month, "PredictedRevenue_Baseline": next_pred,
                   "Method": "Mean of previous 3 months"}]).to_csv(OUT / "sales_forecast.csv", index=False)
    print(f"Next-month baseline forecast for {next_month}: {next_pred:,.2f}")
else:
    print("Not enough monthly periods for the forecasting baseline.")

# Plot monthly revenue
plt.figure(figsize=(12, 5))
plt.plot(monthly["InvoiceMonth"], monthly["Revenue"], marker="o")
plt.title("Monthly Revenue")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=60, ha="right")
plt.tight_layout()
plt.savefig(OUT / "monthly_revenue.png", dpi=160)
plt.close()

print("\nDone. Files saved in:", OUT)
print("Clean rows:", len(clean))
print("Revenue total:", f"{clean['LineRevenue'].sum():,.2f}")
print("Unique invoices:", clean["Invoice"].nunique())
print("Unique customers with IDs:", clean["CustomerID"].nunique())
