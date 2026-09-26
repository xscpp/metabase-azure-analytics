#!/bin/bash
# This runs automatically once, the first time the VM boots (via Azure custom_data).
# It only installs prerequisites (Docker + Compose). The actual Metabase stack is
# started afterwards by running scripts/deploy.sh over SSH - this keeps secrets
# (like database passwords) out of the VM boot metadata.
set -euo pipefail

exec > /var/log/cloud-init-bootstrap.log 2>&1
echo "=== Bootstrap started at $(date) ==="

apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release

# Format and mount the attached data disk for persistent Metabase/Postgres storage
DATA_DISK="/dev/disk/azure/scsi1/lun10"
MOUNT_POINT="/data"
if [ -e "$DATA_DISK" ]; then
  if ! blkid "$DATA_DISK" > /dev/null 2>&1; then
    mkfs.ext4 -F "$DATA_DISK"
  fi
  mkdir -p "$MOUNT_POINT"
  mount "$DATA_DISK" "$MOUNT_POINT" || true
  echo "$DATA_DISK $MOUNT_POINT ext4 defaults,nofail 0 2" >> /etc/fstab
  chown -R azureadmin:azureadmin "$MOUNT_POINT" || true
fi

# Install Docker Engine + Compose plugin (official Docker repo)
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

usermod -aG docker azureadmin || true
systemctl enable docker
systemctl start docker

mkdir -p /opt/metabase-analytics
chown -R azureadmin:azureadmin /opt/metabase-analytics

echo "=== Bootstrap finished at $(date) ==="
echo "Docker and Docker Compose are installed. Next step: run scripts/deploy.sh from your machine to push and start the stack."
