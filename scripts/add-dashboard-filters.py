#!/usr/bin/env python3

import os
import requests

BASE_URL = os.getenv("METABASE_URL", "http://localhost:3000").rstrip("/")
EMAIL = os.getenv("METABASE_EMAIL")
PASSWORD = os.getenv("METABASE_PASSWORD")

if not EMAIL or not PASSWORD:
    raise SystemExit("ERROR: METABASE_EMAIL and METABASE_PASSWORD must be set")

session = requests.Session()

login = session.post(
    BASE_URL + "/api/session",
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

# Real Metabase dashboard
dashboard_id = 2

# Verify that the dashboard exists
response = session.get(
    f"{BASE_URL}/api/dashboard/{dashboard_id}",
    headers=headers,
    timeout=30,
)

if response.status_code != 200:
    raise SystemExit(
        f"DASHBOARD LOOKUP FAILED: "
        f"{response.status_code} {response.text}"
    )

dashboard = response.json()

print("Dashboard:", dashboard.get("name"))
print("Dashboard ID:", dashboard_id)
print()
print("Cards:")

for item in dashboard.get("dashcards", []):
    card = item.get("card") or {}

    print(
        f"  {card.get('id')}: "
        f"{card.get('name')} "
        f"[{card.get('display')}]"
    )

print()
print("Dashboard verification completed successfully.")
print("Next step: create and connect dashboard filters.")

