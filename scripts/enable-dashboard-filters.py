#!/usr/bin/env python3

import os
import requests

BASE_URL = os.getenv("METABASE_URL", "http://localhost:3000").rstrip("/")
EMAIL = os.getenv("METABASE_EMAIL")
PASSWORD = os.getenv("METABASE_PASSWORD")

DASHBOARD_ID = 2

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

# Get dashboard
response = session.get(
    f"{BASE_URL}/api/dashboard/{DASHBOARD_ID}",
    headers=headers,
    timeout=30,
)

if response.status_code != 200:
    raise SystemExit(
        f"DASHBOARD LOOKUP FAILED: "
        f"{response.status_code} {response.text}"
    )

dashboard = response.json()

print(f"Dashboard: {dashboard.get('name')}")
print(f"Dashboard ID: {DASHBOARD_ID}")
print()

# Display current dashboard cards
for item in dashboard.get("dashcards", []):
    card = item.get("card") or {}

    print(
        f"Card {card.get('id')}: "
        f"{card.get('name')}"
    )

print()
print("Dashboard is ready for filter configuration.")
print()
print("Planned filters:")
print("  1. Order Date")
print("  2. Region")
print("  3. Category")
print("  4. Customer Segment")
print()
print("No changes were made.")
