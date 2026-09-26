# Deployment Guide (First-Time Walkthrough)

This guide assumes you have never used Azure or Terraform before. Follow it in order.

## 0. Accounts you need

- An **Azure account** with an active subscription (free trial works): https://azure.microsoft.com
- A **GitHub account** (you likely already have one)

## 1. Install required tools (on your own laptop/PC)

| Tool | Check if installed | Install |
|---|---|---|
| Azure CLI | `az --version` | https://learn.microsoft.com/cli/azure/install-azure-cli |
| Terraform | `terraform -version` | https://developer.hashicorp.com/terraform/install |
| Git | `git --version` | https://git-scm.com/downloads |
| SSH key pair | `ls ~/.ssh/id_rsa.pub` | if missing: `ssh-keygen -t rsa -b 4096` |

## 2. Log in to Azure

```bash
az login
```

This opens a browser to sign in. After logging in, confirm your subscription:

```bash
az account show
```

If you have more than one subscription, set the right one:
```bash
az account set --subscription "<subscription-id-or-name>"
```

## 3. Push this project to GitHub

```bash
cd metabase-azure-analytics
git init
git add .
git commit -m "Initial commit: Metabase on Azure analytics platform"

# Create an empty repo on GitHub first (via github.com -> New repository), then:
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git branch -M main
git push -u origin main
```

> Because `docker/.env` and `terraform/terraform.tfvars` are in `.gitignore`, your passwords
> and secrets will NOT be pushed to GitHub. Good — keep it that way.

## 4. Provision Azure infrastructure with Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
- Set `location` to an Azure region near you (e.g. `"uaenorth"`, `"westeurope"`).
- Find your public IP with `curl ifconfig.me` and set `allowed_ssh_cidr` and `allowed_metabase_cidr` to `"<your-ip>/32"` instead of `0.0.0.0/0`.
- Point `ssh_public_key_path` to your real key, e.g. `"~/.ssh/id_rsa.pub"`.

Then run:

```bash
terraform init      # downloads the Azure provider
terraform plan       # shows what WILL be created (nothing happens yet)
terraform apply       # type "yes" when prompted - this actually creates resources
```

After a minute or two, Terraform prints outputs including `vm_public_ip`. Save that IP — you'll need it next.

> **Cost note:** the default `Standard_B2s` VM is a low-cost "burstable" size, good for a first
> test/demo. Check current Azure pricing for your region before leaving it running long-term,
> and run `terraform destroy` when you're done experimenting to avoid ongoing charges.

## 5. Configure and deploy the application

```bash
cd ../docker
cp .env.example .env
```

Edit `.env` and set a strong `MB_DB_PASS`. Then, from the project root:

```bash
cd ..
chmod +x scripts/*.sh
./scripts/deploy.sh <vm_public_ip>
```

This script:
1. Waits for the VM's SSH to come online.
2. Copies the `docker/` folder to the VM.
3. Runs `docker compose up -d` remotely to start Metabase + Postgres.
4. Polls the health endpoint until Metabase responds.

## 6. First-time Metabase setup (in your browser)

Open `http://<vm_public_ip>:3000`. Metabase will walk you through a setup wizard:
1. Create your admin account (this is separate from Azure/GitHub — it's just for Metabase).
2. Optionally connect a data source (a database, or upload a CSV to try it out).
3. Metabase will offer to auto-generate a starter dashboard — use this as your first sample dashboard.

## 7. Making changes later

- **Change the app** (e.g. Metabase version, env vars): edit `docker/docker-compose.yml` or `docker/.env`, then re-run `./scripts/deploy.sh <vm_public_ip>`.
- **Change infrastructure** (e.g. VM size): edit `terraform/variables.tf` or `terraform.tfvars`, then `terraform apply` again from `terraform/`.
- **Tear everything down**: `terraform destroy` from `terraform/` (removes all Azure resources and stops billing).

## 8. Next steps toward production

- Put a reverse proxy (nginx/Caddy) with HTTPS in front of Metabase instead of exposing port 3000 directly.
- Move `allowed_ssh_cidr`/`allowed_metabase_cidr` to your office/VPN IP only.
- Set up Azure Backup or scheduled snapshots for the data disk.
- Configure Metabase email (SMTP) so scheduled dashboard reports can be emailed to stakeholders.
