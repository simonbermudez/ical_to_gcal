# ICS to Google Calendar Sync

A Python script that synchronizes events from an ICS (iCalendar) feed to a Google Calendar using the Google Calendar API.

## Features

- **One-way sync**: Fetches events from an ICS feed and syncs them to Google Calendar
- **Smart updates**: Only creates/updates events when necessary using UID matching
- **Prune missing events**: Option to delete events from Google Calendar that no longer exist in the ICS feed
- **Dry run mode**: Preview changes without actually modifying your calendar
- **Recurrence support**: Handles recurring events with RRULE patterns
- **All-day events**: Properly handles both timed and all-day events
- **Attendee sync**: Syncs event attendees from ICS to Google Calendar
- **Timezone handling**: Properly converts timezones between ICS and Google Calendar format

## Prerequisites

- Python 3.6+
- Google Cloud Project with Calendar API enabled
- OAuth 2.0 credentials file from Google Cloud Console

## Installation

1. Install required dependencies:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client icalendar pytz python-dateutil requests
```

2. Set up Google Calendar API credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Calendar API
   - Create OAuth 2.0 credentials (Desktop Application)
   - Download the credentials file as `credentials.json`

## Usage

### Basic Sync

```bash
python sync.py --ics-url "https://example.com/calendar.ics" --calendar-id "primary"
```

### Full Command Options

```bash
python sync.py --ics-url ICS_URL --calendar-id CALENDAR_ID [OPTIONS]
```

### Arguments

- `--ics-url`: **(Required)** Public ICS feed URL to sync from
- `--calendar-id`: **(Required)** Target Google Calendar ID (use "primary" for your main calendar, or specific email like "you@domain.com")
- `--credentials`: OAuth client secrets file (default: "credentials.json")
- `--token`: Cached OAuth token file (default: "token.json")
- `--prune-missing`: Delete Google events not present in current ICS feed
- `--dry-run`: Show what would change without actually modifying the calendar

### Examples

**Sync to primary calendar:**
```bash
python sync.py --ics-url "https://calendar.example.com/events.ics" --calendar-id "primary"
```

**Sync with pruning (removes old events):**
```bash
python sync.py --ics-url "https://calendar.example.com/events.ics" --calendar-id "primary" --prune-missing
```

**Preview changes without applying:**
```bash
python sync.py --ics-url "https://calendar.example.com/events.ics" --calendar-id "primary" --dry-run
```

**Use custom credentials file:**
```bash
python sync.py --ics-url "https://calendar.example.com/events.ics" --calendar-id "work@company.com" --credentials "my-creds.json"
```

## First Run Setup

On the first run, the script will:
1. Open your browser for Google OAuth authentication
2. Request permission to manage your Google Calendar
3. Save the authentication token to `token.json` for future use

## How It Works

1. **Fetch ICS**: Downloads the ICS file from the provided URL
2. **Parse Events**: Extracts VEVENT components from the ICS file
3. **Match Events**: Uses the ICS UID property to match events with existing Google Calendar events
4. **Sync Changes**: 
   - Creates new events that don't exist in Google Calendar
   - Updates existing events if they've changed
   - Optionally deletes events that no longer exist in the ICS feed (with `--prune-missing`)
5. **Handle Status**: Processes CANCELLED events by deleting them from Google Calendar

## Event Mapping

The script maps ICS properties to Google Calendar as follows:

| ICS Property | Google Calendar Field |
|--------------|----------------------|
| SUMMARY | summary |
| DESCRIPTION | description |
| LOCATION | location |
| DTSTART | start (date/dateTime + timeZone) |
| DTEND | end (date/dateTime + timeZone) |
| RRULE | recurrence |
| ATTENDEE | attendees |
| UID | extendedProperties.private.icsUid |

## Limitations

- **One-way sync only**: Changes made in Google Calendar will not be reflected back to the ICS source
- **No conflict resolution**: Google Calendar changes will be overwritten by ICS data
- **Basic recurrence**: Complex recurrence patterns may not sync perfectly
- **No attachment support**: File attachments are not synced

## Error Handling

- Malformed events are skipped with error messages
- Events without UIDs are skipped
- Network errors will cause the script to fail (no retry logic)
- Invalid credentials will prompt for re-authentication

## Security Notes

- Keep your `credentials.json` file secure and don't commit it to version control
- The `token.json` file contains access tokens - also keep it secure
- Use environment variables or secure storage for production deployments

## Troubleshooting

**Authentication errors:**
- Delete `token.json` to force re-authentication
- Ensure your `credentials.json` file is valid
- Check that the Google Calendar API is enabled in your Google Cloud project

**Timezone issues:**
- The script treats naive datetime objects as UTC
- Ensure your ICS feed includes proper timezone information

**Permission errors:**
- Verify the calendar ID is correct and accessible
- Ensure you have write permissions to the target calendar

## License

This project is open source. Please check the repository for license details.
