#!/usr/bin/env python3
import sys
import csv

reader = csv.reader(sys.stdin)

for row in reader:
    if len(row) < 8:
        continue

    if row[0] == "InvoiceNo":
        continue

    try:
        quantity = float(row[3])
        unit_price = float(row[5])
        country = row[7].strip()

        if country:
            revenue = quantity * unit_price
            print(f"{country}\t{revenue:.2f}")
    except (ValueError, IndexError):
        continue
