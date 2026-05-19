"""Zentrale Liste der überwachten Steuerberatungs-/Kanzlei-Websites.

Quelle: ``Steuernews_Links_02042026.xlsx`` → Sheet ``JUVE Top30 2025``.

Jede Zeile beschreibt ein Unternehmen plus die CSS-Selektoren, mit denen
der Agent auf der angegebenen URL die Artikelkarten extrahiert. Wer noch
keine Selektoren hat (``selectors=None``), wird vom Agenten übersprungen
und im Log gemeldet — als Hinweis, dass die Selektoren noch zu hinterlegen
sind.
"""
from __future__ import annotations

from dataclasses import dataclass

from tools.scrape_articles import SiteSelectors


@dataclass
class CompanyConfig:
    rank: int           # JUVE-Rang 2025
    key: str            # Eindeutiger Schlüssel in state.json (slug)
    name: str           # Anzeigename im Bericht
    url: str            # Startpunkt für den Scraper
    page_type: str      # Hinweis auf Seitentyp (Newsroom, Blog, …)
    note: str           # Freitextkommentar aus der Quelltabelle
    selectors: SiteSelectors | None = None  # None ⇒ "TODO, noch nicht tunen"
    enabled: bool = True


COMPANIES: list[CompanyConfig] = [
    # ── 1. EY ─────────────────────────────────────────────────────────────────
    CompanyConfig(
        rank=1, key="ey", name="EY",
        url="https://www.ey.com/de_de/technical/steuernachrichten",
        page_type="dedizierte Steuernews-Seite",
        note="offizielle EY-Steuernachrichten",
        selectors=SiteSelectors(
            item="li.up-trending-section--item",
            title="p.up-trending-section--item__link-text",
            url="a.up-trending-section--item__link-name",
            date="span.date",
            summary="p.up-trending-section--item__link-description",
        ),
    ),

    # ── 2. KPMG ───────────────────────────────────────────────────────────────
    CompanyConfig(
        rank=2, key="kpmg", name="KPMG",
        url="https://kpmg.com/de/de/themen/corporate-governance-und-compliance/kpmg-tax-news.html",
        page_type="dedizierte Steuernews-Seite",
        note="offizielle KPMG Tax News",
        selectors=SiteSelectors(
            item="div.cmp-teaser",
            title="h3.cmp-teaser__title",
            url="h3.cmp-teaser__title a",
            summary="div.cmp-teaser__description",
        ),
    ),

    # ── 3. PwC ────────────────────────────────────────────────────────────────
    CompanyConfig(
        rank=3, key="pwc", name="PricewaterhouseCoopers (PwC)",
        url="https://blogs.pwc.de/de/steuern-und-recht",
        page_type="dedizierter Steuerblog",
        note="PwC Blog zu Steuern & Recht",
        selectors=SiteSelectors(
            item="article.article-teaser",
            title="h3.article-teaser--title",
            summary="p.article-teaser--excerpt",
            date="time",
            date_attr="datetime",
        ),
    ),

    # ── 4. Deloitte ───────────────────────────────────────────────────────────
    CompanyConfig(
        rank=4, key="deloitte", name="Deloitte",
        url="https://www.deloitte-tax-news.de/home/index.html",
        page_type="dedizierte Steuernews-Seite",
        note="offizielle Deloitte Tax-News",
        selectors=SiteSelectors(
            item="div.moduleContentTeaser",
            title="h3",
        ),
    ),

    # ── 5. WTS ────────────────────────────────────────────────────────────────
    CompanyConfig(
        rank=5, key="wts", name="WTS",
        url="https://wts.com/de-de/news-knowledge/tax-weekly",
        page_type="dedizierte Steuernews-Seite",
        note="JS-gerendert — bisher keine server-seitig sichtbaren Artikel; selectors noch zu tunen",
        selectors=None,
    ),

    # ── 6. FGS — Flick Gocke Schaumburg ───────────────────────────────────────
    CompanyConfig(
        rank=6, key="fgs", name="Flick Gocke Schaumburg",
        url="https://www.fgs.de/news-and-insights",
        page_type="News-/Insights-Seite",
        note="News, Blogbeiträge, Podcasts und Fachpublikationen",
        selectors=SiteSelectors(
            item="div.blog-teaser-item",
            title="div.blog-title",
            url="div.image-container-16-9 a",
        ),
    ),

    # ── 7. Rödl & Partner ─────────────────────────────────────────────────────
    CompanyConfig(
        rank=7, key="roedl", name="Rödl & Partner",
        url="https://www.roedl.com/newsletter/early-tax-birds/",
        page_type="dedizierter Steuer-Newsletter",
        note="wöchentliche Entwicklungen im Steuerrecht",
        selectors=SiteSelectors(
            item="a.blog_archive_item--list",  # das Item ist selbst der Link
            title="h3.headline",
            date="div.blog_archive_item__date",
        ),
    ),

    # ── 8. RSM Ebner Stolz ────────────────────────────────────────────────────
    CompanyConfig(
        rank=8, key="ebner_stolz", name="RSM Ebner Stolz",
        url="https://www.ebnerstolz.de/de/",
        page_type="News-Einstieg auf Website",
        note="Startseite: nur die Karten mit data-event-category=Aktuelle News",
        selectors=SiteSelectors(
            item='a[data-event-category="Aktuelle News"]',
            title=None,                  # Item selbst ist der Anker
            title_attr="data-event-label",
        ),
    ),

    # ── 9. BDO ────────────────────────────────────────────────────────────────
    CompanyConfig(
        rank=9, key="bdo", name="BDO",
        url="https://www.bdo.de/de-de/insights/news-bdo",
        page_type="dedizierte Tax-/Legal-Update-Seite",
        note="JS-gerendert — nur Skeleton-Platzhalter im HTML; selectors noch zu tunen",
        selectors=None,
    ),

    # ── 10. Forvis Mazars ─────────────────────────────────────────────────────
    CompanyConfig(
        rank=10, key="forvis_mazars", name="Forvis Mazars",
        url="https://www.forvismazars.com/de/de/ueber-uns/aktuelles/nachrichten",
        page_type="News-Seite", note="offizielle Nachrichten-Seite",
        selectors=SiteSelectors(
            item="div.Folder",
            title="h3.Folders-title",
            url="p.Folders-cta a.Button",
            summary="div.Folders-text",
        ),
    ),

    # ── 11. Grant Thornton ────────────────────────────────────────────────────
    CompanyConfig(
        rank=11, key="grant_thornton", name="Grant Thornton",
        url="https://www.grantthornton.de/presse/",
        page_type="Newsroom", note="Pressemitteilungen und Deal News",
        selectors=SiteSelectors(
            item="div.content-item",
            title="div.gt-body-text.item-content__descriptions",
            url="a.item-content__img",
            date="div.gt-body-text.overline.grey",
        ),
    ),

    # ── 12. Baker Tilly ───────────────────────────────────────────────────────
    CompanyConfig(
        rank=12, key="baker_tilly", name="Baker Tilly",
        url="https://www.bakertilly.de/",
        page_type="News-Einstieg auf Website",
        note="Startseite mit Card-Liste der aktuellen Beiträge",
        selectors=SiteSelectors(
            item="div.card.card-news-teaser",
            title="div.card-text p",
            url="a.card-link",
        ),
    ),

    # ── 13. dhpg ──────────────────────────────────────────────────────────────
    CompanyConfig(
        rank=13, key="dhpg", name="dhpg",
        url="https://www.dhpg.de/de/newsroom",
        page_type="Newsroom",
        note="JS-gerendert — Newsroom-Inhalt lädt clientseitig; selectors noch zu tunen",
        selectors=None,
    ),

    # ── 14. DORNBACH ──────────────────────────────────────────────────────────
    CompanyConfig(
        rank=14, key="dornbach", name="DORNBACH",
        url="https://www.dornbach.de/de/downloads-dornbach-update.html",
        page_type="dedizierte Update-/Newsletter-Seite",
        note="PDF-Newsletter-Archiv — strukturell anders; selectors noch zu definieren",
        selectors=None,
    ),

    # ── 15. Freshfields ───────────────────────────────────────────────────────
    CompanyConfig(
        rank=15, key="freshfields", name="Freshfields",
        url="https://www.freshfields.com/de",
        page_type="News-/Insights-Einstieg",
        note=(
            "Anker zu /our-thinking/ enthalten Datum + Titel + Lead als Flow-Text — "
            "wir extrahieren das verschmolzen als Titel und filtern Doubletten per URL"
        ),
        selectors=SiteSelectors(
            item='a[href*="/our-thinking/"]',
            title=None,                  # Anker selbst, Titel = sichtbarer Text
        ),
    ),

    # ── 16. PKF Fasselt ───────────────────────────────────────────────────────
    CompanyConfig(
        rank=16, key="pkf_fasselt", name="PKF Fasselt",
        url="https://www.pkf-fasselt.de/themen-news/news-blogbeitraege",
        page_type="News-/Blog-Seite", note="offizielle News- & Blogbeiträge-Seite",
        selectors=SiteSelectors(
            item="div.news-list-item",
            title="h3",
            url="a.btn",
            date="time",
            max_items=80,                # Übersichtsseite zeigt sehr viele Karten
        ),
    ),

    # ── 17. PKF Wulf & Partner ────────────────────────────────────────────────
    CompanyConfig(
        rank=17, key="pkf_wulf", name="PKF Wulf & Partner",
        url="https://www.pkf-wulf-gruppe.de/",
        page_type="News-Einstieg auf Website",
        note="Startseite — Selektoren noch nicht hinterlegt",
        selectors=None,
    ),

    # ── 18. Clifford Chance ───────────────────────────────────────────────────
    CompanyConfig(
        rank=18, key="clifford_chance", name="Clifford Chance",
        url="https://jobs.cliffordchance.com/praxisgruppen-frankfurt",
        page_type="Tax-Praxis-Seite",
        note="URL zeigt auf Karriere-/Praxisseite, nicht auf Artikelliste — URL ändern",
        selectors=None,
    ),

    # ── 19. BANSBACH ──────────────────────────────────────────────────────────
    CompanyConfig(
        rank=19, key="bansbach", name="BANSBACH",
        url="https://www.bansbach-gruppe.de/",
        page_type="News-Einstieg auf Website",
        note="Startseite mit BANSBACH-Blog — wir greifen die Blog-Artikel auf der Startseite ab",
        selectors=SiteSelectors(
            item="div.blog-article__body",
            title="h2",
        ),
    ),

    # ── 20. ECOVIS KSO ────────────────────────────────────────────────────────
    CompanyConfig(
        rank=20, key="ecovis_kso", name="ECOVIS KSO",
        url="https://ecovis-kso.com/blog/",
        page_type="Blog / News-Seite",
        note="Blog-Rollover-Karten mit Titel + Link",
        selectors=SiteSelectors(
            item="div.fusion-rollover-content",
            title="h4.fusion-rollover-title",
            url="h4.fusion-rollover-title a",
        ),
    ),

    # ── 21. POELLATH ──────────────────────────────────────────────────────────
    CompanyConfig(
        rank=21, key="poellath", name="POELLATH",
        url="https://www.pplaw.com/",
        page_type="News-/Newsletter-Einstieg",
        note="Newstimeline auf der Homepage — gut strukturiert mit Datum + Titel",
        selectors=SiteSelectors(
            item="div.m-newstimeline-teaser",
            title="h4.m-newstimeline-teaser__title",
            url="div.m-newstimeline-teaser__link a",
            date="time",
            date_attr="datetime",
        ),
    ),

    # ── 22. Nexia ─────────────────────────────────────────────────────────────
    CompanyConfig(
        rank=22, key="nexia", name="Nexia",
        url="https://www.nexia.de/",
        page_type="News-/Insights-Einstieg",
        note="News-/Veranstaltungs-Karten auf der Startseite",
        selectors=SiteSelectors(
            item="div.background",
            title="div.header h3",
            summary='div[itemprop="description"]',
            date="p.calendar",
        ),
    ),

    # ── 23. Noerr ─────────────────────────────────────────────────────────────
    CompanyConfig(
        rank=23, key="noerr", name="Noerr",
        url="https://www.noerr.com/de/insights",
        page_type="Insights-/News-Seite",
        note="Wir greifen explizit Anker mit /de/insights/ im href — filtert Themen-Kacheln aus",
        selectors=SiteSelectors(
            item='a[href*="/de/insights/"]',
            title=None,                  # Anker-Text ist der Artikeltitel
        ),
    ),

    # ── 24. Linklaters ────────────────────────────────────────────────────────
    CompanyConfig(
        rank=24, key="linklaters", name="Linklaters",
        url="https://www.linklaters.com/de-de/locations/germany",
        page_type="Deutschland-Seite mit Tax-Bereich",
        note="Praxisgruppen-Seite ohne Artikelliste — URL ändern",
        selectors=None,
    ),

    # ── 25. LKC ───────────────────────────────────────────────────────────────
    CompanyConfig(
        rank=25, key="lkc", name="LKC Kemper Czarske v. Gronau Berz",
        url="https://lkc.de/news/",
        page_type="News-Seite", note="aktuelle News der gesamten LKC-Gruppe",
        selectors=SiteSelectors(
            item="div.news-flash-item",
            title="h5",
            # Das gesamte Item ist von einem Anker umschlossen — der Default-Fallback
            # ``erstes <a> im Item`` greift hier korrekt.
            summary="p",
        ),
    ),

    # ── 26. KMLZ ──────────────────────────────────────────────────────────────
    CompanyConfig(
        rank=26, key="kmlz", name="KMLZ",
        url="https://www.kmlz.de/de/news",
        page_type="dedizierte News-/Newsletter-Seite",
        note="fokussiert auf Umsatzsteuer, Zollrecht und indirekte Steuern",
        selectors=SiteSelectors(
            item="div.news-wrapper",
            title="div.news-vat-title",
            url="div.news-vat-title a",
            date="time",
            date_attr="datetime",
            summary="div.news-vat-body-inner",
        ),
    ),

    # ── 27. Dr. Kleeberg & Partner ────────────────────────────────────────────
    CompanyConfig(
        rank=27, key="kleeberg", name="Dr. Kleeberg & Partner",
        url="https://www.kleeberg.de/aktuell/news/",
        page_type="News-Seite", note="aktuelle Themen aus Tax, Audit, Advisory, Legal u.a.",
        selectors=SiteSelectors(
            item="div.swe-post-item",
            title="div.swe-post-title h3",
            url="a.custom-button.default",
            date="span.swe-post-date",
            summary="div.swe-post-text",
        ),
    ),

    # ── 28. SONNTAG & Partner ─────────────────────────────────────────────────
    CompanyConfig(
        rank=28, key="sonntag", name="SONNTAG & Partner",
        url="https://www.sonntag-partner.de/aktuelles/news/",
        page_type="News-Seite", note="enthält u.a. TAX TUESDAY und Sonderinformationen",
        selectors=SiteSelectors(
            item="h3.itemTitle",         # Titel-Heading dient hier direkt als Item
            title=None,
        ),
    ),

    # ── 29. MÖHRLE HAPP LUTHER ────────────────────────────────────────────────
    CompanyConfig(
        rank=29, key="mhl", name="MÖHRLE HAPP LUTHER",
        url="https://mhl.de/de/",
        page_type="News-Einstieg auf Website",
        note="Startseite — Selektoren noch nicht hinterlegt",
        selectors=None,
    ),

    # ── 30. RWT ───────────────────────────────────────────────────────────────
    CompanyConfig(
        rank=30, key="rwt", name="RWT",
        url="https://www.rwt-gruppe.de/news.html",
        page_type="News-Seite", note="News, Fachartikel und RWTkompakt-Ausgaben",
        selectors=SiteSelectors(
            item="div.news__link",
            title="span[itemprop='headline']",
            url="a[itemprop='url']",
        ),
    ),
]
