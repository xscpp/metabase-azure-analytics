#!/usr/bin/env python3

import os
import requests

BASE_URL = os.getenv("METABASE_URL", "http://localhost:3000").rstrip("/")
EMAIL = os.getenv("METABASE_EMAIL")
PASSWORD = os.getenv("METABASE_PASSWORD")

if not EMAIL or not PASSWORD:
    raise SystemExit(
        "ERROR: METABASE_EMAIL and METABASE_PASSWORD must be set"
    )

session = requests.Session()

# Login
login = session.post(
    f"{BASE_URL}/api/session",
    json={
        "username": EMAIL,
        "password": PASSWORD,
    },
    timeout=30,
)

if login.status_code != 200:
    raise SystemExit(f"LOGIN FAILED: {login.text}")

headers = {
    "X-Metabase-Session": login.json()["id"],
    "Content-Type": "application/json",
}

print("LOGIN OK")

# SQL queries with optional Metabase dashboard filters.
#
# Metabase variables:
#   {{order_date}}
#   {{region}}
#   {{category}}
#   {{segment}}
#
# Each optional filter is wrapped in [[ ... ]].
# If a filter is not selected, Metabase removes the entire block.

queries = {

    27: """
SELECT COALESCE(SUM("Sales"), 0) AS total_sales
FROM orders
WHERE 1=1
[[AND "Order Date" >= {{order_date}}]]
[[AND "Region" = {{region}}]]
[[AND "Category" = {{category}}]]
[[AND "Segment" = {{segment}}]];
""",

    28: """
SELECT COALESCE(SUM("Profit"), 0) AS total_profit
FROM orders
WHERE 1=1
[[AND "Order Date" >= {{order_date}}]]
[[AND "Region" = {{region}}]]
[[AND "Category" = {{category}}]]
[[AND "Segment" = {{segment}}]];
""",

    29: """
SELECT COUNT(DISTINCT "Order ID") AS total_orders
FROM orders
WHERE 1=1
[[AND "Order Date" >= {{order_date}}]]
[[AND "Region" = {{region}}]]
[[AND "Category" = {{category}}]]
[[AND "Segment" = {{segment}}]];
""",

    30: """
SELECT COUNT(DISTINCT "Customer ID") AS total_customers
FROM orders
WHERE 1=1
[[AND "Order Date" >= {{order_date}}]]
[[AND "Region" = {{region}}]]
[[AND "Category" = {{category}}]]
[[AND "Segment" = {{segment}}]];
""",

    31: """
SELECT
    "Region",
    SUM("Sales") AS sales
FROM orders
WHERE 1=1
[[AND "Order Date" >= {{order_date}}]]
[[AND "Region" = {{region}}]]
[[AND "Category" = {{category}}]]
[[AND "Segment" = {{segment}}]]
GROUP BY "Region"
ORDER BY sales DESC;
""",

    32: """
SELECT
    "Category",
    SUM("Sales") AS sales
FROM orders
WHERE 1=1
[[AND "Order Date" >= {{order_date}}]]
[[AND "Region" = {{region}}]]
[[AND "Category" = {{category}}]]
[[AND "Segment" = {{segment}}]]
GROUP BY "Category"
ORDER BY sales DESC;
""",

    33: """
SELECT
    "Order Date" AS order_date,
    SUM("Sales") AS sales
FROM orders
WHERE 1=1
[[AND "Order Date" >= {{order_date}}]]
[[AND "Region" = {{region}}]]
[[AND "Category" = {{category}}]]
[[AND "Segment" = {{segment}}]]
GROUP BY "Order Date"
ORDER BY "Order Date";
""",

    34: """
SELECT
    COUNT(DISTINCT o."Order ID") AS returned_orders
FROM orders o
INNER JOIN returns r
    ON o."Order ID" = r."Order ID"
WHERE 1=1
[[AND o."Order Date" >= {{order_date}}]]
[[AND o."Region" = {{region}}]]
[[AND o."Category" = {{category}}]]
[[AND o."Segment" = {{segment}}]];
"""
}

for card_id, query in queries.items():

    # Get existing card
    response = session.get(
        f"{BASE_URL}/api/card/{card_id}",
        headers=headers,
        timeout=30,
    )

    if response.status_code != 200:
        raise SystemExit(
            f"FAILED TO GET CARD {card_id}: "
            f"{response.status_code} {response.text}"
        )

    card = response.json()

    payload = {
        "dataset_query": {
            "type": "native",
            "native": {
                "query": query.strip(),
                "template-tags": {
                    "order_date": {
                        "id": "order_date",
                        "name": "order_date",
                        "display-name": "Order Date",
                        "type": "date"
                    },
                    "region": {
                        "id": "region",
                        "name": "region",
                        "display-name": "Region",
                        "type": "text"
                    },
                    "category": {
                        "id": "category",
                        "name": "category",
                        "display-name": "Category",
                        "type": "text"
                    },
                    "segment": {
                        "id": "segment",
                        "name": "segment",
                        "display-name": "Customer Segment",
                        "type": "text"
                    }
                }
            },
            "database": card["database_id"]
        }
    }

    update = session.put(
        f"{BASE_URL}/api/card/{card_id}",
        headers=headers,
        json=payload,
        timeout=30,
    )

    if update.status_code not in (200, 202):
        raise SystemExit(
            f"FAILED TO UPDATE CARD {card_id}: "
            f"{update.status_code} {update.text}"
        )

    print(f"UPDATED CARD {card_id}: {card['name']}")

print()
print("All filterable cards were updated.")
print()
print("IMPORTANT:")
print("The dashboard filters still need to be created and mapped.")
