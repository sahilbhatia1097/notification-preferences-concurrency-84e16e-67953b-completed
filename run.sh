#!/usr/bin/env bash
set -e

echo "Starting Notification Preferences API..."
cd /root/task
docker-compose up -d --build
echo "Waiting for services to be ready..."
sleep 10
echo "Checking health..."
curl -s http://localhost:8000/health || echo "Health check failed"
echo ""
echo "Startup completed"
