from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = Path("dataset/raw/online_retail.csv")
OUT = Path("plots")
OUT.mkdir(parents=True, exist_ok=True)

if not DATA.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA.resolve()}. Run from project root.")

df = pd.read_csv(DATA, dtype={"InvoiceNo": str, "StockCode": str})
required = {"InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

valid = df.dropna(subset=["InvoiceNo", "InvoiceDate", "Country", "Quantity", "UnitPrice"]).copy()
valid["InvoiceNo"] = valid["InvoiceNo"].astype(str).str.strip()
valid["Country"] = valid["Country"].astype(str).str.strip()
valid["Description"] = valid["Description"].fillna("Unknown product").astype(str).str.strip()

sales = valid[
    (~valid["InvoiceNo"].str.upper().str.startswith("C", na=False))
    & (valid["Quantity"] > 0)
    & (valid["UnitPrice"] > 0)
].copy()
if sales.empty:
    raise ValueError("No positive-sales rows remain after cleaning.")

def save_plot(filename):
    plt.tight_layout()
    plt.savefig(OUT / filename, dpi=160, bbox_inches="tight")
    plt.close()
    print("Saved:", OUT / filename)

country_revenue = sales.groupby("Country")["Revenue"].sum().sort_values(ascending=False)
country_invoices = sales.groupby("Country")["InvoiceNo"].nunique().sort_values(ascending=False)
product_revenue = sales.groupby("Description")["Revenue"].sum().sort_values(ascending=False)
product_quantity = sales.groupby("Description")["Quantity"].sum().sort_values(ascending=False)
monthly_revenue = sales.set_index("InvoiceDate")["Revenue"].resample("MS").sum()
monthly_invoices = sales.set_index("InvoiceDate")["InvoiceNo"].resample("MS").nunique()
monthly_aov = (monthly_revenue / monthly_invoices.replace(0, float("nan"))).fillna(0)

# 01: Country revenue
ax = country_revenue.head(10).sort_values().plot(kind="barh", figsize=(10, 6), title="Top 10 Countries by Sales Revenue")
ax.set_xlabel("Revenue (dataset currency units)")
ax.set_ylabel("Country")
save_plot("01_country_revenue.png")

# 02: Monthly revenue
ax = monthly_revenue.plot(figsize=(11, 5), marker="o", title="Monthly Sales Revenue Trend")
ax.set_xlabel("Invoice month")
ax.set_ylabel("Revenue (dataset currency units)")
ax.grid(True, alpha=0.25)
save_plot("02_monthly_revenue.png")

# 03: Product revenue
ax = product_revenue.head(10).sort_values().plot(kind="barh", figsize=(10, 6), title="Top 10 Products by Sales Revenue")
ax.set_xlabel("Revenue (dataset currency units)")
ax.set_ylabel("Product")
save_plot("03_product_revenue.png")

# 04: Units sold
ax = product_quantity.head(10).sort_values().plot(kind="barh", figsize=(10, 6), title="Top 10 Products by Units Sold")
ax.set_xlabel("Units sold")
ax.set_ylabel("Product")
save_plot("04_product_quantity.png")

# 05: Invoice volume by country
ax = country_invoices.head(10).sort_values().plot(kind="barh", figsize=(10, 6), title="Top 10 Countries by Invoice Count")
ax.set_xlabel("Distinct invoices")
ax.set_ylabel("Country")
save_plot("05_country_transactions.png")

# 06: Country revenue vs invoice volume
country_metrics = sales.groupby("Country").agg(Revenue=("Revenue", "sum"), Invoices=("InvoiceNo", "nunique"))
plt.figure(figsize=(9, 6))
plt.scatter(country_metrics["Invoices"], country_metrics["Revenue"], alpha=0.7)
plt.title("Country Revenue vs. Number of Invoices")
plt.xlabel("Distinct invoices")
plt.ylabel("Revenue (dataset currency units)")
plt.grid(True, alpha=0.25)
save_plot("06_revenue_vs_transactions.png")

# 07: Monthly invoice volume
ax = monthly_invoices.plot(figsize=(11, 5), marker="o", title="Monthly Invoice Volume")
ax.set_xlabel("Invoice month")
ax.set_ylabel("Distinct invoices")
ax.grid(True, alpha=0.25)
save_plot("07_monthly_invoice_volume.png")

# 08: Monthly average order value
ax = monthly_aov.plot(figsize=(11, 5), marker="o", title="Monthly Average Order Value (AOV)")
ax.set_xlabel("Invoice month")
ax.set_ylabel("Revenue per invoice")
ax.grid(True, alpha=0.25)
save_plot("08_monthly_average_order_value.png")

# 09: Country revenue concentration (Pareto-style)
top_country = country_revenue.head(10)
cumulative_share = top_country.cumsum() / country_revenue.sum() * 100
fig, ax1 = plt.subplots(figsize=(11, 6))
top_country.plot(kind="bar", ax=ax1, alpha=0.8)
ax1.set_ylabel("Revenue")
ax1.set_xlabel("Country")
ax1.set_title("Revenue Concentration: Top 10 Countries")
ax1.tick_params(axis="x", rotation=45)
ax2 = ax1.twinx()
ax2.plot(range(len(cumulative_share)), cumulative_share.values, marker="o")
ax2.set_ylabel("Cumulative share of all country revenue (%)")
ax2.set_ylim(0, 105)
save_plot("09_country_revenue_concentration.png")

# 10: Cancellation-style invoice IDs by month
cancel_rows = valid[valid["InvoiceNo"].str.upper().str.startswith("C", na=False)].copy()
if len(cancel_rows):
    cancel_monthly = cancel_rows.set_index("InvoiceDate")["InvoiceNo"].resample("MS").nunique()
else:
    cancel_monthly = pd.Series(dtype="int64")
ax = cancel_monthly.plot(figsize=(11, 5), marker="o", title="Cancellation-Style Invoice IDs by Month")
ax.set_xlabel("Invoice month")
ax.set_ylabel("Distinct invoice IDs beginning with C")
ax.grid(True, alpha=0.25)
save_plot("10_cancellation_invoice_trend.png")

# 11: Negative quantity rows by month; not all are necessarily confirmed returns
negative_lines = valid[valid["Quantity"] < 0].copy()
if len(negative_lines):
    negative_monthly = negative_lines.set_index("InvoiceDate")["Quantity"].resample("MS").count()
else:
    negative_monthly = pd.Series(dtype="int64")
ax = negative_monthly.plot(figsize=(11, 5), marker="o", title="Negative-Quantity Line Items by Month")
ax.set_xlabel("Invoice month")
ax.set_ylabel("Count of negative-quantity rows")
ax.grid(True, alpha=0.25)
save_plot("11_negative_quantity_trend.png")

# 12: Revenue by weekday
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
sales["Weekday"] = sales["InvoiceDate"].dt.day_name()
weekday_revenue = sales.groupby("Weekday")["Revenue"].sum().reindex(weekday_order).fillna(0)
ax = weekday_revenue.plot(kind="bar", figsize=(10, 5), title="Sales Revenue by Day of Week")
ax.set_xlabel("Day of week")
ax.set_ylabel("Revenue (dataset currency units)")
ax.tick_params(axis="x", rotation=30)
save_plot("12_weekday_revenue.png")

# 13: Units sold versus revenue for top 30 products
product_metrics = sales.groupby("Description").agg(Revenue=("Revenue", "sum"), Units=("Quantity", "sum"))
top_products = product_metrics.nlargest(30, "Revenue")
plt.figure(figsize=(9, 6))
plt.scatter(top_products["Units"], top_products["Revenue"], alpha=0.75)
plt.title("Top 30 Products: Units Sold vs. Revenue")
plt.xlabel("Units sold")
plt.ylabel("Revenue (dataset currency units)")
plt.grid(True, alpha=0.25)
save_plot("13_product_units_vs_revenue.png")

cancelled_ids = valid.loc[valid["InvoiceNo"].str.upper().str.startswith("C", na=False), "InvoiceNo"].nunique()
negative_quantity_rows = int((valid["Quantity"] < 0).sum())
negative_line_value = float(valid.loc[valid["Quantity"] < 0, "Revenue"].sum())
top5_share = country_revenue.head(5).sum() / country_revenue.sum() * 100 if country_revenue.sum() else 0
top10_share = country_revenue.head(10).sum() / country_revenue.sum() * 100 if country_revenue.sum() else 0

summary = [
    "E-COMMERCE TRANSACTION ANALYSIS SUMMARY",
    "=======================================",
    f"Raw rows: {len(df):,}",
    f"Rows with valid invoice/date/country/quantity/price: {len(valid):,}",
    f"Rows included in positive-sales analysis: {len(sales):,}",
    f"Distinct countries in positive-sales analysis: {sales['Country'].nunique():,}",
    f"Distinct invoices in positive-sales analysis: {sales['InvoiceNo'].nunique():,}",
    f"Distinct product codes in positive-sales analysis: {sales['StockCode'].nunique():,}",
    f"Distinct product descriptions in positive-sales analysis: {sales['Description'].nunique():,}",
    f"Positive-sales revenue (positive quantity/price, non-C invoices): {sales['Revenue'].sum():,.2f}",
    f"Distinct cancellation-style invoice IDs (beginning with C): {cancelled_ids:,}",
    f"Rows with negative quantity: {negative_quantity_rows:,}",
    f"Sum of revenue values on negative-quantity rows: {negative_line_value:,.2f}",
    f"Top 5 countries' share of positive-sales revenue: {top5_share:.2f}%",
    f"Top 10 countries' share of positive-sales revenue: {top10_share:.2f}%",
    "",
    "Top 5 countries by positive-sales revenue:",
    country_revenue.head(5).to_string(),
    "",
    "Top 5 products by positive-sales revenue:",
    product_revenue.head(5).to_string(),
    "",
    "Top 5 products by units sold:",
    product_quantity.head(5).to_string(),
    "",
    "Monthly revenue peak:",
    f"{monthly_revenue.idxmax().strftime('%Y-%m')}: {monthly_revenue.max():,.2f}" if len(monthly_revenue) else "Not available",
    "",
    "Metric definitions:",
    "- Line revenue = Quantity * UnitPrice.",
    "- Positive-sales analysis excludes invoice IDs beginning with C, non-positive quantities, and non-positive prices.",
    "- Cancellation-style invoice IDs are identified by an invoice number beginning with C.",
    "- Negative-quantity rows are analysed separately and are not necessarily all confirmed returns.",
    "- AOV = positive-sales revenue for a month / distinct positive-sales invoices for that month.",
    "- No currency conversion is applied; values use the dataset's recorded price units."
]
(OUT / "analysis_summary.txt").write_text("\n".join(summary), encoding="utf-8")
print("\n".join(summary))
print(f"\nAll charts and summary saved in: {OUT.resolve()}")
