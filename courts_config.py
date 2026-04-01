"""Zentrales Register aller deutschen Finanzgerichte mit Scraper-Konfiguration.

Primärquelle: dejure.org (kostenlos, servergerendert, bereits nach Gericht gefiltert).
Sekundärquelle: Direkte Landesrechtsdatenbanken (Voris für Niedersachsen).

Scraper-Typen:
  "dejure"  – DejureScraper  (kein Playwright, schnell, empfohlen)
  "voris"   – VorisScraper   (kein Playwright, Niedersachsen spezifisch)
  "nrw"     – NRWScraper     (Playwright, NRW-Justizportal als Ergänzung)
  "stub"    – StubScraper    (deaktiviert, Paywall oder kein Zugriff)
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CourtConfig:
    key: str                # Eindeutiger Schlüssel in state.json
    name: str               # Anzeigename im Bericht
    enabled: bool
    scraper_type: str       # "dejure" | "voris" | "nrw" | "stub"
    config: dict[str, Any] = field(default_factory=dict)


COURTS: list[CourtConfig] = [

    # ── Baden-Württemberg ─────────────────────────────────────────────────────
    CourtConfig(
        key="fg_bw",
        name="FG Baden-Württemberg",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_bw",
            "gericht": "FG Baden-Württemberg",
        },
    ),

    # ── Bayern: München ───────────────────────────────────────────────────────
    CourtConfig(
        key="fg_muenchen",
        name="FG München",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_muenchen",
            "gericht": "FG München",
        },
    ),

    # ── Bayern: Nürnberg ──────────────────────────────────────────────────────
    CourtConfig(
        key="fg_nuernberg",
        name="FG Nürnberg",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_nuernberg",
            "gericht": "FG Nürnberg",
        },
    ),

    # ── Berlin-Brandenburg ────────────────────────────────────────────────────
    CourtConfig(
        key="fg_berlin_bb",
        name="FG Berlin-Brandenburg",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_berlin_bb",
            "gericht": "FG Berlin-Brandenburg",
        },
    ),

    # ── Brandenburg (historische Einträge auf dejure) ─────────────────────────
    CourtConfig(
        key="fg_brandenburg",
        name="FG Brandenburg",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_brandenburg",
            "gericht": "FG Brandenburg",
        },
    ),

    # ── Bremen ────────────────────────────────────────────────────────────────
    CourtConfig(
        key="fg_bremen",
        name="FG Bremen",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_bremen",
            "gericht": "FG Bremen",
        },
    ),

    # ── Düsseldorf ────────────────────────────────────────────────────────────
    CourtConfig(
        key="fg_duesseldorf",
        name="FG Düsseldorf",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_duesseldorf",
            "gericht": "FG Düsseldorf",
        },
    ),

    # ── Hamburg ───────────────────────────────────────────────────────────────
    CourtConfig(
        key="fg_hamburg",
        name="FG Hamburg",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_hamburg",
            "gericht": "FG Hamburg",
        },
    ),

    # ── Hessen ────────────────────────────────────────────────────────────────
    CourtConfig(
        key="fg_hessen",
        name="FG Hessen",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_hessen",
            "gericht": "FG Hessen",
        },
    ),

    # ── Köln ──────────────────────────────────────────────────────────────────
    CourtConfig(
        key="fg_koeln",
        name="FG Köln",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_koeln",
            "gericht": "FG Köln",
        },
    ),

    # ── Mecklenburg-Vorpommern ────────────────────────────────────────────────
    CourtConfig(
        key="fg_mv",
        name="FG Mecklenburg-Vorpommern",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_mv",
            "gericht": "FG Mecklenburg-Vorpommern",
        },
    ),

    # ── Münster ───────────────────────────────────────────────────────────────
    CourtConfig(
        key="fg_muenster",
        name="FG Münster",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_muenster",
            "gericht": "FG Münster",
        },
    ),

    # ── Niedersachsen ─────────────────────────────────────────────────────────
    # Voris: direkt FG-gefiltert, gut funktionierend
    CourtConfig(
        key="fg_niedersachsen",
        name="FG Niedersachsen",
        enabled=True,
        scraper_type="voris",
        config={
            "court_key": "fg_niedersachsen",
        },
    ),
    # dejure als zweite Quelle (anderer key → separater Eintrag im Bericht)
    CourtConfig(
        key="fg_niedersachsen_dejure",
        name="FG Niedersachsen (dejure)",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_niedersachsen_dejure",
            "gericht": "FG Niedersachsen",
        },
    ),

    # ── Rheinland-Pfalz ───────────────────────────────────────────────────────
    CourtConfig(
        key="fg_rlp",
        name="FG Rheinland-Pfalz",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_rlp",
            "gericht": "FG Rheinland-Pfalz",
        },
    ),

    # ── Saarland ──────────────────────────────────────────────────────────────
    CourtConfig(
        key="fg_saarland",
        name="FG Saarland",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_saarland",
            "gericht": "FG Saarland",
        },
    ),

    # ── Sachsen ───────────────────────────────────────────────────────────────
    CourtConfig(
        key="fg_sachsen",
        name="FG Sachsen",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_sachsen",
            "gericht": "FG Sachsen",
        },
    ),

    # ── Sachsen-Anhalt ────────────────────────────────────────────────────────
    CourtConfig(
        key="fg_sachsen_anhalt",
        name="FG Sachsen-Anhalt",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_sachsen_anhalt",
            "gericht": "FG Sachsen-Anhalt",
        },
    ),

    # ── Schleswig-Holstein ────────────────────────────────────────────────────
    CourtConfig(
        key="fg_schleswig_holstein",
        name="FG Schleswig-Holstein",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_schleswig_holstein",
            "gericht": "FG Schleswig-Holstein",
        },
    ),

    # ── Thüringen ─────────────────────────────────────────────────────────────
    CourtConfig(
        key="fg_thueringen",
        name="FG Thüringen",
        enabled=True,
        scraper_type="dejure",
        config={
            "court_key": "fg_thueringen",
            "gericht": "FG Thüringen",
        },
    ),
]
