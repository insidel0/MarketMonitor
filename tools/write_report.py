"""Write the daily publication report to LATEST_REPORT.md.

Colleagues watch the GitHub repository and receive a commit notification
whenever this file is updated (i.e. when new publications are found).
"""
from datetime import datetime
from pathlib import Path

from tools.scrapers.base import Publication

REPORT_FILE = Path(__file__).parent.parent / "LATEST_REPORT.md"


def write_report(new_publications: dict[str, list[Publication]]) -> None:
    """Write new publications to LATEST_REPORT.md."""
    today = datetime.now().strftime("%d.%m.%Y")
    total = sum(len(v) for v in new_publications.values())

    lines = [
        f"# Neue Finanzgericht-Entscheidungen — {today}",
        "",
        f"**{total} neue Entscheidung{'en' if total != 1 else ''} "
        f"aus {len(new_publications)} Gericht{'en' if len(new_publications) != 1 else ''}**",
        "",
    ]

    for court_name, pubs in new_publications.items():
        lines.append(f"## {court_name} ({len(pubs)})")
        lines.append("")
        for pub in pubs:
            date_str = f"{pub.date} — " if pub.date else ""
            lines.append(f"- **{date_str}{pub.title}**  ")
            lines.append(f"  {pub.url}")
        lines.append("")

    lines += [
        "---",
        f"*Abruf: {datetime.now().strftime('%d.%m.%Y %H:%M')} UTC*",
    ]

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
