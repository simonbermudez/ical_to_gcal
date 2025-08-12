#!/bin/bash

# Script to run the sync with Docker
# Usage: ./docker-sync.sh "ICS_URL" "CALENDAR_ID" [additional_flags]

if [ $# -lt 2 ]; then
    echo "Usage: $0 <ICS_URL> <CALENDAR_ID> [additional_flags]"
    echo ""
    echo "Examples:"
    echo "  $0 \"https://example.com/calendar.ics\" \"primary\" --dry-run"
    echo "  $0 \"https://example.com/calendar.ics\" \"work@company.com\" --future-only"
    echo "  $0 \"https://example.com/calendar.ics\" \"primary\" --future-only --prune-missing"
    exit 1
fi

ICS_URL="$1"
CALENDAR_ID="$2"
shift 2
ADDITIONAL_FLAGS="$@"

# Check if credentials exist
if [ ! -f "credentials/credentials.json" ]; then
    echo "Error: credentials/credentials.json not found"
    echo "Please place your Google OAuth credentials file in the credentials/ directory"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

echo "Starting ICS to Google Calendar sync..."
echo "ICS URL: $ICS_URL"
echo "Calendar ID: $CALENDAR_ID"
echo "Additional flags: $ADDITIONAL_FLAGS"
echo ""

docker run --rm \
  -v $(pwd)/credentials:/app/credentials \
  -v $(pwd)/data:/app/data \
  ical-to-gcal \
  --ics-url "$ICS_URL" \
  --calendar-id "$CALENDAR_ID" \
  $ADDITIONAL_FLAGS
