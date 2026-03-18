import logging
import re
from urllib.parse import urlparse

from playwright.sync_api import Page, BrowserContext, TimeoutError as PlaywrightTimeout

from tools.scrapers.base import BaseScraper, Publication

logger = logging.getLogger(__name__)

TIMEOUT = 60_000   # 60s for full page load
BOOT_TIMEOUT = 45_000  # wait for SPA boot to finish


class JurisScraper(BaseScraper):
    """Scrapes juris Bürgerservice portals (React SPA) using Playwright.

    Handles: FG Baden-Württemberg, Berlin-Brandenburg, Hamburg, Hessen,
    Mecklenburg-Vorpommern, Rheinland-Pfalz, Sachsen-Anhalt.

    Strategy:
      1. Navigate to the search URL (wait for 'load' event)
      2. Wait for the SPA loading screen (.loading_msg) to disappear
      3. Collect all document links via a[href*="/document/"]
      4. Filter + deduplicate, return up to 20 newest
    """

    def __init__(self, context: BrowserContext, config: dict):
        super().__init__(config)
        self.context = context

    def fetch_latest(self) -> list[Publication]:
        base_url: str = self.config["base_url"]
        court_key: str = self.config["court_key"]
        publications: list[Publication] = []

        page = self.context.new_page()
        try:
            # Use 'load' so the JS bundle has time to start executing
            page.goto(base_url, wait_until="load", timeout=TIMEOUT)

            # The SPA shows .loading_msg while it boots.
            # Wait until that element is hidden/gone — then React has rendered.
            try:
                page.wait_for_selector(
                    ".loading_msg", state="hidden", timeout=BOOT_TIMEOUT
                )
            except PlaywrightTimeout:
                # If loading_msg never appeared or never disappeared, proceed anyway
                pass

            # Give React one extra second to finish rendering the result list
            page.wait_for_timeout(3000)

            # Try to click a "Rechtsprechung" filter to narrow to case law
            self._apply_filters(page)

            # Wait a moment for any filter-triggered re-render
            page.wait_for_timeout(2000)

            publications = self._extract_document_links(page, court_key)

        except PlaywrightTimeout:
            logger.error(
                "JurisScraper [%s]: page load timed out at %s", court_key, base_url
            )
        except Exception as e:
            logger.error("JurisScraper [%s]: unexpected error: %s", court_key, e)
        finally:
            page.close()

        logger.info(
            "JurisScraper [%s]: found %d publications", court_key, len(publications)
        )
        return publications

    def _apply_filters(self, page: Page) -> None:
        """Try to click a Rechtsprechung filter. Silently skip if not found."""
        try:
            rspr_btn = page.locator(
                "button:has-text('Rechtsprechung'), "
                "label:has-text('Rechtsprechung'), "
                "a:has-text('Rechtsprechung')"
            ).first
            if rspr_btn.is_visible(timeout=4000):
                rspr_btn.click()
                page.wait_for_timeout(2000)
        except Exception:
            pass

    def _extract_document_links(
        self, page: Page, court_key: str
    ) -> list[Publication]:
        """Collect all a[href*='/document/'] links from the rendered page."""
        base_url: str = self.config["base_url"]
        parsed = urlparse(base_url)
        origin = f"{parsed.scheme}://{parsed.netloc}"

        # All document links on juris portals follow the pattern:
        #   /{portalId}/document/{docId}
        links = page.query_selector_all("a[href*='/document/']")
        seen_ids: set[str] = set()
        publications: list[Publication] = []

        for link in links:
            try:
                href = link.get_attribute("href") or ""
                title = link.inner_text().strip()
                if not href or not title or len(title) < 5:
                    continue

                # Build absolute URL
                url = href if href.startswith("http") else origin + href
                doc_id = href.rstrip("/").split("/")[-1]

                # Skip duplicates (same document linked multiple times)
                if doc_id in seen_ids:
                    continue
                seen_ids.add(doc_id)

                # Extract date from surrounding context
                date = self._extract_date_near_link(page, link)

                publications.append(
                    Publication(
                        id=doc_id,
                        title=title,
                        date=date,
                        url=url,
                        court_key=court_key,
                    )
                )
                if len(publications) >= 20:
                    break
            except Exception as e:
                logger.debug("JurisScraper: could not parse link: %s", e)

        return publications

    def _extract_date_near_link(self, page: Page, link) -> str:
        """Look for a DD.MM.YYYY date in the link's parent container."""
        try:
            # Walk up to find a container with date text
            # Use JS to get the parent element's text
            text = page.evaluate(
                """(el) => {
                    let p = el.parentElement;
                    for (let i = 0; i < 5; i++) {
                        if (!p) break;
                        const m = p.innerText.match(/\\d{2}\\.\\d{2}\\.\\d{4}/);
                        if (m) return m[0];
                        p = p.parentElement;
                    }
                    return '';
                }""",
                link,
            )
            return text or ""
        except Exception:
            return ""
