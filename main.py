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
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

from courts_config import COURTS, CourtConfig
from tools.scrapers.base import Publication
from tools.scrapers.stub_scraper import StubScraper
from tools.scrapers.voris_scraper import VorisScraper
from tools.scrapers.juris_scraper import JurisScraper
from tools.scrapers.bayern_scraper import BayernScraper
from tools.scrapers.nrw_scraper import NRWScraper
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


def get_new_publications(
    publications: list[Publication], seen_ids: list[str]
) -> list[Publication]:
    seen_set = set(seen_ids)
    return [p for p in publications if p.id not in seen_set]


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
    if court.scraper_type == "voris":
        return VorisScraper(court.config)
    elif court.scraper_type == "juris":
        if playwright_context is None:
            raise RuntimeError("JurisScraper requires a Playwright context")
        return JurisScraper(playwright_context, court.config)
    elif court.scraper_type == "bayern":
        if playwright_context is None:
            raise RuntimeError("BayernScraper requires a Playwright context")
        return BayernScraper(playwright_context, court.config)
    elif court.scraper_type == "nrw":
        if playwright_context is None:
            raise RuntimeError("NRWScraper requires a Playwright context")
        return NRWScraper(playwright_context, court.config)
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

    # Separate courts by whether they need Playwright
    needs_playwright = [c for c in COURTS if c.enabled and c.scraper_type in ("juris", "bayern", "nrw")]
    no_playwright = [c for c in COURTS if c.enabled and c.scraper_type not in ("juris", "bayern", "nrw")]

    # --- Run non-Playwright scrapers first (fast) ---
    for court in no_playwright:
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
                logger.info("  → %d new publications", len(new_pubs))
            else:
                logger.info("  → no new publications")
        except Exception as e:
            logger.error("Failed to scrape %s: %s", court.name, e)

    # --- Run Playwright scrapers (shared browser instance) ---
    if needs_playwright:
        logger.info("Starting Playwright browser for %d courts...", len(needs_playwright))
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            context = browser.new_context(
                locale="de-DE",
                user_agent=(
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
            )

            for court in needs_playwright:
                logger.info("Scraping: %s", court.name)
                try:
                    scraper = build_scraper(court, playwright_context=context)
                    publications = scraper.fetch_latest()
                    seen_ids = state["seen"].get(court.key, [])
                    new_pubs = get_new_publications(publications, seen_ids)

                    all_ids = [p.id for p in publications]
                    state["seen"][court.key] = update_seen(seen_ids, all_ids)

                    if new_pubs:
                        new_publications[court.name] = new_pubs
                        logger.info("  → %d new publications", len(new_pubs))
                    else:
                        logger.info("  → no new publications")
                except Exception as e:
                    logger.error("Failed to scrape %s: %s", court.name, e)

            context.close()
            browser.close()

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
