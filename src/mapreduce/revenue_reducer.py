#!/usr/bin/env python3
import sys

current_country = None
total_revenue = 0.0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    try:
        country, revenue = line.rsplit(maxsplit=1)
        revenue = float(revenue)
    except ValueError:
        continue

    if current_country == country:
        total_revenue += revenue
    else:
        if current_country is not None:
            print(f"{current_country}\t{total_revenue:.2f}")

        current_country = country
        total_revenue = revenue

if current_country is not None:
    print(f"{current_country}\t{total_revenue:.2f}")
