"""Generischer Selector-basierter Scraper für Unternehmens-News-Seiten.

Jede Quellseite liefert eine Liste von "Artikel-Karten" (Item-Elemente). Pro
Item werden relative CSS-Selektoren ausgewertet, um Titel, URL, optional Datum
und Zusammenfassung zu extrahieren. Die Selektoren stehen in
``companies_config.py`` pro Unternehmen.

Vorteile gegenüber LLM-Extraktion: keine API-Kosten, deterministisch.
Nachteil: bei Redesigns einer Quellseite brechen die Selektoren — dann müssen
sie nachgezogen werden.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


@dataclass
class SiteSelectors:
    item: str                              # CSS-Selektor für jede Artikel-Karte
    title: str                             # relativ zum Item
    url: str | None = None                 # relativ; None ⇒ url = href des title-Elements
    date: str | None = None                # relativ, optional
    summary: str | None = None             # relativ, optional
    date_attr: str | None = None           # falls Datum in einem Attribut steckt (z. B. ``datetime``)
    date_formats: list[str] = field(default_factory=lambda: [
        "%Y-%m-%d", "%d.%m.%Y", "%d %B %Y", "%d %b %Y",
        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ",
    ])
    max_items: int = 30                    # Sicherheitslimit pro Seite


@dataclass
class Article:
    title: str
    url: str
    date: str | None = None
    summary: str | None = None


def _text(el: Tag | None) -> str:
    if el is None:
        return ""
    return " ".join(el.get_text(" ", strip=True).split())


def _resolve_url(item: Tag, base_url: str, selectors: SiteSelectors) -> str | None:
    if selectors.url:
        node = item.select_one(selectors.url)
    else:
        # Default-Auflösung in dieser Reihenfolge:
        #   1. Item-Element ist selbst ein <a> (z. B. wenn der ganze Card ein Link ist)
        #   2. Titel-Element ist ein <a>
        #   3. <a> innerhalb des Titels
        #   4. erstes <a> im Item (Fallback)
        node = item if item.name == "a" else None
        if node is None:
            title_node = item.select_one(selectors.title)
            if title_node is not None:
                node = title_node if title_node.name == "a" else title_node.find("a")
        if node is None:
            node = item.find("a")
    if node is None:
        return None
    href = node.get("href")
    if not href:
        return None
    absolute = urljoin(base_url, href.strip())
    return absolute.split("#", 1)[0]


_GERMAN_MONTHS = {
    # Lange Namen zuerst, damit "Januar" nicht von "Jan." überschrieben wird.
    "Januar": "January", "Februar": "February", "März": "March", "April": "April",
    "Mai": "May", "Juni": "June", "Juli": "July", "August": "August",
    "September": "September", "Oktober": "October", "November": "November", "Dezember": "December",
    "Jan": "Jan", "Feb": "Feb", "Mrz": "Mar", "Apr": "Apr", "Jun": "Jun", "Jul": "Jul",
    "Aug": "Aug", "Sept": "Sep", "Sep": "Sep", "Okt": "Oct", "Nov": "Nov", "Dez": "Dec",
}


def _normalize_date(raw: str, formats: list[str]) -> str | None:
    if not raw:
        return None
    raw = raw.strip()
    # "Veröffentlicht am 12.05.2026" / "23 Apr. 2026" / "2026-05-18" — alles rausziehen
    m = re.search(
        r"\d{1,2}[./]\d{1,2}[./]\d{2,4}|\d{4}-\d{2}-\d{2}T?\d*:?\d*:?\d*Z?|\d{1,2}\.?\s+\w+\.?\s+\d{4}",
        raw,
    )
    candidate = m.group(0) if m else raw
    # Punkt nach Monats-Abkürzung loswerden ("23 Apr. 2026" → "23 Apr 2026"),
    # numerische Datumsformate wie "12.05.2026" aber NICHT antasten.
    candidate = re.sub(r"(?<=[A-Za-z])\.\s*", " ", candidate)
    candidate = re.sub(r"\s+", " ", candidate).strip()
    # Deutsche Monatsnamen (lang & abgekürzt) → englisch
    candidate_en = candidate
    for de, en in _GERMAN_MONTHS.items():
        candidate_en = re.sub(rf"\b{de}\b", en, candidate_en)
    for fmt in formats:
        try:
            return datetime.strptime(candidate_en, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _extract_date(item: Tag, selectors: SiteSelectors) -> str | None:
    if not selectors.date:
        return None
    node = item.select_one(selectors.date)
    if node is None:
        return None
    raw = ""
    if selectors.date_attr:
        raw = node.get(selectors.date_attr, "") or ""
    if not raw:
        raw = _text(node)
    return _normalize_date(raw, selectors.date_formats)


def scrape_articles(
    *,
    html: str,
    base_url: str,
    selectors: SiteSelectors,
) -> list[Article]:
    """Extrahiere Artikel aus einer Übersichtsseite mittels CSS-Selektoren."""
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(selectors.item)
    if not items:
        logger.warning("No items matched selector %r on %s", selectors.item, base_url)
        return []

    articles: list[Article] = []
    seen_urls: set[str] = set()

    for item in items[: selectors.max_items]:
        title = _text(item.select_one(selectors.title))
        url = _resolve_url(item, base_url, selectors)
        if not title or not url or url in seen_urls:
            continue
        seen_urls.add(url)
        articles.append(Article(
            title=title,
            url=url,
            date=_extract_date(item, selectors),
            summary=_text(item.select_one(selectors.summary)) if selectors.summary else None,
        ))
    logger.info("Scraped %d articles from %s", len(articles), base_url)
    return articles
