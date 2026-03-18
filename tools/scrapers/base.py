from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Publication:
    id: str        # Stable unique ID (URL path segment or UUID)
    title: str
    date: str      # DD.MM.YYYY or ISO string as found on site
    url: str
    court_key: str


class BaseScraper(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def fetch_latest(self) -> list[Publication]:
        """Fetch the most recent publications from the court's website.
        Returns up to 20 Publication objects, newest first."""
        ...
