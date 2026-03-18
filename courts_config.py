"""Central registry of all German Finanzgerichte and their scraper configuration.

To add a new court:
  1. Import or define the appropriate scraper class.
  2. Add a CourtConfig entry to COURTS with enabled=True.
  3. For Playwright-based scrapers, pass the BrowserContext at runtime via main.py.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CourtConfig:
    key: str                # Unique key used in state.json
    name: str               # Display name used in email digest
    enabled: bool           # Set False for paywalled, blocked, or URL-unknown courts
    scraper_type: str       # "voris" | "juris" | "bayern" | "nrw" | "stub"
    config: dict[str, Any] = field(default_factory=dict)


COURTS: list[CourtConfig] = [
    CourtConfig(
        key="fg_bw",
        name="FG Baden-Württemberg",
        enabled=True,
        scraper_type="juris",
        config={
            "court_key": "fg_bw",
            "base_url": "https://www.landesrecht-bw.de/bsbw/search",
        },
    ),
    CourtConfig(
        key="fg_muenchen",
        name="FG München / FG Nürnberg (Bayern)",
        enabled=True,
        scraper_type="bayern",
        config={
            "court_key": "fg_muenchen",
        },
    ),
    CourtConfig(
        key="fg_berlin",
        name="FG Berlin-Brandenburg",
        enabled=True,
        scraper_type="juris",
        config={
            "court_key": "fg_berlin",
            "base_url": "https://gesetze.berlin.de/bsbe/search",
        },
    ),
    # FG Bremen: publications only via juris (kostenpflichtig) — skipped
    CourtConfig(
        key="fg_bremen",
        name="FG Bremen",
        enabled=False,
        scraper_type="stub",
        config={
            "court_key": "fg_bremen",
            "reason": "Veröffentlichung nur über juris (kostenpflichtig). Manuelle Prüfung erforderlich.",
        },
    ),
    CourtConfig(
        key="fg_hamburg",
        name="FG Hamburg",
        enabled=True,
        scraper_type="juris",
        config={
            "court_key": "fg_hamburg",
            "base_url": "https://www.landesrecht-hamburg.de/bsha/search",
        },
    ),
    CourtConfig(
        key="fg_hessen",
        name="FG Hessen",
        enabled=True,
        scraper_type="juris",
        config={
            "court_key": "fg_hessen",
            "base_url": "https://www.rv.hessenrecht.hessen.de/bshe/search",
        },
    ),
    CourtConfig(
        key="fg_mv",
        name="FG Mecklenburg-Vorpommern",
        enabled=True,
        scraper_type="juris",
        config={
            "court_key": "fg_mv",
            "base_url": "https://www.landesrecht-mv.de/bsmv/search",
        },
    ),
    CourtConfig(
        key="fg_niedersachsen",
        name="FG Niedersachsen",
        enabled=True,
        scraper_type="voris",
        config={
            "court_key": "fg_niedersachsen",
        },
    ),
    CourtConfig(
        key="fg_nrw",
        name="FG NRW (Köln / Düsseldorf / Münster)",
        enabled=True,
        scraper_type="nrw",
        config={
            "court_key": "fg_nrw",
        },
    ),
    CourtConfig(
        key="fg_rlp",
        name="FG Rheinland-Pfalz",
        enabled=True,
        scraper_type="juris",
        config={
            "court_key": "fg_rlp",
            "base_url": "https://www.landesrecht.rlp.de/bsrp/search",
        },
    ),
    CourtConfig(
        key="fg_saarland",
        name="FG Saarland",
        enabled=False,
        scraper_type="stub",
        config={
            "court_key": "fg_saarland",
            "reason": "Seite durch Cloudflare WAF geschützt — automatischer Zugriff nicht möglich. Manuelle Prüfung erforderlich.",
        },
    ),
    CourtConfig(
        key="fg_sachsen",
        name="FG Sachsen",
        enabled=False,
        scraper_type="stub",
        config={
            "court_key": "fg_sachsen",
            "reason": "Kein Finanzgericht im esamosplus-Portal auswählbar. Keine öffentliche Urteilsdatenbank gefunden.",
        },
    ),
    CourtConfig(
        key="fg_sachsen_anhalt",
        name="FG Sachsen-Anhalt",
        enabled=True,
        scraper_type="juris",
        config={
            "court_key": "fg_sachsen_anhalt",
            "base_url": "https://www.landesrecht.sachsen-anhalt.de/bsst/search",
        },
    ),
    CourtConfig(
        key="fg_schleswig_holstein",
        name="FG Schleswig-Holstein",
        enabled=True,
        scraper_type="juris",
        config={
            "court_key": "fg_schleswig_holstein",
            "base_url": "https://www.gesetze-rechtsprechung.sh.juris.de/bssh/search",
        },
    ),
    CourtConfig(
        key="fg_thueringen",
        name="FG Thüringen",
        enabled=True,
        scraper_type="juris",
        config={
            "court_key": "fg_thueringen",
            "base_url": "https://www.landesrecht.thueringen.de/bsth/search",
        },
    ),
]
