#!/bin/bash

# Script to set up cron job for ICS to Google Calendar sync
# Run every 6 hours

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
CRON_COMMAND="0 */6 * * * cd $SCRIPT_DIR && docker-compose run --rm ical-sync > /tmp/ical-sync.log 2>&1"

echo "Setting up cron job to run ICS sync every 6 hours..."
echo "Script directory: $SCRIPT_DIR"
echo ""
echo "Cron command that will be added:"
echo "$CRON_COMMAND"
echo ""

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please copy .env.example to .env and configure your settings first."
    exit 1
fi

# Check if credentials exist
if [ ! -f "$SCRIPT_DIR/credentials/credentials.json" ]; then
    echo "⚠️  Warning: credentials.json not found!"
    echo "Please place your Google OAuth credentials in credentials/credentials.json"
    exit 1
fi

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo ""
    echo "The sync will run every 6 hours at:"
    echo "- 00:00 (midnight)"
    echo "- 06:00 (6 AM)"
    echo "- 12:00 (noon)"
    echo "- 18:00 (6 PM)"
    echo ""
    echo "Logs will be written to /tmp/ical-sync.log"
    echo ""
    echo "To view current cron jobs: crontab -l"
    echo "To remove this cron job: crontab -e (then delete the line)"
else
    echo "❌ Failed to add cron job"
    exit 1
fi
