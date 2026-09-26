#!/bin/bash
# Deploys the Metabase stack to the remote Azure VM.
# Usage: ./scripts/deploy.sh <vm_public_ip> [ssh_user] [ssh_key_path]
#
# Prerequisites:
#   - terraform apply has already run successfully (see terraform/README or docs/DEPLOYMENT.md)
#   - docker/.env exists locally (copy from docker/.env.example and fill it in)
#   - You can SSH into the VM
set -euo pipefail

VM_IP="${1:?Usage: ./scripts/deploy.sh <vm_public_ip> [ssh_user] [ssh_key_path]}"
SSH_USER="${2:-azureadmin}"
SSH_KEY="${3:-$HOME/.ssh/id_rsa}"
REMOTE_DIR="/opt/metabase-analytics"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -f "$PROJECT_ROOT/docker/.env" ]; then
  echo "ERROR: docker/.env not found. Copy docker/.env.example to docker/.env and fill in real values first."
  exit 1
fi

echo "== Waiting for SSH to become available on $VM_IP =="
for i in $(seq 1 20); do
  if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 "$SSH_USER@$VM_IP" "echo ok" &> /dev/null; then
    echo "SSH is up."
    break
  fi
  echo "Not ready yet, retrying ($i/20)..."
  sleep 10
done

echo "== Copying deployment files to the VM =="
ssh -i "$SSH_KEY" "$SSH_USER@$VM_IP" "sudo mkdir -p $REMOTE_DIR && sudo chown $SSH_USER:$SSH_USER $REMOTE_DIR"
scp -i "$SSH_KEY" -r "$PROJECT_ROOT/docker/." "$SSH_USER@$VM_IP:$REMOTE_DIR/"
scp -i "$SSH_KEY" "$PROJECT_ROOT/scripts/health-check.sh" "$SSH_USER@$VM_IP:$REMOTE_DIR/"

echo "== Starting the stack on the VM =="
ssh -i "$SSH_KEY" "$SSH_USER@$VM_IP" bash -s <<'REMOTE_SCRIPT'
set -euo pipefail
cd /opt/metabase-analytics

# Point Docker Compose at the mounted data disk if it exists, else use a local folder
if [ -d /data ]; then
  sed -i 's#^DATA_PATH=.*#DATA_PATH=/data#' .env || echo "DATA_PATH=/data" >> .env
fi

sudo docker compose pull
sudo docker compose up -d
REMOTE_SCRIPT

echo "== Deployment triggered. Running health check (Metabase can take 1-2 minutes to fully start) =="
bash "$PROJECT_ROOT/scripts/health-check.sh" "$VM_IP"

echo ""
echo "Done. Once healthy, open: http://$VM_IP:3000"
