# Workflow: Steuer-News von Beratungs- und Anwaltsgesellschaften überwachen

## Ziel
Wöchentlich die offiziellen News-/Blog-/Insights-Seiten der relevanten Beratungs-
und Kanzleimarken (JUVE Top30) auf neue Steuer-/Recht-/Wirtschafts-Beiträge prüfen
und einen markdown-Bericht ins Repository commiten.

## Eingaben (Inputs)
- `companies_config.py` — Liste der überwachten Unternehmen inkl. CSS-Selektoren
  pro Unternehmen (Quelle: `Steuernews_Links_02042026.xlsx`, Sheet *JUVE Top30 2025*)
- `state.json` — bereits gesehene Artikel-URLs pro Unternehmen

## Architektur (WAT)
- **Workflow:** dieses Dokument
- **Agent:** `main.py` orchestriert: State laden → Seite holen → Selektoren anwenden → Diff → State speichern → Report schreiben
- **Tools:**
  - `tools/fetch_page.py` — HTTP-Fetcher (requests + Retries, realistischer User-Agent)
  - `tools/scrape_articles.py` — generischer Selector-basierter Extractor (BeautifulSoup) inkl. Datumsnormalisierung
  - `tools/write_report.py` — schreibt `LATEST_REPORT.md`

## Ablauf
1. `main.py` lädt `state.json`
2. Für jedes aktivierte Unternehmen in `companies_config.py` **mit hinterlegten Selektoren**:
   - URL abrufen (`tools/fetch_page.py`)
   - Mit den CSS-Selektoren des Unternehmens Artikel extrahieren (`tools/scrape_articles.py`)
   - Neue URLs (nicht in `state.json`) als Treffer markieren
   - Alle gesehenen URLs in `state.json` aktualisieren
3. Unternehmen mit `selectors=None` werden mit Hinweis im Log übersprungen
4. `state.json` speichern
5. Wenn Treffer vorhanden: `LATEST_REPORT.md` schreiben
6. GitHub Actions committed `state.json` (immer) und `LATEST_REPORT.md` (bei Treffern)

## Seed-Lauf (Erstlauf pro Unternehmen)
Beim ersten Lauf eines Unternehmens wird *kein* Bericht erstellt — alle gefundenen
Artikel werden nur als „gesehen" markiert. So vermeiden wir einen riesigen
Initial-Report bei neu hinzugefügten Unternehmen.

## Aktueller Stand
**22 von 30 Unternehmen** haben Selektoren und liefern beim Smoke-Test echte
Artikel:

| # | Unternehmen | Treffer | Notiz |
|---|---|---:|---|
| 1 | EY | 3 | Datum + Summary |
| 2 | KPMG | 27 | Summary ✓ |
| 3 | PwC | 20 | Datum + Summary |
| 4 | Deloitte | 6 | nur Titel/URL |
| 6 | Flick Gocke Schaumburg | 4 | nur Titel/URL |
| 7 | Rödl & Partner | 30 | Datum ✓ |
| 8 | RSM Ebner Stolz | 3 | Titel via `data-event-label`-Attribut |
| 10 | Forvis Mazars | 13 | Summary ✓ |
| 11 | Grant Thornton | 8 | Datum (deutsch) wird normalisiert |
| 12 | Baker Tilly | 18 | nur Titel/URL |
| 15 | Freshfields | 6 | Titel = Anker-Text (enthält Datum + Lead) |
| 16 | PKF Fasselt | 80 | Datum ✓ |
| 19 | BANSBACH | 4 | Blog-Karten |
| 20 | ECOVIS KSO | 12 | nur Titel/URL |
| 21 | POELLATH | 20 | Datum ✓ |
| 22 | Nexia | 11 | Datum + Summary |
| 23 | Noerr | 15 | Anker-basierter Filter via `/de/insights/` |
| 25 | LKC | 10 | Summary ✓ |
| 26 | KMLZ | 3 | Datum + Summary |
| 27 | Dr. Kleeberg & Partner | 24 | Datum + Summary |
| 28 | SONNTAG & Partner | 10 | nur Titel/URL |
| 30 | RWT | 12 | nur Titel/URL |

### Noch ohne Selektoren (8 Unternehmen)
Sie werden im Lauf mit Log-Hinweis übersprungen.

