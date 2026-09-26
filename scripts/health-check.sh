#!/bin/bash
# Polls Metabase's /api/health endpoint until it responds healthy, or times out.
# Usage: ./scripts/health-check.sh <host_or_ip> [port]
set -euo pipefail

HOST="${1:?Usage: ./scripts/health-check.sh <host_or_ip> [port]}"
PORT="${2:-3000}"
URL="http://$HOST:$PORT/api/health"
MAX_ATTEMPTS=30
SLEEP_SECONDS=10

echo "Checking $URL ..."
for i in $(seq 1 "$MAX_ATTEMPTS"); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL" || echo "000")
  if [ "$STATUS" = "200" ]; then
    echo "✅ Metabase is healthy (attempt $i/$MAX_ATTEMPTS)."
    exit 0
  fi
  echo "⏳ Not healthy yet (HTTP $STATUS) - attempt $i/$MAX_ATTEMPTS. Waiting ${SLEEP_SECONDS}s..."
  sleep "$SLEEP_SECONDS"
done

echo "❌ Metabase did not become healthy after $((MAX_ATTEMPTS * SLEEP_SECONDS / 60)) minutes."
echo "   SSH into the VM and check logs with: sudo docker compose logs -f metabase"
exit 1
