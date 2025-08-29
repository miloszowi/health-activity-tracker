from enum import Enum
from functools import cached_property

from health_tracker.provider.activities.strava import StravaActivitiesProvider


class ActivitiesSource(Enum):
    STRAVA = ("strava", StravaActivitiesProvider)

    def __init__(self, label: str, provider_cls):
        self._label = label
        self._provider_cls = provider_cls

    @property
    def label(self) -> str:
        return self._label

    @cached_property
    def provider(self):
        return self._provider_cls()

    @classmethod
    def choices(cls):
        return [s.label for s in cls]

    @classmethod
    def help(cls):
        return f"Activities sources: {', '.join(cls.choices())}"

    @classmethod
    def from_label(cls, label: str) -> "ActivitiesSource":
        for s in cls:
            if s.label.lower() == label.lower():
                return s
        raise ValueError(f"{label} is not a valid {cls.__name__}")
