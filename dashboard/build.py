#!/usr/bin/env python3
"""Build the Nabd dashboard: inject data from csv/ into index.template.html -> dist/index.html.

Reads:  orders.csv (order + line-item grain), returns.csv (Order ID, Returned),
        people.csv (Regional Manager, Region)
Usage:  python3 dashboard/build.py [--csv csv] [--out dashboard/dist/index.html]
Env:    CURRENCY (default USD)
Re-run whenever the CSV data changes. No third-party packages required.
"""
import argparse, csv, json, os
from pathlib import Path

here = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--csv', default=str(here.parent / 'csv'))
ap.add_argument('--out', default=str(here / 'dist' / 'index.html'))
args = ap.parse_args()

def rows(name):
    with open(Path(args.csv) / f'{name}.csv', newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

num = lambda v: float(v) if v not in ('', None) else None

order_rows = rows('orders')
return_rows = rows('returns')
people_rows = rows('people')

returned_ids = {r['Order ID'] for r in return_rows if r.get('Returned', '').strip().lower() == 'yes'}
managers = {r['Region']: r['Regional Manager'] for r in people_rows}

# Dedupe customers / products (order grain repeats them per line item).
customers_map, products_map, orders_map = {}, {}, {}
items = []

for r in order_rows:
    cid = r['Customer ID']
    if cid not in customers_map:
        customers_map[cid] = [cid, r['Customer Name'], r['Segment']]

    pid = r['Product ID']
    if pid not in products_map:
        products_map[pid] = [pid, r['Product Name'], r['Category'], r['Sub-Category']]

    oid = r['Order ID']
    if oid not in orders_map:
        orders_map[oid] = [oid, cid, r['Order Date'], r['Ship Date'], r['Ship Mode'],
                            r['Region'], r['State/Province'], r['City'],
                            1 if oid in returned_ids else 0]

    items.append([oid, pid, num(r['Sales']), int(num(r['Quantity']) or 0),
                  num(r['Discount']), num(r['Profit'])])

dates = [o[2] for o in orders_map.values()]
data = {
    'meta': {
        'minDate': min(dates), 'maxDate': max(dates),
        'currency': os.environ.get('CURRENCY', 'USD'),
        'managers': managers,
    },
    'customers': list(customers_map.values()),
    'products': list(products_map.values()),
    'orders': list(orders_map.values()),
    'items': items,
}

html = (here / 'index.template.html').read_text(encoding='utf-8')
marker = '/*__DATA__*/null'
assert marker in html, 'template marker missing'
out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html.replace(marker, json.dumps(data, ensure_ascii=False, separators=(',', ':'))), encoding='utf-8')
print(f'Built {out} ({out.stat().st_size/1024:.0f} KB): '
      f'{len(orders_map)} orders, {len(items)} line items, '
      f'{len(customers_map)} customers, {len(products_map)} products, '
      f"up to {data['meta']['maxDate']}")