| # | Unternehmen | Grund | Was zu tun ist |
|---|---|---|---|
| 5 | WTS | JS-gerendert (Tax Weekly lädt clientseitig) | Playwright-Variante oder andere URL |
| 9 | BDO | JS-gerendert (nur Skeleton-Platzhalter im HTML) | Playwright-Variante oder andere URL |
| 13 | dhpg | JS-gerenderter Newsroom | Playwright-Variante oder andere URL |
| 14 | DORNBACH | PDF-Newsletter-Archiv, keine Artikel-Karten | Andere Strategie nötig (Auflistung der jüngsten Editionen) |
| 17 | PKF Wulf & Partner | Quell-URL ist Homepage ohne News-Sektion | URL auf eine dedizierte News-Seite ändern |
| 18 | Clifford Chance | Quell-URL zeigt auf Karriere-/Praxisseite | URL auf eine echte News-/Insights-Seite ändern |
| 24 | Linklaters | Quell-URL ist Deutschland-Standortseite | URL auf eine echte News-/Insights-Seite ändern |
| 29 | MÖHRLE HAPP LUTHER | Homepage; News-Sektion ist serverseitig nur als Teaser sichtbar | URL z. B. auf eine dedizierte Presseseite ändern |

## Output
**`LATEST_REPORT.md`** — Beispiel:

```
# Neue Steuer-News — 25.05.2026

**4 neue Beiträge von 2 Unternehmen**

## KPMG (3)

- **Neuntes Gesetz zur Änderung des StBerG…**
  https://kpmg.com/de/de/themen/2026/01/reg-e-gewst-hebesatz.html
  > BR-Drs. 223/26

## EY (1)

- **2026-04-23 — Wichtige Steuertermine**
  https://www.ey.com/de_de/technical/steuernachrichten/wichtige-steuertermine13
  > Zum 31.05.2026 ist u. a. der Fristablauf …

---
*Abruf: 25.05.2026 07:02 UTC*
```

## Manuell ausführen (lokal)
```bash
pip install -r requirements.txt

# Alle aktiven Unternehmen:
python main.py

# Nur ausgewählte (zum Selektor-Testen):
python main.py --only ey,kpmg,deloitte

# State zurücksetzen (führt zu neuem Seed-Lauf für alle):
python main.py --reset-state
```

## In GitHub Actions auslösen
**Actions → "Monitor Tax News" → Run workflow → Branch `main` → Run workflow.**

Keine Secrets nötig.

## Neue Selektoren für ein Unternehmen hinterlegen

1. Lokal die Seite holen und HTML cachen:
   ```python
   from tools.fetch_page import fetch
   open('tmp/html/<key>.html','w').write(fetch('<url>').html)
   ```
2. Im Browser DevTools auf der Seite öffnen, eine Artikelkarte inspizieren.
   Notieren:
   - **Container** der einzelnen Karte (eindeutige Klasse, z. B. `div.news-item`)
   - **Titel** relativ zur Karte (z. B. `h3.title`)
   - **URL**, wenn das Titel-Element nicht direkt der Link ist (z. B. `a.read-more`)
   - **Datum** (falls vorhanden, z. B. `time[datetime]` oder `span.date`)
   - **Zusammenfassung** (falls vorhanden, z. B. `p.excerpt`)
3. In `companies_config.py` für das Unternehmen einen `SiteSelectors`-Eintrag
   anlegen.
4. Lokal testen:
   ```bash
   python main.py --only <key>
   ```
   Prüfen, dass im Log echte Artikeltitel/URLs/Daten erscheinen.

## Selektoren reparieren, wenn ein Unternehmen plötzlich 0 Treffer liefert

Wenn ein bisher funktionierender Lauf für ein Unternehmen 0 Artikel meldet:
1. Die Seite hat sich vermutlich umgestaltet.
2. Lokales HTML neu holen, DevTools öffnen, neue Klassen identifizieren.
3. Selektoren in `companies_config.py` aktualisieren.
4. `python main.py --only <key>` zum Verifizieren.

## Hinweis zur Datumsnormalisierung
`tools/scrape_articles.py` versucht Datumsangaben in das ISO-Format `YYYY-MM-DD`
zu normalisieren. Unterstützt:
- `YYYY-MM-DD` (auch mit Uhrzeit-Suffix)
- `12.05.2026`
- `5 März 2026`, `23 Apr. 2026` (lange & abgekürzte deutsche Monatsnamen)

Wenn eine Karte sein Datum in einer ungewöhnlichen Form ausgibt, kann pro
Unternehmen in `SiteSelectors.date_formats` ein zusätzliches Format ergänzt
werden.

## Zeitplan
GitHub Actions führt den Workflow montags 07:00 UTC aus (08:00 CET / 09:00 CEST).
