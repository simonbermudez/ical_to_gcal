# Docker Usage Guide

## Quick Start with Docker

### 1. Build the Docker image

```bash
docker build -t ical-to-gcal .
```

### 2. Set up directories

```bash
mkdir -p credentials data
```

### 3. Add your Google credentials

Place your `credentials.json` file in the `credentials/` directory:

```bash
cp path/to/your/credentials.json credentials/
```

### 4. Run the sync

```bash
docker run --rm \
  -v $(pwd)/credentials:/app/credentials \
  -v $(pwd)/data:/app/data \
  ical-to-gcal \
  --ics-url "YOUR_ICS_URL" \
  --calendar-id "YOUR_CALENDAR_ID" \
  --dry-run
```

## Using Docker Compose

### 1. Set up directories and credentials

```bash
mkdir -p credentials data
cp path/to/your/credentials.json credentials/
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env file with your ICS URL and Calendar ID
```

### 3. List available calendars

```bash
docker-compose --profile tools run --rm list-calendars
```

### 4. Run sync with environment variables

```bash
docker-compose run --rm ical-sync
```

### 5. Or override with command line arguments

```bash
docker-compose run --rm ical-sync \
  --ics-url "YOUR_ICS_URL" \
  --calendar-id "YOUR_CALENDAR_ID" \
  --dry-run
```

## Environment Variables

- `ICS_URL`: The ICS feed URL to sync from
- `CALENDAR_ID`: Target Google Calendar ID
- `SYNC_FLAGS`: Additional sync flags (default: `--dry-run`)
- `CREDENTIALS_PATH`: Path to Google OAuth credentials file (default: `/app/credentials/credentials.json`)
- `TOKEN_PATH`: Path to OAuth token cache file (default: `/app/credentials/token.json`)

### Example .env file

```env
ICS_URL=https://outlook.office365.com/owa/calendar/your-calendar/calendar.ics
CALENDAR_ID=primary
SYNC_FLAGS=--future-only --prune-missing
```

## Volume Mounts

- `/app/credentials`: Mount your credentials directory here (contains both credentials.json and token.json)
- `/app/data`: Mount for additional data storage (optional)

## Common Docker Commands

### Build and run in one command
```bash
docker build -t ical-to-gcal . && \
docker run --rm \
  -v $(pwd)/credentials:/app/credentials \
  -v $(pwd)/data:/app/data \
  ical-to-gcal \
  --ics-url "YOUR_ICS_URL" \
  --calendar-id "YOUR_CALENDAR_ID" \
  --future-only
```

### Run with all flags
```bash
docker run --rm \
  -v $(pwd)/credentials:/app/credentials \
  -v $(pwd)/data:/app/data \
  ical-to-gcal \
  --ics-url "YOUR_ICS_URL" \
  --calendar-id "YOUR_CALENDAR_ID" \
  --future-only \
  --prune-missing \
  --dry-run
```

### Interactive shell for debugging
```bash
docker run --rm -it \
  -v $(pwd)/credentials:/app/credentials \
  -v $(pwd)/data:/app/data \
  --entrypoint /bin/bash \
  ical-to-gcal
```

## Scheduling with Cron

You can schedule the Docker container to run periodically using cron:

```bash
# Add to crontab (crontab -e)
# Run every 4 hours
0 */4 * * * cd /path/to/ical_to_gcal && docker-compose run --rm ical-sync --ics-url "YOUR_ICS_URL" --calendar-id "YOUR_CALENDAR_ID" --future-only
```

## Automated Scheduling with Docker Compose

For a more robust scheduling solution, you can use the built-in scheduler service:

### 1. Start the scheduler service

```bash
docker-compose --profile scheduler up -d scheduler
```

This will:
- Start the Ofelia scheduler container
- Run your sync automatically every 6 hours (00:00, 06:00, 12:00, 18:00)
- Use your environment variables from `.env` file

### 2. Monitor the scheduler

```bash
# Check scheduler status
docker-compose --profile scheduler ps

# View scheduler logs
docker-compose --profile scheduler logs scheduler

# View sync job logs
docker-compose logs ical-sync
```

### 3. Stop the scheduler

```bash
docker-compose --profile scheduler down
```

### How it works

The scheduler uses [Ofelia](https://github.com/mcuadros/ofelia), a modern cron-like job scheduler for Docker:

1. **Ofelia Container**: Runs continuously and monitors the schedule
2. **Docker Socket**: Mounted to allow Ofelia to start/stop containers
3. **Service Labels**: Define when and how to run the sync job
4. **Cron Schedule**: `0 */6 * * *` means "run at minute 0 of every 6th hour"

The schedule can be customized by editing the `ofelia.job-service-run.ical-sync.schedule` label in `docker-compose.yml`:
- `0 */4 * * *` - Every 4 hours
- `0 8,20 * * *` - Twice daily at 8 AM and 8 PM
- `0 9 * * 1` - Every Monday at 9 AM

## Setting up Automated Scheduling (Alternative Methods)

For other scheduling options, see the included scripts:
- `./setup-cron.sh` - Set up traditional cron job
- `./setup-systemd.sh` - Set up systemd timer (Linux)

## Docker Hub

To push to Docker Hub:

```bash
docker build -t your-username/ical-to-gcal .
docker push your-username/ical-to-gcal
```
