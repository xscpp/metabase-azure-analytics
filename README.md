# Internal Analytics & Reporting Platform (Metabase on Azure)

A self-service business intelligence platform built with **Metabase**, deployed to **Microsoft Azure**
using **Terraform**, **Bash automation**, and **Docker Compose**.

Business users (sales, ops, finance, product, leadership) get a simple web interface to explore data,
build dashboards, and track KPIs — without needing SQL or a dedicated report developer for every request.

## Architecture

```
                     ┌─────────────────────────────┐
                     │           Azure              │
                     │  ┌────────────────────────┐  │
   Business Users ───┼─▶│  Ubuntu VM               │  │
   (browser :3000)   │  │  ┌──────────┐ ┌────────┐│  │
                     │  │  │ Metabase │▶│Postgres││  │
                     │  │  │ (docker) │ │(docker)││  │
                     │  │  └──────────┘ └────────┘│  │
                     │  │       persistent data    │  │
                     │  │       disk (/data)        │  │
                     │  └────────────────────────┘  │
                     │  NSG: allows 22, 3000, 443    │
                     └─────────────────────────────┘
```

- **Terraform** provisions the resource group, virtual network, NSG, public IP, VM, and a persistent data disk.
- **Bash scripts** install Docker, sync files to the VM, start the stack, and check health.
- **Docker Compose** runs two containers: Metabase (the BI app) and Postgres (Metabase's own metadata store).

## Repository layout

```
.
├── terraform/              # Azure infrastructure as code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── cloud-init.sh.tpl   # runs once on first VM boot (installs Docker)
│   └── terraform.tfvars.example
├── docker/                 # The application stack
│   ├── docker-compose.yml
│   └── .env.example
├── scripts/                 # Automation
│   ├── install-docker.sh
│   ├── deploy.sh
│   ├── health-check.sh
│   └── cleanup.sh
├── docs/
│   ├── DEPLOYMENT.md        # full step-by-step first-time walkthrough
│   └── TROUBLESHOOTING.md
└── .github/workflows/       # optional CI checks (terraform fmt/validate)
```

## Quick start

See **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for the complete first-time, step-by-step guide
(installing tools, Azure login, Terraform apply, first deploy). Short version:

```bash
# 1. Infrastructure
cd terraform
cp terraform.tfvars.example terraform.tfvars   # edit with your values
terraform init
terraform apply

# 2. Application
cd ../docker
cp .env.example .env                            # edit with a real password
cd ..
./scripts/deploy.sh <vm_public_ip>

# 3. Open Metabase
# http://<vm_public_ip>:3000
```

## Sample business workflow

1. A department connects its operational database (or uploads a CSV) inside Metabase.
2. Business users build questions and dashboards for sales, support, or service health.
3. Filters/segments answer routine operational questions without engineering involvement.
4. Leadership reviews dashboards for decision-making.
5. Teams track KPIs over time using a consistent, shared reporting layer.

## Security notes

- Restrict `allowed_ssh_cidr` and `allowed_metabase_cidr` in `terraform.tfvars` to your own IP/VPN — do not leave them open to the internet in real use.
- Never commit `docker/.env` or `terraform/terraform.tfvars` — both are already in `.gitignore`.
- Put Metabase behind HTTPS (e.g. a reverse proxy with Let's Encrypt, or Azure Application Gateway) before giving it to real users; port 3000 plain HTTP is fine for a first internal test only.

## Static analytics dashboard (free, no Azure required)

Alongside Metabase, `dashboard/` contains a free, zero-dependency static dashboard:
`build.py` injects your `csv/orders.csv`, `csv/returns.csv`, `csv/people.csv` into
`dashboard/index.template.html`, producing a single self-contained `dashboard/dist/index.html`
with a custom professional design (KPI cards, charts, filters, sortable orders table).

```bash
python3 dashboard/build.py
```

No server, no database, no cost — host it for free on GitHub Pages, or drop it on the same
Azure VM as Metabase if you're already paying for that. See **[dashboard/README.md](dashboard/README.md)**
for exactly where to put your CSVs and how to publish it for free.

## Out of scope (v1)

- Enterprise-wide semantic layer
- Complex data governance platform integration
- Multi-region deployment
