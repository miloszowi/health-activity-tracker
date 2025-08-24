# health-activity-tracker

automatically fetch strava activities & garmin health to a defined google sheet
sheet draft: https://docs.google.com/spreadsheets/d/1VfEODBPIlzlbpqyD_8aGmGfZALvCgcMaKNx4TubFlQY

## Installation
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
- cp `.env.example` `.env` and fill in the values
- cp `strava_token.json.example` `strava_token.json` and fill in the values (check out stravalib python package for obtaining first oauth access_token)
- cp `processed_activities.json.example` `processed_activities.json` (can be empty initially)
- `python check.py` to run

for google auth:
- create OAuth 2.0 Client IDs in Google Cloud Console
- create service account and download the JSON key file
- copy service_account.json to ~/.config/gspread/service_account.json

for strava:
- create an app in Strava Developer settings
- get client_id, client_secret and refresh_token and put them in .env
