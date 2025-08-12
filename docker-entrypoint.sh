#!/bin/bash
set -e

# Debug: Print environment variables
echo "Debug: ICS_URL=$ICS_URL"
echo "Debug: CALENDAR_ID=$CALENDAR_ID"
echo "Debug: SYNC_FLAGS=$SYNC_FLAGS"
echo "Debug: Arguments passed: $@"
echo ""

# Use environment variables for credentials and token paths if set
CREDENTIALS_ARG=""
TOKEN_ARG=""

if [ -n "$CREDENTIALS_PATH" ]; then
    CREDENTIALS_ARG="--credentials $CREDENTIALS_PATH"
fi

if [ -n "$TOKEN_PATH" ]; then
    TOKEN_ARG="--token $TOKEN_PATH"
fi

# If ICS_URL and CALENDAR_ID are set as environment variables, use them
if [ -n "$ICS_URL" ] && [ -n "$CALENDAR_ID" ]; then
    echo "Using environment variables for sync configuration:"
    echo "ICS_URL: $ICS_URL"
    echo "CALENDAR_ID: $CALENDAR_ID"
    
    # If SYNC_FLAGS is set, use it; otherwise default to --dry-run for safety
    if [ -n "$SYNC_FLAGS" ]; then
        ADDITIONAL_FLAGS="$SYNC_FLAGS"
        echo "FLAGS: $ADDITIONAL_FLAGS"
    else
        ADDITIONAL_FLAGS="--dry-run"
        echo "FLAGS: $ADDITIONAL_FLAGS (default)"
    fi
    echo ""
    
    # If no command line arguments provided or only --help, use environment variables
    if [ $# -eq 0 ] || [ "$1" = "--help" ]; then
        exec python sync.py $CREDENTIALS_ARG $TOKEN_ARG --ics-url "$ICS_URL" --calendar-id "$CALENDAR_ID" $ADDITIONAL_FLAGS
    fi
fi

# Execute the sync command with all arguments (original behavior for manual override)
exec python sync.py $CREDENTIALS_ARG $TOKEN_ARG "$@"
