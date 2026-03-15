#!/bin/bash
# Deploy script para a VPS
# Rodar de: /opt/stack/
set -e

echo "=== Uúba Tech API — Deploy ==="

# Pull latest
echo "→ Pulling latest from GitHub..."
cd /opt/stack/uuba-tech
git pull origin main

# Rebuild e restart
echo "→ Rebuilding and restarting uuba-api..."
cd /opt/stack
docker compose build uuba-api
docker compose up -d uuba-api

# Aguardar healthcheck
echo "→ Waiting for health check..."
sleep 5
for i in {1..10}; do
    if docker compose exec uuba-api python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" 2>/dev/null; then
        echo "✓ API is healthy!"
        break
    fi
    echo "  Attempt $i/10..."
    sleep 3
done

# Status
echo ""
echo "=== Status ==="
docker compose ps uuba-api uuba-db
echo ""
echo "API: http://localhost:8000/health"
echo "Docs: http://localhost:8000/docs"
