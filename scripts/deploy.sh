#!/bin/bash
set -e

cd /opt/video-downloader
git fetch origin
git reset --hard origin/main

docker compose build api worker frontend
docker compose up -d --force-recreate api worker frontend

echo "Deploy completed at $(date)"
