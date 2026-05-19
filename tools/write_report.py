"""Schreibt den Bericht über neue Steuer-News in ``LATEST_REPORT.md``.

Kollegen beobachten das GitHub-Repository und bekommen eine Commit-Benachrichtigung,
sobald diese Datei aktualisiert wird (d. h. wenn neue Artikel gefunden wurden).
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from tools.scrape_articles import Article

REPORT_FILE = Path(__file__).parent.parent / "LATEST_REPORT.md"


def write_report(new_articles: dict[str, list[Article]]) -> None:
    """Schreibe neue Artikel nach LATEST_REPORT.md, gruppiert nach Unternehmen."""
    today = datetime.now().strftime("%d.%m.%Y")
    total = sum(len(v) for v in new_articles.values())

    lines = [
        f"# Neue Steuer-News — {today}",
        "",
        f"**{total} neue{'r' if total == 1 else ''} Beitrag{'' if total == 1 else 'e'} "
        f"von {len(new_articles)} Unternehmen**",
        "",
    ]

    for company, articles in new_articles.items():
        lines.append(f"## {company} ({len(articles)})")
        lines.append("")
        for art in articles:
            date_part = f"{art.date} — " if art.date else ""
            lines.append(f"- **{date_part}{art.title}**")
            lines.append(f"  {art.url}")
            if art.summary:
                lines.append(f"  > {art.summary}")
        lines.append("")

    lines += [
        "---",
        f"*Abruf: {datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M')} UTC*",
        "",
    ]

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
