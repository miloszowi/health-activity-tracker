# 🏃‍♂️ Health Activity Tracker  

**Health Activity Tracker** is a CLI tool to sync your **fitness and health data** from providers like **Garmin** and **Strava** into destinations like **Google Sheets**.  

- 📊 **Health sync** → Garmin sleep, HRV, stress, body battery, etc.  
- 🏃 **Activities sync** → Strava runs, rides, swims, etc.
---

## 📦 Installation  

Clone the repo and install dependencies:  

```bash
git clone https://github.com/miloszowi/health-activity-tracker.git
cd health-activity-tracker
pip install -e .
```

Or directly from GitHub in another project:
```bash
# pyproject.toml
dependencies = [
  "health-activity-tracker @ git+https://github.com/<your-username>/health-activity-tracker.git@main"
]
```

## Configuration
```bash
cp .env.example .env
vi .env
```

## Auth

### Strava

[Register an app in Strava API](https://www.strava.com/settings/api)

Get your tokens and save them to strava_tokens.json: (see `stravalib` for obtaining first oauth token)

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_at": 1234567890
}
```

### Garmin

Configure credentials for Garmin Connect (handled via garth/garminconnect).

Follow prompts on first login.

## Usage

### Health data sync
```bash
python health_tracker/main.py sync-health \
  --source garmin \
  --target sheets \
  --start-date 2025-08-01 \
  --end-date 2025-08-10
```

### Activities data sync
```bash
python health_tracker/main.py sync-activities \
  --source strava \
  --target sheets \
  --minutes-ago 720
```