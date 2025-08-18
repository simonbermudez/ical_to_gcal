# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an ICS to Google Calendar synchronization tool that performs one-way sync from ICS (iCalendar) feeds to Google Calendar using the Google Calendar API. The project is containerized with Docker and includes automated scheduling capabilities.

## Key Architecture

### Core Sync Logic
- **sync.py**: Main synchronization script that fetches ICS data, parses events, and syncs to Google Calendar
  - Uses UID matching to track events between ICS and Google Calendar
  - Stores ICS UIDs in Google Calendar's extendedProperties.private.icsUid field
  - Handles recurring events with RRULE conversion
  - Supports timezone conversion, all-day events, and attendee sync

### Authentication Flow
- Uses OAuth 2.0 with Google Calendar API
- Credentials stored in `credentials/credentials.json` (OAuth client secrets)
- Token cached in `credentials/token.json` (OAuth access token)
- Requires `https://www.googleapis.com/auth/calendar` scope

### Docker Architecture
- Main container: `ical-to-gcal` runs Python sync script
- Scheduler: Uses Ofelia (mcuadros/ofelia) for cron-like scheduling
- Docker Compose profiles:
  - `scheduler`: Runs automated sync every hour
  - `tools`: Utility commands like listing calendars
  - `setup`: Initial credential setup

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run sync (basic)
python sync.py --ics-url "URL" --calendar-id "primary"

# Run with all options
python sync.py --ics-url "URL" --calendar-id "ID" --future-only --prune-missing --dry-run

# List available calendars
python list_calendars.py

# Run tests (simple test files exist but no test framework)
python test_ics.py
python test_single_event.py
python test_rrule_conversion.py
```

### Docker Development
```bash
# Build Docker image
./docker-build.sh
# or
docker build -t ical-to-gcal .

# Run sync with Docker
./docker-sync.sh "ICS_URL" "CALENDAR_ID" --dry-run

# Using Docker Compose
docker-compose run --rm ical-sync

# List calendars
docker-compose --profile tools run --rm list-calendars

# Start scheduled sync (runs every hour)
docker-compose --profile scheduler up -d

# Check scheduler logs
docker-compose --profile scheduler logs scheduler
docker logs ical_to_gcal-scheduler-1 --tail 20

# Stop scheduler
docker-compose --profile scheduler down

# Interactive debugging
docker run --rm -it -v $(pwd)/credentials:/app/credentials --entrypoint /bin/bash ical-to-gcal

# Run Sync Manually 
docker compose run --rm ical-sync
```

## Command Line Arguments

### sync.py Arguments
- `--ics-url` (required): ICS feed URL to sync from
- `--calendar-id` (required): Target Google Calendar ID ("primary" or specific email)
- `--credentials`: OAuth client secrets file (default: "credentials.json")
- `--token`: Cached OAuth token file (default: "token.json")
- `--prune-missing`: Delete events from Google Calendar not in current ICS feed
- `--dry-run`: Preview changes without modifying calendar
- `--future-only`: Only sync future events (checks UNTIL date for recurring events)

## Environment Variables (Docker)
- `ICS_URL`: ICS feed URL
- `CALENDAR_ID`: Target calendar ID
- `SYNC_FLAGS`: Additional sync flags (default: "--dry-run")
- `CREDENTIALS_PATH`: Path to credentials.json (default: "/app/credentials/credentials.json")
- `TOKEN_PATH`: Path to token.json (default: "/app/credentials/token.json")

## Event Synchronization Logic

1. **Event Matching**: Uses ICS UID property stored in Google Calendar's extendedProperties
2. **Update Detection**: Compares event hashes to detect changes
3. **Status Handling**: CANCELLED events in ICS trigger deletion in Google Calendar
4. **Recurrence**: Converts ICS RRULE to Google Calendar recurrence format
5. **Timezone**: Preserves timezone information from ICS, treats naive datetimes as UTC

## Testing Approach

No formal test framework is configured. Test files are standalone Python scripts that can be run directly:
- `test_ics.py`: Tests ICS parsing
- `test_single_event.py`: Tests single event sync
- `test_rrule_conversion.py`: Tests recurring event conversion
- `test_future_filter.py`: Tests future-only filtering
- `test_cached_rrule.py`: Tests RRULE caching logic

Run tests individually: `python test_name.py`

## Important Files
- `sync.py`: Core synchronization logic
- `list_calendars.py`: Utility to list available Google Calendars
- `docker-compose.yml`: Container orchestration with scheduler
- `credentials/`: Directory for Google OAuth credentials (gitignored)
- Test files: `test_*.py` for various sync scenarios