import logging
import re

from playwright.sync_api import Page, BrowserContext, TimeoutError as PlaywrightTimeout

from tools.scrapers.base import BaseScraper, Publication

logger = logging.getLogger(__name__)

# Timeout for page load and element waits (ms)
TIMEOUT = 30_000


class JurisScraper(BaseScraper):
    """Scrapes juris Bürgerservice portals (React SPA) using Playwright.

    Handles: FG Baden-Württemberg, Berlin-Brandenburg, Hamburg, Hessen,
    Mecklenburg-Vorpommern, Rheinland-Pfalz, Sachsen-Anhalt.

    All share the same underlying React frontend; the portal ID differs per state.
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
            # Navigate to the search page and wait for the app shell
            page.goto(base_url, wait_until="domcontentloaded", timeout=TIMEOUT)

            # The juris Bürgerservice SPA renders results after JS initialises.
            # We wait for a known selector that appears once the page is ready.
            # Primary selectors observed across all portals:
            #   - [data-testid="search-result-item"]
            #   - .result-list-item
            #   - article (generic fallback)
            result_selector = self._wait_for_results(page)
            if result_selector is None:
                logger.warning(
                    "JurisScraper [%s]: could not find result list", court_key
                )
                return []

            # Filter to Rechtsprechung (case law) if the URL doesn't already do so
            self._apply_filters(page, court_key)

            # Re-wait after filter application
            page.wait_for_timeout(2000)

            publications = self._extract_results(page, result_selector, court_key)

        except PlaywrightTimeout:
            logger.error(
                "JurisScraper [%s]: page load timed out at %s", court_key, base_url
            )
        except Exception as e:
            logger.error("JurisScraper [%s]: unexpected error: %s", court_key, e)
        finally:
            page.close()

        logger.info("JurisScraper [%s]: found %d publications", court_key, len(publications))
        return publications

    def _wait_for_results(self, page: Page) -> str | None:
        """Try known result selectors in order and return the one that works."""
        candidates = [
            "[data-testid='search-result-item']",
            ".result-list-item",
            ".bs-search-result-item",
            ".hitlist-item",
            "article.result",
            "li.result",
        ]
        for selector in candidates:
            try:
                page.wait_for_selector(selector, timeout=10_000)
                return selector
            except PlaywrightTimeout:
                continue
        return None

    def _apply_filters(self, page: Page, court_key: str) -> None:
        """Attempt to filter to Rechtsprechung documents if not already filtered.
        Silently skips if the filter UI is not found — results will still include
        all document types but deduplication handles noise over time.
        """
        try:
            # Look for a document-type filter button/chip labelled "Rechtsprechung"
            rspr_btn = page.locator(
                "button:has-text('Rechtsprechung'), "
                "label:has-text('Rechtsprechung'), "
                "a:has-text('Rechtsprechung')"
            ).first
            if rspr_btn.is_visible(timeout=3000):
                rspr_btn.click()
                page.wait_for_timeout(1500)
        except Exception:
            pass  # Filter not found or not needed

    def _extract_results(
        self, page: Page, result_selector: str, court_key: str
    ) -> list[Publication]:
        """Extract Publication objects from rendered result items."""
        items = page.query_selector_all(result_selector)
        publications = []

        for item in items[:20]:
            try:
                # Title + link: find the first anchor with meaningful text
                link = item.query_selector("a[href]")
                if not link:
                    continue

                href = link.get_attribute("href") or ""
                title = link.inner_text().strip()
                if not title or not href:
                    continue

                # Build absolute URL
                url = href if href.startswith("http") else self._absolute_url(href)

                # Derive a stable ID from the URL path
                doc_id = self._extract_id(href)

                # Date: look for a time element or text matching DD.MM.YYYY
                date = self._extract_date(item)

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
                logger.debug("JurisScraper: could not parse item: %s", e)
                continue

        return publications

    def _absolute_url(self, href: str) -> str:
        base = self.config["base_url"].rstrip("/")
        # Remove path portion, keep scheme+host
        from urllib.parse import urlparse
        parsed = urlparse(base)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        return origin + ("" if href.startswith("/") else "/") + href

    def _extract_id(self, href: str) -> str:
        # Try to pull the last meaningful path segment as the document ID
        parts = [p for p in href.rstrip("/").split("/") if p]
        return parts[-1] if parts else href

    def _extract_date(self, item) -> str:
        # 1) <time datetime="..."> element
        time_el = item.query_selector("time[datetime]")
        if time_el:
            dt = time_el.get_attribute("datetime") or ""
            m = re.search(r"\d{2}\.\d{2}\.\d{4}|\d{4}-\d{2}-\d{2}", dt)
            if m:
                return m.group(0)

        # 2) DD.MM.YYYY anywhere in the item text
        text = item.inner_text()
        m = re.search(r"\d{2}\.\d{2}\.\d{4}", text)
        if m:
            return m.group(0)

        return ""
