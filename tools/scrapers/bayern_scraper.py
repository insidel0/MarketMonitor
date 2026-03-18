import logging
import re

from playwright.sync_api import BrowserContext, TimeoutError as PlaywrightTimeout

from tools.scrapers.base import BaseScraper, Publication

logger = logging.getLogger(__name__)

TIMEOUT = 60_000
SEARCH_URL = "https://www.gesetze-bayern.de/Search/Hitlist"


class BayernScraper(BaseScraper):
    """Scrapes FG München / FG Nürnberg publications from gesetze-bayern.de.

    The site is server-rendered (ASP.NET MVC) but requires a search query to
    display results. Strategy:
      1. Navigate to the Hitlist page with pre-set filter parameters in the URL
      2. If that shows no results, click the Gerichtsentscheidungen / FG link
      3. Extract result links
    """

    def __init__(self, context: BrowserContext, config: dict):
        super().__init__(config)
        self.context = context

    def fetch_latest(self) -> list[Publication]:
        court_key: str = self.config["court_key"]
        publications: list[Publication] = []
        page = self.context.new_page()

        try:
            # Navigate to Hitlist — clicking through "Gerichtsentscheidungen"
            # then filtering to Finanzgerichtsbarkeit
            page.goto(SEARCH_URL, wait_until="load", timeout=TIMEOUT)

            # Try to click the "Gerichtsentscheidungen" category link
            try:
                # The page shows category counts like "Gerichtsentscheidungen (24109)"
                recht_link = page.locator(
                    "a:has-text('Gerichtsentscheidungen'), "
                    "a[href*='DOKTYP/rspr'], "
                    "a[href*='rspr']"
                ).first
                if recht_link.is_visible(timeout=8000):
                    recht_link.click()
                    page.wait_for_load_state("load", timeout=TIMEOUT)
            except Exception:
                pass

            # Now try to filter to Finanzgerichtsbarkeit
            try:
                fg_link = page.locator(
                    "a:has-text('Finanzgerichtsbarkeit'), "
                    "a[href*='Finanzgerichtsbarkeit']"
                ).first
                if fg_link.is_visible(timeout=8000):
                    fg_link.click()
                    page.wait_for_load_state("load", timeout=TIMEOUT)
            except Exception:
                pass

            # Extract all document links on the resulting page
            # gesetze-bayern.de links documents as /Content/Document/byid/{id}
            # or /Search/Hitlist/... — look for any anchor with document references
            publications = self._extract_links(page, court_key)

        except PlaywrightTimeout:
            logger.error("BayernScraper: page load timed out")
        except Exception as e:
            logger.error("BayernScraper: unexpected error: %s", e)
        finally:
            page.close()

        logger.info("BayernScraper: found %d publications", len(publications))
        return publications

    def _extract_links(self, page, court_key: str) -> list[Publication]:
        """Extract publication links from the current page."""
        publications = []
        seen_ids: set[str] = set()

        # Try multiple result container selectors
        for container_sel in [
            ".hitlist", ".result-list", ".search-results",
            "#content", "main", "article"
        ]:
            try:
                container = page.query_selector(container_sel)
                if not container:
                    continue
                links = container.query_selector_all("a[href]")
                if len(links) > 2:  # Found meaningful links
                    for link in links[:30]:
                        pub = self._parse_link(link, court_key, seen_ids)
                        if pub:
                            publications.append(pub)
                            if len(publications) >= 20:
                                break
                    if publications:
                        break
            except Exception:
                continue

        # Fallback: grab all anchors on the page
        if not publications:
            links = page.query_selector_all("a[href]")
            for link in links:
                pub = self._parse_link(link, court_key, seen_ids)
                if pub:
                    publications.append(pub)
                if len(publications) >= 20:
                    break

        return publications

    def _parse_link(self, link, court_key: str, seen_ids: set) -> Publication | None:
        try:
            href = link.get_attribute("href") or ""
            title = link.inner_text().strip()
            # Filter: must look like a document link (contains year/decision markers)
            if not href or not title or len(title) < 10:
                return None
            if any(skip in href for skip in ["changefontsize", "changecontrast",
                                              "javascript:", "#", "mailto:"]):
                return None

            url = href if href.startswith("http") else f"https://www.gesetze-bayern.de{href}"
            doc_id = href.rstrip("/").split("/")[-1]
            if not doc_id or doc_id in seen_ids:
                return None
            seen_ids.add(doc_id)

            # Look for date near the link
            text = link.evaluate(
                """(el) => {
                    let p = el.parentElement;
                    for (let i = 0; i < 4; i++) {
                        if (!p) break;
                        const m = p.innerText.match(/\\d{2}\\.\\d{2}\\.\\d{4}/);
                        if (m) return m[0];
                        p = p.parentElement;
                    }
                    return '';
                }"""
            )
            return Publication(
                id=doc_id, title=title, date=text or "", url=url, court_key=court_key
            )
        except Exception:
            return None
