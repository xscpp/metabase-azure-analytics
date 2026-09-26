#!/usr/bin/env python3

import os
import sys
import json
import requests

BASE_URL = os.getenv("METABASE_URL", "http://localhost:3000").rstrip("/")
EMAIL = os.getenv("METABASE_EMAIL")
PASSWORD = os.getenv("METABASE_PASSWORD")

if not EMAIL or not PASSWORD:
    print("ERROR: Set METABASE_EMAIL and METABASE_PASSWORD first.")
    sys.exit(1)


def api(method, path, **kwargs):
    url = f"{BASE_URL}{path}"
    response = requests.request(method, url, timeout=30, **kwargs)

    if not response.ok:
        print(f"API ERROR {response.status_code}: {response.text}")
        sys.exit(1)

    if response.text:
        return response.json()

    return None


# ---------------------------------------------------------
# 1. Login
# ---------------------------------------------------------

print("Logging into Metabase...")

session = api(
    "POST",
    "/api/session",
    json={
        "username": EMAIL,
        "password": PASSWORD,
    },
)

session_id = session["id"]

HEADERS = {
    "X-Metabase-Session": session_id,
    "Content-Type": "application/json",
}

print("Login successful.")


# ---------------------------------------------------------
# 2. Find Analytics PostgreSQL database
# ---------------------------------------------------------

print("Finding Analytics PostgreSQL database...")

databases = api(
    "GET",
    "/api/database",
    headers=HEADERS,
)

database = None

for db in databases.get("data", []):
    name = (db.get("name") or "").lower()

    if "analytics" in name:
        database = db
        break

if not database:
    print("ERROR: Could not find Analytics PostgreSQL database.")
    print("Available databases:")

    for db in databases.get("data", []):
        print(f"  {db.get('id')}: {db.get('name')}")

    sys.exit(1)

DATABASE_ID = database["id"]

print(
    f"Using database: {database['name']} "
    f"(ID {DATABASE_ID})"
)


# ---------------------------------------------------------
# 3. Find/create collection
# ---------------------------------------------------------

print("Finding dashboard collection...")

collections = api(
    "GET",
    "/api/collection",
    headers=HEADERS,
)

collection = None

for c in collections:
    if c.get("name") == "Project 7 Analytics":
        collection = c
        break

if not collection:
    print("Creating collection...")

    collection = api(
        "POST",
        "/api/collection",
        headers=HEADERS,
        json={
            "name": "Project 7 Analytics",
            "description": "Internal Analytics and Reporting Platform",
        },
    )

COLLECTION_ID = collection["id"]

print(f"Collection ID: {COLLECTION_ID}")


# ---------------------------------------------------------
# 4. SQL Questions
# ---------------------------------------------------------

questions = [
    {
        "name": "KPI - Total Sales",
        "sql": """
SELECT COALESCE(SUM(sales), 0) AS total_sales
FROM orders;
""",
    },
    {
        "name": "KPI - Total Profit",
        "sql": """
SELECT COALESCE(SUM(profit), 0) AS total_profit
FROM orders;
""",
    },
    {
        "name": "KPI - Total Orders",
        "sql": """
SELECT COUNT(DISTINCT "Order ID") AS total_orders
FROM orders;
""",
    },
    {
        "name": "KPI - Total Customers",
        "sql": """
SELECT COUNT(DISTINCT "Customer ID") AS total_customers
FROM orders;
""",
    },
    {
        "name": "Sales by Region",
        "sql": """
SELECT
    "Region",
    SUM(sales) AS sales
FROM orders
GROUP BY "Region"
ORDER BY sales DESC;
""",
    },
    {
        "name": "Sales by Category",
        "sql": """
SELECT
    "Category",
    SUM(sales) AS sales
FROM orders
GROUP BY "Category"
ORDER BY sales DESC;
""",
    },
    {
        "name": "Sales Trend",
        "sql": """
SELECT
    "Order Date" AS order_date,
    SUM(sales) AS sales
FROM orders
GROUP BY "Order Date"
ORDER BY "Order Date";
""",
    },
    {
        "name": "Returned Orders",
        "sql": """
SELECT
    COUNT(DISTINCT o."Order ID") AS returned_orders
FROM orders o
INNER JOIN returns r
    ON o."Order ID" = r."Order ID";
""",
    },
]


# ---------------------------------------------------------
# 5. Create Questions
# ---------------------------------------------------------

print("Creating questions...")

card_ids = []

for question in questions:

    payload = {
        "name": question["name"],
        "collection_id": COLLECTION_ID,
        "dataset_query": {
            "type": "native",
            "native": {
                "query": question["sql"],
            },
            "database": DATABASE_ID,
        },
        "display": "scalar",
        "visualization_settings": {},
    }

    card = api(
        "POST",
        "/api/card",
        headers=HEADERS,
        json=payload,
    )

    card_id = card["id"]

    card_ids.append(
        {
            "id": card_id,
            "name": question["name"],
        }
    )

    print(f"Created: {question['name']} -> {card_id}")


# ---------------------------------------------------------
# 6. Create Dashboard
# ---------------------------------------------------------

print("Creating dashboard...")

dashboard = api(
    "POST",
    "/api/dashboard",
    headers=HEADERS,
    json={
        "name": "Project 7 - Analytics Dashboard",
        "description": (
            "Internal analytics dashboard for sales, "
            "profit, customers, orders and returns."
        ),
        "collection_id": COLLECTION_ID,
    },
)

DASHBOARD_ID = dashboard["id"]

print(f"Dashboard created: {DASHBOARD_ID}")


# ---------------------------------------------------------
# 7. Add cards to dashboard
# ---------------------------------------------------------

print("Adding cards to dashboard...")

# Simple grid layout
positions = [
    (0, 0, 6, 4),
    (6, 0, 6, 4),
    (12, 0, 6, 4),
    (18, 0, 6, 4),
    (0, 4, 12, 8),
    (12, 4, 12, 8),
    (0, 12, 18, 8),
    (18, 12, 6, 8),
]

dashcards = []

for index, card in enumerate(card_ids):

    x, y, w, h = positions[index]

    dashcards.append(
        {
            "id": -1 - index,
            "card_id": card["id"],
            "row": y,
            "col": x,
            "size_x": w,
            "size_y": h,
        }
    )


api(
    "PUT",
    f"/api/dashboard/{DASHBOARD_ID}",
    headers=HEADERS,
    json={
        "name": "Project 7 - Analytics Dashboard",
        "description": (
            "Internal analytics dashboard for sales, "
            "profit, customers, orders and returns."
        ),
        "dashcards": dashcards,
    },
)


# ---------------------------------------------------------
# 8. Output
# ---------------------------------------------------------

print()
print("=" * 60)
print("Dashboard setup completed.")
print("=" * 60)
print()
print(f"Metabase:  {BASE_URL}")
print(
    f"Dashboard: {BASE_URL}/dashboard/{DASHBOARD_ID}"
)
print()
print("Cards created:")

for card in card_ids:
    print(f"  {card['id']} - {card['name']}")

print()
print("IMPORTANT:")
print("The dashboard was created through the Metabase API.")
print("Filters can be added after verifying the dashboard.")
