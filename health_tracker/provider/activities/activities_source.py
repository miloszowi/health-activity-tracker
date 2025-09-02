from enum import Enum

from health_tracker.destination.destination import Target
from health_tracker.provider.abstract.activities_provider import ActivitiesProvider
from health_tracker.provider.activities.strava import StravaActivitiesProvider


class ActivitiesSource(Enum):
    STRAVA = ("strava", StravaActivitiesProvider)

    def __init__(self, label: str, provider_cls):
        self._label = label
        self._provider_cls = provider_cls

    @property
    def label(self) -> str:
        return self._label

    def provider(self, target: Target) -> ActivitiesProvider:
        return self._provider_cls(target)

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
