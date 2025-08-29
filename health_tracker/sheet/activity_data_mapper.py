import os

from health_tracker.data.activity_data import ActivityData


class ActivityDataMapper:
    def __init__(self, env_var="ACTIVITIES_COLUMNS"):
        self.mapping = os.getenv(env_var, "")

    def to_updates(self, activity: ActivityData, row: int):
        updates = []
        for part in self.mapping.split(","):
            if not part.strip():
                continue
            col, field = part.split(":")
            if field == "date":
                value = activity.date.strftime("%Y-%m-%d %H:%M:%S")
            elif hasattr(activity, field):
                attr = getattr(activity, field)
                value = attr() if callable(attr) else attr
            else:
                value = ""
            if value not in ("", None):
                updates.append({"range": f"{col}{row}", "values": [[value]]})
        return updates
