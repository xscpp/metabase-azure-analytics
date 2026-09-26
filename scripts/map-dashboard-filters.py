import requests
import os
import sys
import json

BASE_URL = os.environ["METABASE_URL"].rstrip("/")
EMAIL = os.environ["METABASE_EMAIL"]
PASSWORD = os.environ["METABASE_PASSWORD"]

DASHBOARD_ID = 2

FILTERS = {
    "order_date": {
        "date_from": "date_from",
        "date_to": "date_to",
    },
    "region": {
        "tag": "region",
    },
    "category": {
        "tag": "category",
    },
    "customer_segment": {
        "tag": "segment",
    },
}

CARD_IDS = [27, 28, 29, 30, 31, 32, 33, 34]


def fail(message):
    print(message)
    sys.exit(1)


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
    fail("LOGIN FAILED: " + login.text)

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
    fail("FAILED TO GET DASHBOARD: " + r.text)

dashboard = r.json()

print(f"Dashboard: {dashboard.get('name')}")
print(f"Dashboard ID: {DASHBOARD_ID}")


# ------------------------------------------------------------
# Build parameter mappings
# ------------------------------------------------------------

def build_mappings(card_id):

    mappings = []

    # Date range
    mappings.append({
        "parameter_id": "order_date",
        "card_id": card_id,
        "target": [
            "variable",
            [
                "template-tag",
                "date_from"
            ]
        ]
    })

    mappings.append({
        "parameter_id": "order_date",
        "card_id": card_id,
        "target": [
            "variable",
            [
                "template-tag",
                "date_to"
            ]
        ]
    })

    # Region
    mappings.append({
        "parameter_id": "region",
        "card_id": card_id,
        "target": [
            "variable",
            [
                "template-tag",
                "region"
            ]
        ]
    })

    # Category
    mappings.append({
        "parameter_id": "category",
        "card_id": card_id,
        "target": [
            "variable",
            [
                "template-tag",
                "category"
            ]
        ]
    })

    # Customer Segment
    mappings.append({
        "parameter_id": "customer_segment",
        "card_id": card_id,
        "target": [
            "variable",
            [
                "template-tag",
                "segment"
            ]
        ]
    })

    return mappings


# ------------------------------------------------------------
# Update dashcards locally
# ------------------------------------------------------------

dashcards = dashboard.get("dashcards", [])

updated = 0

for dashcard in dashcards:

    card_id = dashcard.get("card_id")

    if card_id not in CARD_IDS:
        continue

    mappings = build_mappings(card_id)

    dashcard["parameter_mappings"] = mappings

    if "card" in dashcard:
        dashcard["card"]["parameter_mappings"] = mappings

    updated += 1

    print(f"Prepared CARD {card_id}")


if updated != len(CARD_IDS):
    print(
        f"WARNING: Found {updated} matching cards, "
        f"expected {len(CARD_IDS)}."
    )


# ------------------------------------------------------------
# Prepare dashboard update
# ------------------------------------------------------------

payload = {
    "name": dashboard.get("name"),
    "description": dashboard.get("description"),
    "parameters": dashboard.get("parameters", []),
    "dashcards": dashcards,
}


# ------------------------------------------------------------
# Update dashboard
# ------------------------------------------------------------

r = session.put(
    f"{BASE_URL}/api/dashboard/{DASHBOARD_ID}",
    headers=headers,
    json=payload,
    timeout=60,
)

print()
print("Dashboard update status:", r.status_code)

if r.status_code not in (200, 202):
    print(r.text)
    fail("Dashboard update failed.")


print()
print("=" * 60)
print("Dashboard filter mappings submitted.")
print("=" * 60)


# ------------------------------------------------------------
# Verify
# ------------------------------------------------------------

r = session.get(
    f"{BASE_URL}/api/dashboard/{DASHBOARD_ID}",
    headers=headers,
    timeout=30,
)

if r.status_code != 200:
    fail("Verification failed: " + r.text)

verified = r.json()

print()
print("VERIFICATION")
print("=" * 60)

total_mappings = 0

for dashcard in verified.get("dashcards", []):

    card_id = dashcard.get("card_id")

    if card_id not in CARD_IDS:
        continue

    mappings = dashcard.get("parameter_mappings", [])

    print(
        f"Card {card_id}: "
        f"{dashcard.get('card', {}).get('name')} "
        f"-> {len(mappings)} mappings"
    )

    total_mappings += len(mappings)


print()
print(f"TOTAL MAPPINGS: {total_mappings}")

if total_mappings == 0:
    print()
    print("WARNING: Metabase did not persist the mappings.")
else:
    print()
    print("Dashboard filter mapping verification completed.")
