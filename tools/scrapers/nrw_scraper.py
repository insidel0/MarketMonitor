import logging
import re

from playwright.sync_api import BrowserContext, TimeoutError as PlaywrightTimeout

from tools.scrapers.base import BaseScraper, Publication

logger = logging.getLogger(__name__)

TIMEOUT = 30_000
BASE_URL = "https://nrwesuche.justiz.nrw.de/index.php"


class NRWScraper(BaseScraper):
    """Scrapes FG NRW (Köln, Düsseldorf, Münster) from nrwesuche.justiz.nrw.de.
    The page uses a Drupal/SOLR frontend that renders results client-side.
    Playwright submits the form with the Finanzgericht filter and extracts results.
    """

    def __init__(self, context: BrowserContext, config: dict):
        super().__init__(config)
        self.context = context

    def fetch_latest(self) -> list[Publication]:
        court_key: str = self.config["court_key"]
        publications: list[Publication] = []
        page = self.context.new_page()

        try:
            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=TIMEOUT)

            # Try to set the court type filter to "Finanzgericht"
            # The NRW site has a search form; attempt to select Finanzgericht
            self._apply_court_filter(page)

            # Wait for results to render
            result_selector = None
            for sel in [
                ".alleErgebnisse .ergebnis",
                ".alleErgebnisse li",
                ".result-list li",
                ".solr-results li",
                "#solrNrwe li",
                ".views-row",
            ]:
                try:
                    page.wait_for_selector(sel, timeout=12_000)
                    result_selector = sel
                    break
                except PlaywrightTimeout:
                    continue

            if result_selector is None:
                logger.warning("NRWScraper: could not find result list after filter")
                return []

            items = page.query_selector_all(result_selector)
            for item in items[:20]:
                try:
                    link = item.query_selector("a[href]")
                    if not link:
                        continue
                    href = link.get_attribute("href") or ""
                    title = link.inner_text().strip()
                    if not title or not href:
                        continue

                    url = (
                        href if href.startswith("http")
                        else f"https://nrwesuche.justiz.nrw.de{href}"
                    )
                    doc_id = href.rstrip("/").split("/")[-1] or href

                    text = item.inner_text()
                    m = re.search(r"\d{2}\.\d{2}\.\d{4}", text)
                    date = m.group(0) if m else ""

                    publications.append(
                        Publication(
                            id=doc_id,
                            title=title,
                            date=date,
                            url=url,
                            court_key=court_key,
                        )
                    )
                except Exception as e:
                    logger.debug("NRWScraper: could not parse item: %s", e)

        except PlaywrightTimeout:
            logger.error("NRWScraper: page load timed out")
        except Exception as e:
            logger.error("NRWScraper: unexpected error: %s", e)
        finally:
            page.close()

        logger.info("NRWScraper: found %d publications", len(publications))
        return publications

    def _apply_court_filter(self, page) -> None:
        """Try to select 'Finanzgericht' in the court type dropdown/filter."""
        try:
            # Try a <select> dropdown first
            selects = page.query_selector_all("select")
            for sel_el in selects:
                options = sel_el.query_selector_all("option")
                for opt in options:
                    if "Finanzgericht" in (opt.inner_text() or ""):
                        sel_el.select_option(value=opt.get_attribute("value"))
                        break

            # Try clicking a submit/search button
            submit = page.locator(
                "button[type='submit'], input[type='submit'], button:has-text('Suchen')"
            ).first
            if submit.is_visible(timeout=3000):
                submit.click()
                page.wait_for_timeout(2000)
        except Exception:
            pass  # Filter not available; results will be all courts
