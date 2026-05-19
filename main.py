"""Orchestrator für das Monitoring deutscher Steuer-News-Seiten.

Ablauf:
  1. State laden (gesehene Artikel-URLs pro Unternehmen)
  2. Für jedes aktivierte Unternehmen mit Selektoren:
       Seite laden → Artikel per CSS-Selektoren extrahieren → Diff gegen State
  3. State aktualisieren und zurückschreiben
  4. Bei Treffern: ``LATEST_REPORT.md`` schreiben
  5. (Im GitHub-Actions-Workflow committed der Bot die Änderungen zurück)

Lokal:
  python main.py
  python main.py --only ey,kpmg        # nur ausgewählte Unternehmen
  python main.py --reset-state         # state.json vorher löschen
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from companies_config import COMPANIES, CompanyConfig
from tools.fetch_page import fetch
from tools.scrape_articles import Article, scrape_articles
from tools.write_report import write_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

STATE_FILE = Path(__file__).parent / "state.json"
STATE_VERSION = 2
MAX_SEEN_URLS = 500  # Pro Unternehmen — beschränkt state.json-Größe


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        with STATE_FILE.open(encoding="utf-8") as f:
            state = json.load(f)
        if state.get("version") == STATE_VERSION:
            return state
        logger.info("State version %s ≠ %s — starting fresh.", state.get("version"), STATE_VERSION)
    return {"version": STATE_VERSION, "last_run": None, "seen": {}}


def save_state(state: dict) -> None:
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")


def update_seen(seen: list[str], new_urls: list[str]) -> list[str]:
    combined = seen + [u for u in new_urls if u not in seen]
    if len(combined) > MAX_SEEN_URLS:
        combined = combined[-MAX_SEEN_URLS:]
    return combined


# ---------------------------------------------------------------------------
# Per-company processing
# ---------------------------------------------------------------------------

def process_company(company: CompanyConfig, state: dict) -> list[Article]:
    """Verarbeite ein Unternehmen. Gibt die als neu erkannten Artikel zurück."""
    logger.info("→ %s (%s)", company.name, company.url)
    result = fetch(company.url)
    articles = scrape_articles(
        html=result.html,
        base_url=result.final_url,
        selectors=company.selectors,  # garantiert nicht None (Aufrufer filtert)
    )
    if not articles:
        return []

    seen_urls: list[str] = state["seen"].get(company.key, [])
    seen_set = set(seen_urls)
    all_urls = [a.url for a in articles]

    is_first_run = company.key not in state["seen"]
    if is_first_run:
        # Erstlauf: nur Seeding, kein Reporting (vermeidet einen Riesen-Initialbericht).
        state["seen"][company.key] = update_seen([], all_urls)
        logger.info("   (Erstlauf — %d Artikel als gesehen markiert, kein Report)", len(all_urls))
        return []

    new_articles = [a for a in articles if a.url not in seen_set]
    state["seen"][company.key] = update_seen(seen_urls, all_urls)
    logger.info("   %d neu / %d gesamt", len(new_articles), len(articles))
    return new_articles


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Monitor company tax-news pages.")
    p.add_argument(
        "--only",
        help="Komma-separierte Liste von Unternehmens-Keys (siehe companies_config.py).",
    )
    p.add_argument(
        "--reset-state",
        action="store_true",
        help="state.json vor dem Lauf löschen (alle Unternehmen werden frisch geseedet).",
    )
    p.add_argument(
        "--snapshot",
        action="store_true",
        help=(
            "Einmal-Modus: schreibe LATEST_REPORT.md mit ALLEN aktuell gefundenen Artikeln, "
            "ohne state.json zu verändern. Nützlich, um nach dem Seed-Lauf einen Statusbericht zu erzeugen."
        ),
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    if args.reset_state and STATE_FILE.exists():
        STATE_FILE.unlink()
        logger.info("state.json gelöscht.")

    only_keys: set[str] | None = None
    if args.only:
        only_keys = {k.strip() for k in args.only.split(",") if k.strip()}

    logger.info("=== Tax-News Monitor startet%s ===", " (SNAPSHOT)" if args.snapshot else "")
    state = load_state()

    scope = [c for c in COMPANIES if c.enabled and (only_keys is None or c.key in only_keys)]
    runnable = [c for c in scope if c.selectors is not None]
    skipped = [c for c in scope if c.selectors is None]

    for c in skipped:
        logger.info("⊘ %s — keine Selektoren hinterlegt (TODO), übersprungen.", c.name)

    new_articles: dict[str, list[Article]] = {}
    for company in runnable:
        try:
            if args.snapshot:
                # Im Snapshot-Modus: alle aktuell sichtbaren Artikel sammeln,
                # state.json bleibt unangetastet.
                result = fetch(company.url)
                articles = scrape_articles(html=result.html, base_url=result.final_url, selectors=company.selectors)
                if articles:
                    new_articles[company.name] = articles
                logger.info("→ %s: %d Artikel im Snapshot", company.name, len(articles))
            else:
                found = process_company(company, state)
                if found:
                    new_articles[company.name] = found
        except Exception as e:
            logger.error("Fehler bei %s: %s", company.name, e)
            continue

    if not args.snapshot:
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        logger.info("state.json gespeichert (%d aktiv, %d ohne Selektoren).", len(runnable), len(skipped))
    else:
        logger.info("state.json bleibt im Snapshot-Modus unverändert.")

    if new_articles:
        total = sum(len(v) for v in new_articles.values())
        logger.info("Schreibe Report: %d Beiträge von %d Unternehmen", total, len(new_articles))
        write_report(new_articles, snapshot=args.snapshot)
    else:
        logger.info("Keine Beiträge gefunden — LATEST_REPORT.md bleibt unverändert.")

    logger.info("=== Tax-News Monitor fertig ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
