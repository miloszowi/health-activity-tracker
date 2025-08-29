import os

from health_tracker.data.day_health_data import DayHealthData


class HealthDataMapper:
    def __init__(self, env_var="HEALTH_COLUMNS"):
        self.mapping = os.getenv(env_var, "")

    def to_updates(self, data: DayHealthData, row: int, date: str):
        updates = []
        for part in self.mapping.split(","):
            if not part.strip():
                continue
            col, field = part.split(":")
            value = getattr(data, field, "") if hasattr(data, field) else (date if field == "date" else "")
            updates.append({"range": f"{col}{row}", "values": [[value if value else ""]]})
        return updates