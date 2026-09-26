#!/bin/bash
# Stops and removes the Metabase stack on the remote VM (containers + volumes stay on the data disk
# unless --purge is passed). Does NOT destroy Azure infrastructure - use terraform destroy for that.
# Usage: ./scripts/cleanup.sh <vm_public_ip> [ssh_user] [--purge]
set -euo pipefail

VM_IP="${1:?Usage: ./scripts/cleanup.sh <vm_public_ip> [ssh_user] [--purge]}"
SSH_USER="${2:-azureadmin}"
PURGE_FLAG="${3:-}"

ssh "$SSH_USER@$VM_IP" bash -s <<REMOTE_SCRIPT
set -euo pipefail
cd /opt/metabase-analytics
sudo docker compose down $( [ "$PURGE_FLAG" = "--purge" ] && echo "-v" )
echo "Stack stopped."
REMOTE_SCRIPT

echo "Done. To fully remove Azure resources, run: terraform destroy (from the terraform/ folder)."
