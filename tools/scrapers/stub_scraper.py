import logging

from tools.scrapers.base import BaseScraper, Publication

logger = logging.getLogger(__name__)


class StubScraper(BaseScraper):
    """Placeholder scraper for courts that cannot be automatically monitored.

    Returns an empty list. The reason for disabling is logged at startup.
    Used for: Saarland (Cloudflare WAF), Sachsen (no FG in portal),
    Schleswig-Holstein (URL unknown), Thüringen (URL unknown).
    """

    def fetch_latest(self) -> list[Publication]:
        reason = self.config.get("reason", "no reason given")
        logger.info(
            "StubScraper [%s]: skipped — %s",
            self.config.get("court_key", "unknown"),
            reason,
        )
        return []
