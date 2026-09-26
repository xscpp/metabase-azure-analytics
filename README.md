# Metabase Azure Analytics

Analytics dashboard project deployed on an Azure Virtual Machine.

## Architecture

Internet
→ Nginx :80
→ Metabase :3000 (internal)

The Metabase port 3000 is not exposed through the Azure NSG.

## Azure

- Resource Group: METADB
- Virtual Machine: METADB
- Region: East US
- Metabase exposed through Nginx
- SSH: port 22
- HTTP: port 80

## Metabase

Dashboard:

- Project 7 - Analytics Dashboard

Dashboard components:

- Total Sales
- Total Profit
- Total Orders
- Total Customers
- Sales by Region
- Sales by Category
- Sales Trend
- Returned Orders
- Profit by Region
- Top 10 Products by Sales
- Orders table

Filters:

- Order Date
- Region
- Category
- Customer Segment

## Users

- Administrator
- Viewer

The Viewer account is intended for dashboard viewing rather than administration.

## Environment Variables

Copy `.env.example` to `.env` and set the required credentials.

Never commit `.env` or passwords to GitHub.

## Security

- Metabase is accessed through Nginx.
- Direct public access to port 3000 is disabled in the Azure NSG.
- SSH is available on port 22.
- HTTP is available on port 80.

## Backup

Dashboard and permissions backups are stored locally and excluded from Git.

## Access

Metabase is available through:

http://20.127.163.201/metabase/
