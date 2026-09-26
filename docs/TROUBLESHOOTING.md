# Troubleshooting

## `terraform apply` fails with an authorization/permission error
Run `az login` again and confirm the right subscription with `az account show`.
Your account needs Contributor (or Owner) rights on the subscription/resource group.

## Can't SSH into the VM
- Confirm the VM finished booting (can take 1-2 minutes after `terraform apply`).
- Confirm `allowed_ssh_cidr` in `terraform.tfvars` includes your current public IP (`curl ifconfig.me`). If your IP changed, update it and run `terraform apply` again.
- Make sure you're using the private key that matches the public key in `ssh_public_key_path`.

## `./scripts/deploy.sh` hangs at "Waiting for SSH..."
- The VM might still be running its first-boot script (installing Docker). Wait a few more minutes and re-run.
- Check the NSG rule for port 22 is present: `az network nsg rule list -g <resource-group> --nsg-name <nsg-name> -o table`.

## Metabase never becomes healthy
SSH into the VM and check logs:
```bash
ssh azureadmin@<vm_public_ip>
cd /opt/metabase-analytics
sudo docker compose ps
sudo docker compose logs -f metabase
sudo docker compose logs -f metabase-db
```
Common causes:
- `MB_DB_PASS` in `.env` doesn't match what Postgres was initialized with (if you changed the password after the first run, you must also wipe the old Postgres volume — see below).
- The VM ran out of memory. `Standard_B2s` (4GB RAM) is usually enough, but if you add heavy data sources consider a larger `vm_size`.

## I changed the database password and now Metabase can't connect
Postgres only applies `POSTGRES_PASSWORD` on first initialization. If you change the password afterward,
either update it manually inside the running Postgres container, or wipe the volume and start fresh
(this deletes all Metabase configuration/dashboards):
```bash
ssh azureadmin@<vm_public_ip>
cd /opt/metabase-analytics
sudo docker compose down -v
sudo docker compose up -d
```

## I want to see resource costs before committing
```bash
cd terraform
terraform plan
```
This shows exactly what will be created without creating anything. You can also use the
[Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/) with the VM size from `variables.tf`.

## I'm done testing and want to stop being charged
```bash
cd terraform
terraform destroy
```
Type `yes` when prompted. This removes the VM, disks, networking, and public IP.
