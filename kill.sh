#!/usr/bin/env bash
set -e
echo "Stopping and removing Docker containers and volumes..."
docker-compose down -v || true
echo "Removing Docker images..."
docker image prune -a -f || true
echo "Running Docker system prune..."
docker system prune -f || true
echo "Removing task directory at /root/task if it exists..."
rm -rf /root/task || true
echo "Cleanup completed"
