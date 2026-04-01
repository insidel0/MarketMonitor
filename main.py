"""Main orchestrator for the German Finanzgericht publication monitoring agent.

Workflow:
  1. Load state (seen publication IDs per court)
  2. For each enabled court: scrape latest publications
  3. Diff against seen IDs to find new ones
  4. Save updated state back to state.json
  5. If new publications found: send Gmail digest email

Run locally:
  python main.py

Run in GitHub Actions:
  See .github/workflows/monitor.yml
"""
import json
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from courts_config import COURTS, CourtConfig
from tools.scrapers.base import Publication
from tools.scrapers.stub_scraper import StubScraper
from tools.scrapers.voris_scraper import VorisScraper
from tools.scrapers.dejure_scraper import DejureScraper
from tools.write_report import write_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

STATE_FILE = Path(__file__).parent / "state.json"
MAX_SEEN_IDS = 500  # Max IDs to keep per court to bound state.json size


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        with STATE_FILE.open(encoding="utf-8") as f:
            return json.load(f)
    return {"last_run": None, "version": 1, "seen": {}}


def save_state(state: dict) -> None:
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")


def is_recent(pub: Publication, max_days: int = 28) -> bool:
    """Return True if the publication date is within the last max_days days.
    Publications with no parseable date are included to avoid missing real ones."""
    if not pub.date:
        return True
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            pub_date = datetime.strptime(pub.date, fmt).date()
            cutoff = (datetime.now(timezone.utc) - timedelta(days=max_days)).date()
            return pub_date >= cutoff
        except ValueError:
            continue
    return True  # Unparseable date — include to be safe


def get_new_publications(
    publications: list[Publication], seen_ids: list[str]
) -> list[Publication]:
    seen_set = set(seen_ids)
    return [
        p for p in publications
        if p.id not in seen_set and is_recent(p)
    ]


def update_seen(seen_ids: list[str], new_ids: list[str]) -> list[str]:
    combined = seen_ids + [i for i in new_ids if i not in seen_ids]
    # Trim oldest entries if over limit
    if len(combined) > MAX_SEEN_IDS:
        combined = combined[len(combined) - MAX_SEEN_IDS:]
    return combined


# ---------------------------------------------------------------------------
# Scraper factory
# ---------------------------------------------------------------------------

def build_scraper(court: CourtConfig, playwright_context=None):
    """Return an instantiated scraper for the given court."""
    if court.scraper_type == "dejure":
        return DejureScraper(court.config)
    elif court.scraper_type == "voris":
        return VorisScraper(court.config)
    elif court.scraper_type == "stub":
        return StubScraper(court.config)
    else:
        raise ValueError(f"Unknown scraper_type: {court.scraper_type!r}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    logger.info("=== FG Monitor starting ===")
    state = load_state()
    new_publications: dict[str, list[Publication]] = {}

    # --- Alle Gerichte scrapen (kein Playwright mehr erforderlich) ---
    for court in [c for c in COURTS if c.enabled]:
        logger.info("Scraping: %s", court.name)
        try:
            scraper = build_scraper(court)
            publications = scraper.fetch_latest()
            seen_ids = state["seen"].get(court.key, [])
            new_pubs = get_new_publications(publications, seen_ids)

            all_ids = [p.id for p in publications]
            state["seen"][court.key] = update_seen(seen_ids, all_ids)

            if new_pubs:
                new_publications[court.name] = new_pubs
                logger.info("  → %d neue Entscheidungen", len(new_pubs))
            else:
                logger.info("  → keine neuen Entscheidungen")
        except Exception as e:
            logger.error("Fehler beim Scrapen von %s: %s", court.name, e)

    # --- Update state timestamp and save ---
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    logger.info("State saved to %s", STATE_FILE)

    # --- Send email digest ---
    if new_publications:
        total = sum(len(v) for v in new_publications.values())
        logger.info(
            "Writing report: %d new publications from %d courts",
            total,
            len(new_publications),
        )
        write_report(new_publications)
        logger.info("Report written to LATEST_REPORT.md")
    else:
        logger.info("No new publications found — report not updated.")

    logger.info("=== FG Monitor done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
