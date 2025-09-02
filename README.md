# Health Activity Tracker

A comprehensive health and activity data synchronization tool that integrates with Garmin, Strava, Google Sheets, and Notion.

## Features

- **Health Data Sync**: Automatically sync health metrics from Garmin Connect
- **Activity Sync**: Sync activities from Strava with configurable time ranges
- **Multiple Destinations**: Support for Google Sheets and Notion
- **Configurable Mappings**: YAML-based field mappings for each destination
- **Flexible Configuration**: Local config overrides with sensible defaults

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd health-activity-tracker
python -m health_tracker.main setup-config
python -m health_tracker.main setup-main-config
```

### 2. Configure

Copy and customize the configuration files:

- **Main config**: `config/config.yaml` (paths, database IDs, etc.)
- **Mappings**: `config/mapping/` (field mappings for each destination)

### 3. Set Environment Variables

Create `.env` file with your secrets:

```bash
# Garmin credentials
GARMIN_EMAIL=your_email@example.com
GARMIN_PASSWORD=your_password

# Notion API
NOTION_SECRET=your_notion_integration_token

# Strava API
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
STRAVA_REFRESH_TOKEN=your_strava_refresh_token
```

### 4. Run Sync

```bash
# Sync health data to Google Sheets
python -m health_tracker.main sync-health --target sheets

# Sync activities from specific date range to Notion
python -m health_tracker.main sync-activities \
    --target notion \
    --start-date "2024-01-01 00:00:00" \
    --end-date "2024-01-31 23:59:59"

# Sync activities from specific date range to Google Sheets
python -m health_tracker.main sync-activities \
    --target sheets \
    --start-date "2024-01-01 00:00:00" \
    --end-date "2024-01-31 23:59:59"
```

## Configuration

### Main Configuration (`config/config.yaml`)

Configure paths, database IDs, and other settings:

```yaml
google_sheets:
  credentials_file: "google_sheets_credentials.json"
  spreadsheet_url: "your_spreadsheet_url"
  worksheets:
    health: "Health"
    activities: "Activities"

notion:
  databases:
    health: "your_health_database_id"
    activities: "your_activities_database_id"

garmin:
  token_dir: ".garminconnect"

strava:
  token_file: "strava_tokens.json"
  processed_file: "processed_activities.json"
```

### Mapping Configuration

Customize field mappings for each destination in `config/mapping/`:

- **Google Sheets**: Column mappings
- **Notion**: Property mappings with types

## CLI Commands

```bash
# Configuration management
python -m health_tracker.main setup-config          # Setup mapping structure
python -m health_tracker.main setup-main-config     # Setup main config
python -m health_tracker.main mapping-info          # Show available mappings
python -m health_tracker.main config-info           # Show current config

# Data synchronization
python -m health_tracker.main sync-health --target <target>
python -m health_tracker.main sync-activities --target <target> --start-date <date> --end-date <date>
```

## Features

- **Providers**: Garmin (health), Strava (activities)
- **Destinations**: Google Sheets, Notion
- **Mapping System**: YAML-based field mappings with local override support
- **Configuration**: Layered config system (env > local > default)
