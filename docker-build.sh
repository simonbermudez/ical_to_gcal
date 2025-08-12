#!/bin/bash

# Build the Docker image
echo "Building ical-to-gcal Docker image..."
docker build -t ical-to-gcal .

# Create directories if they don't exist
mkdir -p credentials data

echo ""
echo "Build complete!"
echo ""
echo "Next steps:"
echo "1. Place your credentials.json in the credentials/ directory"
echo "2. Copy .env.example to .env and configure your ICS URL and Calendar ID"
echo "3. Run 'docker-compose run --rm ical-sync' to start syncing"
echo ""
echo "To list your Google Calendars:"
echo "docker-compose --profile tools run --rm list-calendars"
