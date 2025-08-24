from stravalib import Client
from stravalib.client import BatchedResultsIterator
from stravalib.model import SummaryActivity
from dotenv import load_dotenv
import os
import json
import gspread
from gspread import Spreadsheet
import time
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import Optional, List
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.getenv('LOG_FILE_PATH', '/var/log/health-activity-tracker.log'))
    ]
)

def load_token_data():
    try:
        with open('strava_tokens.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: strava_tokens.json not found.")
        raise

def save_token_data(token_data):
    with open('strava_tokens.json', 'w') as f:
        json.dump(token_data, f, indent=2)

def load_processed_activities():
    try:
        with open('processed_activities.json', 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_processed_activities(activity_ids):
    with open('processed_activities.json', 'w') as f:
        json.dump(list(activity_ids), f, indent=2)

def get_strava_client():
    token_data = load_token_data()

    client = Client(
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_expires=token_data["expires_at"]
    )

    return client, token_data

def save_tokens_if_refreshed(client: Client, original_expires_at: int):
    if client.token_expires != original_expires_at:
        logging.info("Token refreshed, updating.")

        new_token_data = {
            "access_token": client.access_token,
            "refresh_token": client.refresh_token,
            "expires_at": client.token_expires
        }
        save_token_data(new_token_data)

def get_google_sheet() -> Spreadsheet:
    gc = gspread.service_account()
    
    return gc.open_by_url(os.getenv('GOOGLE_SHEET_URL'))

def fetch_recent_activities(client: Client, minutes_ago=360) -> BatchedResultsIterator[SummaryActivity]:
    now = datetime.now(timezone.utc)
    time_threshold = now - timedelta(minutes=minutes_ago)

    logging.info(f"Fetching activities uploaded after {time_threshold.isoformat()}")
    activities = client.get_activities(after=time_threshold - timedelta(hours=1))

    recent_activities = []
    for activity in activities:
        if activity.start_date >= time_threshold:
            recent_activities.append(activity)
        
        if len(recent_activities) >= 50:
            break
    
    return recent_activities

@dataclass
class ConvertedActivity:
    date: datetime
    sport_type: str
    duration: str
    distance: Optional[int]
    avg_speed: Optional[float]
    avg_hr: Optional[int]
    max_hr: Optional[int]
    calories: Optional[int]
    avg_watt: Optional[int]
    max_watt: Optional[int]
    normalized_power: Optional[int]
    elevation: Optional[int]
    strava_url_formula: str

def prepare_activity_data(summary_activity: SummaryActivity) -> ConvertedActivity:
    activity = client.get_activity(activity_id=summary_activity.id)
    map_sport_type = {
        "EBikeRide": "Bike",
        "Hike": "Walk",
        "Ride": "Bike",
        "TrailRun": "Run",
        "VirtualRide": "Bike",
        "VirtualRun": "Run",
        "Walk": "Walk",
        "WeightTraining": "Exercise",
        "Workout": "Exercise",
        "Yoga": "Stretch",
        "Run": "Run",
        "Swim": "Swim"
    }

    date_sport = activity.start_date
    sport_type = map_sport_type.get(activity.sport_type.root, activity.sport_type.root)
    duration = f"=TIME(0;0;{activity.moving_time})"
    distance = activity.distance if sport_type not in ["Stretch", "Exercise"] else 0
    avg_speed = activity.average_speed
    calories = activity.calories
    avg_hr = activity.average_heartrate
    max_hr = activity.max_heartrate
    avg_watt = activity.average_watts
    max_watt = activity.max_watts
    normalized_power = activity.weighted_average_watts
    elevation = activity.total_elevation_gain
    strava_url = f"https://strava.com/activities/{activity.id}"
    hyperlink_formula = f'=HYPERLINK("{strava_url}";"Strava")'

    return ConvertedActivity(
        date=date_sport,
        sport_type=sport_type,
        duration=duration,
        distance=distance,
        avg_speed=avg_speed,
        avg_hr=avg_hr,
        max_hr=max_hr,
        calories=calories,
        avg_watt=avg_watt,
        max_watt=max_watt,
        normalized_power=normalized_power,
        elevation=elevation,
        strava_url_formula=hyperlink_formula
    )
    
def sync_to_google_sheets(activities_data: List[ConvertedActivity]):
    if not activities_data:
        logging.info("No new activities to upload.")
        return
    
    try:
        gc = get_google_sheet()
        worksheet = gc.worksheet(os.getenv('ACTIVITIES_WORKSHEET_NAME'))
        
        values = worksheet.get_all_values()
        next_row = len(values) + 1

        batch_requests = []
        
        for i, activity in enumerate(activities_data):
            current_row = next_row + i
            
            updates = {
                'A': activity.date.strftime('%Y-%m-%d %H:%M:%S'),
                'B': activity.strava_url_formula,
                'C': activity.sport_type,
                'E': activity.duration,
                'F': activity.distance if activity.distance > 0 else '',
                'G': activity.avg_speed if activity.avg_speed > 0 else '',
                'I': activity.avg_hr if activity.avg_hr else '',
                'K': activity.max_hr if activity.max_hr else '',
                'L': activity.calories if activity.calories else '',
                'M': activity.avg_watt if activity.avg_watt else '',
                'N': activity.max_watt if activity.max_watt else '',
                'O': activity.normalized_power if activity.normalized_power else '',
                'P': activity.elevation if activity.elevation else ''
            }
            
            for col, value in updates.items():
                batch_requests.append({
                    'range': f'{col}{current_row}',
                    'values': [[value]]
                })

        worksheet.batch_update(batch_requests, value_input_option='USER_ENTERED')
        
        logging.info(f"Successfully uploaded {len(activities_data)} activities to Google Sheets!")
        
    except Exception as e:
        logging.error(f"Error uploading to Google Sheets: {e}")
        raise

logging.info(f"=== Strava Sync Started at {datetime.now()} ===")
    
try:
    client, original_token_data = get_strava_client()
    original_expires_at = original_token_data["expires_at"]
    
    processed_activities = load_processed_activities()    
    recent_activities = fetch_recent_activities(client, minutes_ago=360)
    logging.info(f"Found {len(recent_activities)} new activities")
    
    new_activities = [
        activity for activity in recent_activities 
        if activity.id not in processed_activities
    ]
    
    if not new_activities:
        logging.info("No new activities to process.")
        exit()
        
    batch_data = []
    new_activity_ids = set()
    
    for activity in new_activities:
        try:
            batch_data.append(prepare_activity_data(activity))
            new_activity_ids.add(activity.id)
        except Exception as e:
            logging.info(f"Error processing activity {activity.id}: {e}")
            continue
    
    if batch_data:
        sync_to_google_sheets(batch_data)
        
        processed_activities.update(new_activity_ids)
        save_processed_activities(processed_activities)
    
    save_tokens_if_refreshed(client, original_expires_at)
    
    logging.info("=== Sync completed successfully ===")
    
except Exception as e:
    logging.error(f"Error during sync: {e}")
    logging.error("=== Sync failed ===")

    raise
