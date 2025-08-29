from enum import Enum
from functools import cached_property

from health_tracker.destination.google_sheets import GoogleSheets


class ActivitiesTarget(Enum):
    SHEETS = ("sheets", GoogleSheets)

    def __init__(self, label: str, factory):
        self._label = label
        self._factory = factory

    @property
    def label(self) -> str:
        return self._label

    @cached_property
    def instance(self):
        return self._factory()

    @classmethod
    def from_label(cls, label: str) -> "ActivitiesTarget":
        for t in cls:
            if t.label.lower() == label.lower():
                return t
        raise ValueError(f"{label} is not a valid activities target")

    @classmethod
    def choices(cls):
        return [t.label for t in cls]

    @classmethod
    def help(cls):
        return f"Available activities targets: {', '.join(cls.choices())}"
