import logging
import re

from playwright.sync_api import BrowserContext, TimeoutError as PlaywrightTimeout

from tools.scrapers.base import BaseScraper, Publication

logger = logging.getLogger(__name__)

TIMEOUT = 60_000
BASE_URL = "https://nrwesuche.justiz.nrw.de/index.php"


class NRWScraper(BaseScraper):
    """Scrapes FG NRW (Köln, Düsseldorf, Münster) from nrwesuche.justiz.nrw.de.

    The page is server-rendered HTML with confirmed form/result IDs:
      - Form:       #myNrweForm
      - Court type: #gerichtstyp  (select dropdown)
      - Results:    .alleErgebnisse
    """

    def __init__(self, context: BrowserContext, config: dict):
        super().__init__(config)
        self.context = context

    def fetch_latest(self) -> list[Publication]:
        court_key: str = self.config["court_key"]
        publications: list[Publication] = []
        page = self.context.new_page()

        try:
            page.goto(BASE_URL, wait_until="load", timeout=TIMEOUT)

            # Select "FG" (Finanzgericht) in the #gerichtstyp dropdown
            try:
                page.wait_for_selector("#gerichtstyp", timeout=15_000)
                # Try known option values for Finanzgericht
                for value in ["FG", "Finanzgericht", "finanzgericht"]:
                    try:
                        page.select_option("#gerichtstyp", value=value)
                        break
                    except Exception:
                        continue
            except PlaywrightTimeout:
                logger.warning("NRWScraper: #gerichtstyp not found, submitting without filter")

            # Submit the search form
            try:
                submit = page.locator(
                    "#span_absenden, #button_suche_span, "
                    "button[type='submit'], input[type='submit']"
                ).first
                if submit.is_visible(timeout=5000):
                    submit.click()
                else:
                    # Fallback: submit the form directly
                    page.evaluate("document.getElementById('myNrweForm').submit()")
            except Exception as e:
                logger.warning("NRWScraper: could not click submit: %s", e)

            # Wait for results to appear
            try:
                page.wait_for_selector(".alleErgebnisse", timeout=20_000)
            except PlaywrightTimeout:
                logger.warning("NRWScraper: .alleErgebnisse not found after submit")
                return []

            # Extract result items — try common child selectors
            items = []
            for sel in [".alleErgebnisse li", ".alleErgebnisse .ergebnis",
                        ".alleErgebnisse tr", ".alleErgebnisse div"]:
                items = page.query_selector_all(sel)
                if items:
                    break

            # Fallback: use all links inside .alleErgebnisse
            if not items:
                links = page.query_selector_all(".alleErgebnisse a[href]")
                for link in links[:20]:
                    try:
                        href = link.get_attribute("href") or ""
                        title = link.inner_text().strip()
                        if not href or not title:
                            continue
                        url = href if href.startswith("http") else f"https://nrwesuche.justiz.nrw.de{href}"
                        doc_id = href.rstrip("/").split("/")[-1] or href
                        publications.append(Publication(
                            id=doc_id, title=title, date="", url=url, court_key=court_key
                        ))
                    except Exception:
                        continue
                return publications

            for item in items[:20]:
                try:
                    link = item.query_selector("a[href]")
                    if not link:
                        continue
                    href = link.get_attribute("href") or ""
                    title = link.inner_text().strip()
                    if not href or not title:
                        continue

                    url = href if href.startswith("http") else f"https://nrwesuche.justiz.nrw.de{href}"
                    doc_id = href.rstrip("/").split("/")[-1] or href

                    text = item.inner_text()
                    m = re.search(r"\d{2}\.\d{2}\.\d{4}", text)
                    date = m.group(0) if m else ""

                    publications.append(Publication(
                        id=doc_id, title=title, date=date, url=url, court_key=court_key
                    ))
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
