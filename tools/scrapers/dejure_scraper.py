"""Scrapes dejure.org Rechtsprechung for a specific Finanzgericht.

dejure.org is a free German legal database. The URL
  https://dejure.org/dienste/rechtsprechung?gericht=FG%20Hamburg
returns a server-rendered list of decisions filtered exclusively to
that court — no JavaScript required.

Each <li> in the result list contains an <a> whose href encodes
Gericht, Datum (DD.MM.YYYY) and Aktenzeichen as URL parameters, e.g.:
  /dienste/vernetzung/rechtsprechung?Gericht=FG%20Hamburg&Datum=19.03.2026&Aktenzeichen=6%20V%2030%2F26

Multiple pages exist (?seite=N). We fetch up to MAX_PAGES pages and
stop early when all entries on a page are outside the 28-day window.
"""
import logging
import re
import time
from urllib.parse import quote, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

from tools.scrapers.base import BaseScraper, Publication

logger = logging.getLogger(__name__)

BASE_URL = "https://dejure.org/dienste/rechtsprechung"
DECISION_HOST = "https://dejure.org"
MAX_PAGES = 3
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; FG-Monitor/1.0; "
        "automatisierte Rechtsprechungsübersicht)"
    ),
    "Accept-Language": "de-DE,de;q=0.9",
}


class DejureScraper(BaseScraper):
    """Scrapes dejure.org Rechtsprechung for one Finanzgericht.

    Required config keys:
      court_key   – internal key (e.g. 'fg_hamburg')
      gericht     – URL-decoded court name (e.g. 'FG Hamburg')
    """

    def fetch_latest(self) -> list[Publication]:
        court_key: str = self.config["court_key"]
        gericht: str = self.config["gericht"]
        publications: list[Publication] = []

        # dejure.org uses Latin-1 (ISO-8859-1) percent-encoding for umlauts,
        # e.g. ü → %FC, ö → %F6. Python's requests encodes as UTF-8 (%C3%BC),
        # which dejure.org does not recognise. Build the URL manually.
        gericht_enc = quote(gericht, encoding="latin-1")

        for page_num in range(1, MAX_PAGES + 1):
            url = f"{BASE_URL}?gericht={gericht_enc}"
            if page_num > 1:
                url += f"&seite={page_num}"

            try:
                resp = requests.get(url, headers=HEADERS, timeout=30)
                resp.raise_for_status()
            except requests.RequestException as e:
                logger.warning(
                    "DejureScraper [%s]: Seite %d Fehler: %s", court_key, page_num, e
                )
                break

            page_pubs = self._parse_page(resp.text, court_key)
            if not page_pubs:
                break

            publications.extend(page_pubs)

            # Polite delay between pages
            if page_num < MAX_PAGES:
                time.sleep(1)

        logger.info(
            "DejureScraper [%s]: %d Entscheidungen gefunden", court_key, len(publications)
        )
        return publications

    def _parse_page(self, html: str, court_key: str) -> list[Publication]:
        soup = BeautifulSoup(html, "html.parser")
        publications: list[Publication] = []
        seen_ids: set[str] = set()

        # dejure lists each decision as <li><a href="...">text</a></li>
        # The href points to /dienste/vernetzung/rechtsprechung?...
        for link in soup.find_all(
            "a", href=re.compile(r"/dienste/vernetzung/rechtsprechung")
        ):
            href = link.get("href", "")
            if not href:
                continue

            # Parse URL params: Gericht, Datum, Aktenzeichen
            parsed = urlparse(href)
            params = parse_qs(parsed.query)

            datum = params.get("Datum", [""])[0]          # DD.MM.YYYY
            aktenzeichen = params.get("Aktenzeichen", [""])[0]

            if not datum and not aktenzeichen:
                continue

            # Stable unique ID per decision
            az_slug = (
                aktenzeichen.replace(" ", "_")
                             .replace("/", "-")
                             .replace("\\", "-")
            )
            doc_id = f"{court_key}_{datum}_{az_slug}"
            if doc_id in seen_ids:
                continue
            seen_ids.add(doc_id)

            # Full URL
            url = (
                DECISION_HOST + href
                if href.startswith("/")
                else href
            )

            # Link text: typically "DD.MM.YYYY - Aktenzeichen\nSubject text"
            raw_text = link.get_text(" ", strip=True)
            # Try title attribute first (often cleaner)
            title_attr = link.get("title", "").strip()

            # Build a readable title: "Aktenzeichen — Subject"
            # Strip date prefix from raw text (it's already in the date field)
            date_prefix_re = re.compile(r"^\d{2}\.\d{2}\.\d{4}\s*[-–]\s*")
            clean_text = date_prefix_re.sub("", raw_text).strip()
            title = clean_text if clean_text else (title_attr or aktenzeichen)

            publications.append(
                Publication(
                    id=doc_id,
                    title=title,
                    date=datum,
                    url=url,
                    court_key=court_key,
                )
            )

        return publications
