import pandas as pd

source = "dataset/raw/Online Retail.xlsx"
destination = "dataset/raw/online_retail.csv"

df = pd.read_excel(source, engine="openpyxl")
df.to_csv(destination, index=False, encoding="utf-8")

print("Rows:", len(df))
print("Columns:", list(df.columns))
print("CSV created:", destination)
