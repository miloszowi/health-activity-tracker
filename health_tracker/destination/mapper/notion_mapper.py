from health_tracker.data.day_health_data import DayHealthData


class NotionMapper:
    COLUMN_MAP = {
        "sleepHours": {
            "name": "Sleep",
            "type": "number"
        },
        "sleepScore": {
            "name": "Sleep Score",
            "type": "number"
        },
        "sleepRemHours": {
            "name": "Sleep REM",
            "type": "number"
        },
        "sleepAwakeMinutes": {
            "name": "Sleep Awake",
            "type": "number"
        },
        "sleepAwakeCount": {
            "name": "Awake N",
            "type": "number"
        },
        "averageSleepStress": {
            "name": "Sleep Stress",
            "type": "number"
        },
        "sleepNeededHours": {
            "name": "Sleep Need",
            "type": "number"
        },
        "averageSpO2Value": {
            "name": "Avg SpO2",
            "type": "number"
        },
        "averageOvernightHrv": {
            "name": "HRV",
            "type": "number"
        },
        "restingHeartRate": {
            "name": "Resting HR",
            "type": "number"
        },
        "averageStressLevel": {
            "name": "Avg Stress",
            "type": "number"
        },
        "stressHours": {
            "name": "Stress Duration",
            "type": "number"
        },
        "weight": {
            "name": "Weight",
            "type": "number"
        },
        "bodyBattery": {
            "name": "Body Battery",
            "type": "number"
        },
        "runVO2max": {
            "name": "Run VO2Max",
            "type": "number"
        },
        "bikeVO2max": {
            "name": "Bike VO2max",
            "type": "number"
        },
        "bikeFTP": {
            "name": "Bike FTP",
            "type": "number"
        },
        "totalSteps": {
            "name": "Total Steps",
            "type": "number"
        },
    }

    def __init__(self):
        pass

    def map(self, dto: DayHealthData) -> dict:
        props = {}
        for dto_field, cfg in self.COLUMN_MAP.items():
            value = getattr(dto, dto_field)
            if value is None:
                continue

            notion_name = cfg["name"]
            notion_type = cfg["type"]

            if notion_type == "number":
                props[notion_name] = {"number": float(value)}
            elif notion_type == "rich_text":
                props[notion_name] = {
                    "rich_text": [{"type": "text", "text": {"content": str(value)}}]
                }
            elif notion_type == "title":
                props[notion_name] = {
                    "title": [{"type": "text", "text": {"content": str(value)}}]
                }
            elif notion_type == "date":
                props[notion_name] = {"date": {"start": value}}

        return {"properties": props}
