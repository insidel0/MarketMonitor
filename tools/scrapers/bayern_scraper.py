import logging
import re

from playwright.sync_api import BrowserContext, TimeoutError as PlaywrightTimeout

from tools.scrapers.base import BaseScraper, Publication

logger = logging.getLogger(__name__)

TIMEOUT = 30_000

# URL that pre-filters to Finanzgerichtsbarkeit decisions on gesetze-bayern.de
FILTER_URL = (
    "https://www.gesetze-bayern.de/Search/Filter"
    "/LEVEL1RSPRTREENODE/Finanzgerichtsbarkeit/DOKTYP/rspr"
)


class BayernScraper(BaseScraper):
    """Scrapes FG München / FG Nürnberg publications from gesetze-bayern.de.
    The site uses ASP.NET MVC with JavaScript-rendered search results.
    """

    def __init__(self, context: BrowserContext, config: dict):
        super().__init__(config)
        self.context = context

    def fetch_latest(self) -> list[Publication]:
        court_key: str = self.config["court_key"]
        publications: list[Publication] = []
        page = self.context.new_page()

        try:
            page.goto(FILTER_URL, wait_until="domcontentloaded", timeout=TIMEOUT)

            # Wait for result items — gesetze-bayern uses .result-item or similar
            result_selector = None
            for sel in [".result-item", ".search-result", "li.hit", "article", ".hitlist tr"]:
                try:
                    page.wait_for_selector(sel, timeout=10_000)
                    result_selector = sel
                    break
                except PlaywrightTimeout:
                    continue

            if result_selector is None:
                logger.warning("BayernScraper: could not find result list")
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

                    url = href if href.startswith("http") else f"https://www.gesetze-bayern.de{href}"
                    doc_id = href.rstrip("/").split("/")[-1]

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
                    logger.debug("BayernScraper: could not parse item: %s", e)

        except PlaywrightTimeout:
            logger.error("BayernScraper: page load timed out")
        except Exception as e:
            logger.error("BayernScraper: unexpected error: %s", e)
        finally:
            page.close()

        logger.info("BayernScraper: found %d publications", len(publications))
        return publications
