
import pandas as pd
import mysql.connector
from getpass import getpass

csv_path = r"D:\ecommerce_sales_project\output\cleaned_transactions.csv"

df = pd.read_csv(
    csv_path,
    dtype={
        "Invoice": str,
        "StockCode": str,
        "CustomerID": str
    }
)

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)

df = df.astype(object).where(pd.notna(df), None)

password = getpass("Enter your MySQL password: ")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="ecommerce_analytics"
)

cursor = conn.cursor()

sql = """
INSERT INTO cleaned_transactions
(Invoice, StockCode, Description, Quantity, InvoiceDate,
 Price, CustomerID, Country, LineRevenue)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

columns = [
    "Invoice", "StockCode", "Description", "Quantity",
    "InvoiceDate", "Price", "CustomerID", "Country",
    "LineRevenue"
]

def prepare_value(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if hasattr(value, "item"):
        return value.item()
    return value

rows = [
    tuple(prepare_value(value) for value in row)
    for row in df[columns].itertuples(
        index=False, name=None
    )
]


try:
    batch_size = 500
    total_rows = len(rows)

    for start in range(0, total_rows, batch_size):
        batch = rows[start:start + batch_size]

        cursor.executemany(sql, batch)
        conn.commit()

        imported = min(start + batch_size, total_rows)
        print(f"Imported {imported} / {total_rows} rows")

    print("Import completed successfully!")

except Exception as error:
    try:
        conn.rollback()
    except Exception:
        pass

    print("Import failed:", error)

finally:
    try:
        cursor.close()
    except Exception:
        pass

    try:
        conn.close()
    except Exception:
        pass

