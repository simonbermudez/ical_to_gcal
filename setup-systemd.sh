#!/bin/bash

# Script to set up systemd timer for ICS to Google Calendar sync
# Run every 6 hours

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
SERVICE_FILE="ical-sync.service"
TIMER_FILE="ical-sync.timer"

echo "Setting up systemd timer for ICS sync every 6 hours..."
echo "Script directory: $SCRIPT_DIR"
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

# Update the service file with correct user and working directory
sed -i "s|User=%i|User=$USER|g" "$SERVICE_FILE"
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$SCRIPT_DIR|g" "$SERVICE_FILE"

# Copy service and timer files to systemd directory
sudo cp "$SERVICE_FILE" /etc/systemd/system/
sudo cp "$TIMER_FILE" /etc/systemd/system/

# Reload systemd and enable timer
sudo systemctl daemon-reload
sudo systemctl enable ical-sync.timer
sudo systemctl start ical-sync.timer

if [ $? -eq 0 ]; then
    echo "✅ Systemd timer set up successfully!"
    echo ""
    echo "The sync will run every 6 hours at:"
    echo "- 00:00 (midnight)"
    echo "- 06:00 (6 AM)"
    echo "- 12:00 (noon)"
    echo "- 18:00 (6 PM)"
    echo ""
    echo "Commands to manage the timer:"
    echo "- Check status: sudo systemctl status ical-sync.timer"
    echo "- View logs: journalctl -u ical-sync.service"
    echo "- Stop timer: sudo systemctl stop ical-sync.timer"
    echo "- Disable timer: sudo systemctl disable ical-sync.timer"
    echo "- Run manually: sudo systemctl start ical-sync.service"
else
    echo "❌ Failed to set up systemd timer"
    exit 1
fi
