#!/bin/sh

echo "Starting cookie-refresh cron..."

# Run immediately on start
node /app/refresh.js

# Then every 24 hours
while true; do
  sleep 86400
  echo "Running scheduled cookie refresh..."
  node /app/refresh.js
done
