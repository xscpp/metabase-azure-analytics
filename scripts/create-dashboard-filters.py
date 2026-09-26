#!/usr/bin/env python3

import os
import requests
import sys

BASE_URL = os.getenv("METABASE_URL", "http://localhost:3000").rstrip("/")
EMAIL = os.getenv("METABASE_EMAIL")
PASSWORD = os.getenv("METABASE_PASSWORD")
DASHBOARD_ID = 2

if not EMAIL or not PASSWORD:
    print("ERROR: METABASE_EMAIL and METABASE_PASSWORD must be set.")
    sys.exit(1)

session = requests.Session()

# ------------------------------------------------------------
# Login
# ------------------------------------------------------------

login = session.post(
    f"{BASE_URL}/api/session",
    json={
        "username": EMAIL,
        "password": PASSWORD,
    },
    timeout=30,
)

if login.status_code != 200:
    print("LOGIN FAILED:", login.text)
    sys.exit(1)

session_id = login.json()["id"]

headers = {
    "X-Metabase-Session": session_id,
    "Content-Type": "application/json",
}

print("LOGIN OK")

# ------------------------------------------------------------
# Get dashboard
# ------------------------------------------------------------

r = session.get(
    f"{BASE_URL}/api/dashboard/{DASHBOARD_ID}",
    headers=headers,
    timeout=30,
)

if r.status_code != 200:
    print("FAILED TO GET DASHBOARD:", r.text)
    sys.exit(1)

dashboard = r.json()

print(f"Dashboard: {dashboard.get('name')}")
print(f"Dashboard ID: {DASHBOARD_ID}")

# ------------------------------------------------------------
# Existing dashboard parameters
# ------------------------------------------------------------

parameters = dashboard.get("parameters", [])

print("\nExisting parameters:")
for p in parameters:
    print(
        f"  {p.get('id')} | "
        f"{p.get('name')} | "
        f"{p.get('type')}"
    )

# ------------------------------------------------------------
# Create dashboard filters
# ------------------------------------------------------------

filters = [
    {
        "id": "order_date",
        "name": "Order Date",
        "slug": "order_date",
        "type": "date/all-options",
        "sectionId": "date",
    },
    {
        "id": "region",
        "name": "Region",
        "slug": "region",
        "type": "string/=",
        "sectionId": "string",
    },
    {
        "id": "category",
        "name": "Category",
        "slug": "category",
        "type": "string/=",
        "sectionId": "string",
    },
    {
        "id": "customer_segment",
        "name": "Customer Segment",
        "slug": "customer_segment",
        "type": "string/=",
        "sectionId": "string",
    },
]

# ------------------------------------------------------------
# Metabase dashboard parameter format
# ------------------------------------------------------------

new_parameters = []

for f in filters:
    new_parameters.append({
        "id": f["id"],
        "name": f["name"],
        "slug": f["slug"],
        "type": f["type"],
        "sectionId": f["sectionId"],
    })

# ------------------------------------------------------------
# Update dashboard
# ------------------------------------------------------------

payload = {
    "parameters": new_parameters
}

update = session.put(
    f"{BASE_URL}/api/dashboard/{DASHBOARD_ID}",
    headers=headers,
    json=payload,
    timeout=30,
)

print("\nDashboard update status:", update.status_code)

if update.status_code not in (200, 202):
    print("UPDATE FAILED:")
    print(update.text)
    sys.exit(1)

print("Dashboard filters created.")

# ------------------------------------------------------------
# Verify
# ------------------------------------------------------------

verify = session.get(
    f"{BASE_URL}/api/dashboard/{DASHBOARD_ID}",
    headers=headers,
    timeout=30,
)

if verify.status_code != 200:
    print("VERIFICATION FAILED:", verify.text)
    sys.exit(1)

result = verify.json()

print("\n============================================================")
print("DASHBOARD FILTERS")
print("============================================================")

for p in result.get("parameters", []):
    print(
        f"- {p.get('name')} "
        f"| ID: {p.get('id')} "
        f"| Type: {p.get('type')}"
    )

print("\n============================================================")
print("DONE")
print("============================================================")
print(f"Dashboard: {BASE_URL}/dashboard/{DASHBOARD_ID}")
