import logging
import re

import requests
from bs4 import BeautifulSoup

from tools.scrapers.base import BaseScraper, Publication

logger = logging.getLogger(__name__)

BASE_URL = "https://voris.wolterskluwer-online.de/search"
PARAMS = {
    "query": "",
    "sort_order": "date_desc",
    "publicationtype": "publicationform-ats-filter!ATS_Rechtsprechung_Finanzgerichte_FG",
}
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; FG-Monitor/1.0; "
        "automated court publication tracker)"
    )
}


class VorisScraper(BaseScraper):
    """Scrapes FG Niedersachsen publications from voris.wolterskluwer-online.de.
    Uses plain requests + BeautifulSoup (no JavaScript required).
    """

    def fetch_latest(self) -> list[Publication]:
        try:
            resp = requests.get(
                BASE_URL, params=PARAMS, headers=HEADERS, timeout=30
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error("VorisScraper: request failed: %s", e)
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        publications = []

        result_items = soup.find_all(
            "div", class_=re.compile(r"egal-search-result-item-title")
        )

        for item in result_items[:20]:
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue

            href = link_tag["href"]
            # href is like /browse/document/{uuid}
            doc_id = href.rstrip("/").split("/")[-1]
            url = f"https://voris.wolterskluwer-online.de{href}"
            title = link_tag.get_text(strip=True)

            # Extract DD.MM.YYYY from the full item container text.
            # This is robust against class-name changes on the Voris portal.
            date = ""
            parent = item.parent
            if parent:
                item_text = parent.get_text(" ", strip=True)
                m = re.search(r"\d{2}\.\d{2}\.\d{4}", item_text)
                if m:
                    date = m.group(0)

            publications.append(
                Publication(
                    id=doc_id,
                    title=title,
                    date=date,
                    url=url,
                    court_key=self.config["court_key"],
                )
            )

        logger.info(
            "VorisScraper: found %d publications", len(publications)
        )
        return publications
